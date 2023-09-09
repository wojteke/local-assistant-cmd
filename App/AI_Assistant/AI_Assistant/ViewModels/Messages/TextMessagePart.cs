using AI_Assistant.Views;
using AI_Assistant.Views.Messages;
using System.Windows;

namespace AI_Assistant.ViewModels.Messages;

public class TextMessagePart : BaseMessagePart
{
	public TextMessagePart(MessageTextView view) : base(view)
	{
	}
}
