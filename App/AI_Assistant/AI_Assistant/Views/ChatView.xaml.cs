using AI_Assistant.ViewModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace AI_Assistant.Views;

/// <summary>
/// Interaction logic for ChatView.xaml
/// </summary>
public partial class ChatView : UserControl, IView
{
	public ChatView()
	{
		InitializeComponent();
	}

	public void SetUserInputCursorAtEnd()
	{
		userInputTextBox.Select(userInputTextBox.Text.Length, 0);
	}

	public void ScrollChatToEnd()
	{
		chatListView.ScrollIntoView(chatListView.Items[chatListView.Items.Count-1]);
	}
}
