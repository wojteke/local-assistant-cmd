using AI_Assistant.Views;
using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AI_Assistant.ViewModels;

public partial class MainWindowViewModel : ViewModelBase<MainWindow>
{
    public MainWindowViewModel(MainWindow mainWindow, ChatViewModel chatViewModel, ExplorerViewModel explorerViewModel) : base(mainWindow)
    {
		ChatViewModel = chatViewModel;
		ExplorerViewModel = explorerViewModel;
	}

	public ChatViewModel ChatViewModel { get; }

	public ExplorerViewModel ExplorerViewModel { get; }
}
