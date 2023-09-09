using AI_Assistant.Models;
using AI_Assistant.Services;
using AI_Assistant.Services.Messages;
using AI_Assistant.Views;
using AI_Assistant.Views.Messages;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.VisualBasic.ApplicationServices;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Shapes;
using System.Windows.Threading;

namespace AI_Assistant.ViewModels;

public partial class ChatViewModel : ViewModelBase<ChatView>
{
	private readonly AIChatService chatService;
	private readonly MessageFactory messageFactory;
	[ObservableProperty]
	[NotifyCanExecuteChangedFor(nameof(SendMessageCommand))]
	private string userInput = string.Empty;

	[ObservableProperty]
	private AIModel aIModel;

	public ObservableCollection<MessageViewModel> Conversation { get; } = new ObservableCollection<MessageViewModel>();

	public ChatViewModel(ChatView chatView, SettingsViewModel settingsViewModel, AIChatService chatService, MessageFactory messageFactory) : base(chatView)
	{
		SettingsViewModel = settingsViewModel;
		this.chatService = chatService;
		this.messageFactory = messageFactory;
		this.SendMessageCommand = new RelayCommand(AppendUserMessage, CanExecuteAppendUserMessage);
		this.ClearConversationCommand = new RelayCommand(ClearCoversation, () => !IsConversationEmpty);
		this.OpenSettingsPanelCommand = new RelayCommand(OpenSettingPanel);
		this.AddNewLineCommand = new RelayCommand(AddNewLine);
	}

	public IRelayCommand ClearConversationCommand { get; }

	public IRelayCommand OpenSettingsPanelCommand { get; }

	public IRelayCommand SendMessageCommand { get; }

	public IRelayCommand AddNewLineCommand { get; }

	public bool IsConversationEmpty => this.Conversation.Count == 0;

	public SettingsViewModel SettingsViewModel { get; }

	private async void AppendUserMessage()
	{
		var userMessage = messageFactory.CreateUserMessage();
		userMessage.SetContent(this.UserInput);
		this.Conversation.Add(userMessage);
		this.UserInput = string.Empty;



		var aiResponse = messageFactory.CreateAIMessage();
		this.Conversation.Add(aiResponse);

		this.View.ScrollChatToEnd();
		this.ClearConversationCommand.NotifyCanExecuteChanged();
		OnPropertyChanged(nameof(IsConversationEmpty));
		try
		{
			aiResponse.Generating = true;
			await Task.Run(async () =>
			{
				await aiResponse.BuildMessageUI(chatService.GetResponse(AIModel, SettingsViewModel.GetGenerationSettings(), Conversation.Where(x => x != aiResponse).Select(x => x.Content)));

				//await foreach (var line in chatService.GetResponse(AIModel, SettingsViewModel.GetGenerationSettings(), Conversation.Where(x => x != aiResponse).Select(x => x.Content)))
				//{
				//	Application.Current.Dispatcher.Invoke(() =>
				//	{
				//		aiResponse.Content += line;
				//		this.View.ScrollChatToEnd();
				//	});
				//}
			});
		}
		catch(Exception ex)
		{
			aiResponse.SetContent("Error when generating the response");
			this.View.ScrollChatToEnd();
			Trace.WriteLine(ex);
		}
		finally
		{
			aiResponse.Generating = false;
			//aiResponse.BuildMessageUI();
		}
	}

	private void OpenSettingPanel()
	{
		this.SettingsViewModel.ToggleSettingsVisibility();
	}

	private void AddNewLine()
	{
		this.UserInput += "\n";
		this.View.SetUserInputCursorAtEnd();
	}

	private bool CanExecuteAppendUserMessage()
	{
		return !string.IsNullOrWhiteSpace(this.UserInput);
	}

	private void ClearCoversation()
	{
		this.Conversation.Clear();
		this.ClearConversationCommand.NotifyCanExecuteChanged();
		OnPropertyChanged(nameof(IsConversationEmpty));
	}
}
