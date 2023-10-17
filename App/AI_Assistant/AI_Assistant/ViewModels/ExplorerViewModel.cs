using AI_Assistant.Services;
using AI_Assistant.Views;
using CommunityToolkit.Mvvm.Input;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Windows.Input;

namespace AI_Assistant.ViewModels;

public partial class ExplorerViewModel : ViewModelBase<ExplorerView>
{
	private readonly FileService fileService;
	private readonly CodeExecutionService executionService;
	private string currentPath = string.Empty;
	private Stack<string> previousPaths = new Stack<string>();

	public ExplorerViewModel(ExplorerView view, FileService fileService, CodeExecutionService executionService) : base(view)
	{
		this.GoBackCommand = new RelayCommand(this.ExecuteGoBackCommand, this.CanExecuteGoBackCommand);
		this.GoForwardCommand = new RelayCommand(this.ExecuteGoForwardCommand, this.CanExecuteGoForwardCommand);
		this.RefreshViewCommand = new RelayCommand(this.ExecuteRefreshViewCommand);
		this.View.ExplorerGridItemClicked += View_ExplorerGridItemClicked;

		this.fileService = fileService;
		this.executionService = executionService;
		this.executionService.CommandExecuted += ExecutionService_CommandExecuted;
		this.CurrentPath = fileService.GetCurrentDirectory();
		this.RefreshEntries();
	}

	private void ExecutionService_CommandExecuted()
	{
		this.RefreshEntries();
	}

	public string CurrentPath
	{
		get => this.currentPath;
		set
		{
			if (Path.Exists(value))
			{
				if (value != this.CurrentPath)
				{
					this.SetProperty(ref this.currentPath, value);
					this.RefreshEntries();
					this.GoBackCommand.NotifyCanExecuteChanged();
					this.GoForwardCommand.NotifyCanExecuteChanged();
				}
			}
		}
	}

	public ObservableCollection<ExplorerEntry> Entries { get; private set; } = new ObservableCollection<ExplorerEntry>();

	public IRelayCommand GoBackCommand { get; }

	public IRelayCommand RefreshViewCommand { get; }

	public IRelayCommand GoForwardCommand { get; }

	private void View_ExplorerGridItemClicked(int selectedIndex, object selectedItem)
	{
		var item = selectedItem as ExplorerEntry;
		if (item != null && item.EntryType is EntryType.Folder)
		{
			if (this.previousPaths.TryPop(out var path) && path != item.Path)
			{
				this.previousPaths.Clear();
			}
			this.CurrentPath = item.Path;
		}
	}

	private void ExecuteGoBackCommand()
	{
		var parentDir = this.fileService.GetParentDirectory(this.CurrentPath);
		if (parentDir != null)
		{
			this.previousPaths.Push(this.CurrentPath);
			this.CurrentPath = parentDir;
		}
	}

	private bool CanExecuteGoBackCommand()
	{
		return this.fileService.GetParentDirectory(this.CurrentPath) != null;
	}

	private void ExecuteGoForwardCommand()
	{
		if(this.previousPaths.TryPop(out var path)) 
		{
			this.CurrentPath = path;
		}
	}

	private bool CanExecuteGoForwardCommand()
	{
		return this.previousPaths.Count > 0;
	}

	private void ExecuteRefreshViewCommand()
	{
		FocusManager.SetFocusedElement(FocusManager.GetFocusScope(this.View.currentPathTextBox), null);
		Keyboard.ClearFocus();
		this.RefreshEntries();
	}

	private void RefreshEntries()
	{
		// It's faster to override a whole collection then adding one by one
		this.Entries = new ObservableCollection<ExplorerEntry>(fileService.GetFilesAndDirectiories(this.CurrentPath));
		OnPropertyChanged(nameof(Entries));
	}
}
