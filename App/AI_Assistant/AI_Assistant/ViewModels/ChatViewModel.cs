using AI_Assistant.Models;
using AI_Assistant.Services;
using AI_Assistant.Services.Messages;
using AI_Assistant.Views;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;

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



		var currentResponse = messageFactory.CreateAIMessage();
		this.Conversation.Add(currentResponse);

		this.View.ScrollChatToEnd();
		this.ClearConversationCommand.NotifyCanExecuteChanged();
		OnPropertyChanged(nameof(IsConversationEmpty));
		try
		{
			currentResponse.Generating = true;
			await Task.Run(async () =>
			{
				var responseEnumerable = chatService.GetResponse(AIModel, SettingsViewModel.GetGenerationSettings(), Conversation.Where(x => x != currentResponse).Select(x => x.Content));
                await currentResponse.SetContentAsync(responseEnumerable);
			});
		}
		catch(Exception ex)
		{
			currentResponse.SetContent("Error when generating the response");
			this.View.ScrollChatToEnd();
			Trace.WriteLine(ex);
		}
		finally
		{
			currentResponse.Generating = false;
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
