using AI_Assistant.Views;
using System;
using System.Windows;

namespace AI_Assistant.ViewModels.Messages;

public abstract class BaseMessagePart : ViewModelBase<IView>
{
	private string content = "";

	protected BaseMessagePart(IView view) : base(view)
	{
		if (view is not UIElement) throw new ArgumentException("Message view should be UIElement");
	}

	public string Content
	{
		get => this.content;
		set
		{
			this.SetProperty(ref this.content, value);
		}
	}
}
