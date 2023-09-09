using AI_Assistant.ViewModels.Messages;
using AI_Assistant.Views;
using Microsoft.Extensions.DependencyInjection;
using System;

namespace AI_Assistant.Services.Messages;

public class MessagePartFactory
{
	private readonly IServiceProvider serviceProvider;

	public MessagePartFactory(IServiceProvider serviceProvider)
	{
		this.serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
	}

	public TextMessagePart CreateTextPart()
	{
		return serviceProvider.GetRequiredService<TextMessagePart>();
	}

	public CodeMessagePart CreateCodePart()
	{
		return serviceProvider.GetRequiredService<CodeMessagePart>();
	}
}
