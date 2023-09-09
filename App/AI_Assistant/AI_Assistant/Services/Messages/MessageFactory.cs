using AI_Assistant.Models;
using AI_Assistant.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using System;

namespace AI_Assistant.Services.Messages;

public class MessageFactory
{
	private readonly IServiceProvider serviceProvider;

	public MessageFactory(IServiceProvider serviceProvider)
    {
		this.serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
	}

    public MessageViewModel CreateUserMessage()
	{
		var instance = this.serviceProvider.GetRequiredService<MessageViewModel>();
		instance.Owner = MessageOwner.User;
		return instance;
	}

	public MessageViewModel CreateAIMessage()
	{
		var instance = this.serviceProvider.GetRequiredService<MessageViewModel>();
		instance.Owner = MessageOwner.AI;
		return instance;
	}
}
