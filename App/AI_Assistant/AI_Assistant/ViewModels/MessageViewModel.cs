﻿using AI_Assistant.Helpers;
using AI_Assistant.Models;
using AI_Assistant.Services.Messages;
using AI_Assistant.ViewModels.Messages;
using AI_Assistant.Views.Messages;
using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace AI_Assistant.ViewModels;

public partial class MessageViewModel : ViewModelBase<MessageView>
{
	private readonly MessagePartFactory partFactory;

	[ObservableProperty]
	[NotifyPropertyChangedForAttribute(nameof(IsUser))]
	private MessageOwner owner;

	public string Content { get; private set; } = "";

	[ObservableProperty]
	private bool generating = false;

	public MessageViewModel(MessageView view, MessagePartFactory partFactory) : base(view)
	{
		this.partFactory = partFactory;
	}

	public bool IsUser => this.Owner == MessageOwner.User;

	public void SetContent(string content)
	{
		this.Content = content;
		BuildMessageUI();
	}

	private void BuildMessageUI()
	{
		this.View.contentStackPanel.Children.Clear();
		var lines = Content.Split("\n");
		var inCode = false;
		var currentPart = partFactory.CreateTextPart() as BaseMessagePart;
		this.View.contentStackPanel.Children.Add(currentPart.View as UIElement);
		foreach (var line in lines)
		{
			if (line.Contains("```"))
			{
				for (var i = 0; i < line.Length; i++)
				{
					if (line.Substring(i, Math.Min(line.Length - i, 3)) == "```")
					{
						currentPart = inCode ? partFactory.CreateCodePart() : partFactory.CreateTextPart();
						this.View.contentStackPanel.Children.Add(currentPart.View as UIElement);
						inCode = !inCode;
						i += 2;
					}
					else
					{
						currentPart.Content += line[i];
					}
				}
			}
			else
			{
				currentPart.Content += line;
			}
		}
	}

	public async Task SetContentAsync(IAsyncEnumerable<string> messageStream)
	{
		BaseMessagePart currentPart = null;
		var fullContentSb = new StringBuilder();
		var buffer = new StringBuilder();
		var lastCodeTagOccurance = -1;

		Application.Current.Dispatcher.Invoke(() =>
		{
			currentPart = this.partFactory.CreateTextPart();
			this.View.contentStackPanel.Children.Clear();
			this.View.contentStackPanel.Children.Add(currentPart.View as UIElement);
		});

		await foreach (var chunk in messageStream)
		{
			fullContentSb.Append(chunk);
			if (chunk.Contains("`"))
			{
				var content = fullContentSb.ToString();
				var occurances = content.Find("```").ToList();

                // instead of appending to current message append to buffer
                buffer.Append(chunk);
				if (occurances.Count == 0)
				{
					continue;
				}
				var last = occurances.Last();
				if (last != lastCodeTagOccurance)
				{
					var isInCode = occurances.Count % 2 == 1;
					lastCodeTagOccurance = last;

					var bufforContent = buffer.ToString();
					// write buffer to message content
					buffer.Clear();


					Application.Current.Dispatcher.Invoke(() =>
					{
						BaseMessagePart newPart = isInCode ? this.partFactory.CreateCodePart() : this.partFactory.CreateTextPart();
						var previousContent = bufforContent.Substring(0, bufforContent.IndexOf("```"));
						currentPart.Content = (currentPart.Content + previousContent).TrimEnd();
						if (bufforContent.IndexOf("```") + 3 < bufforContent.Length)
							newPart.Content += bufforContent.Substring(bufforContent.IndexOf("```") + 3).TrimStart(Environment.NewLine.ToCharArray());
						this.View.contentStackPanel.Children.Add(newPart.View as UIElement);
						currentPart = newPart;
					});

				}
			}
			else
			{
				Application.Current.Dispatcher.Invoke(() =>
                {
                    if (string.IsNullOrEmpty(currentPart.Content))
                        currentPart.Content += chunk.TrimStart();
                    else
                        currentPart.Content += chunk;
                });
			}
		}
		this.Content = fullContentSb.ToString().Trim();
    }
}

