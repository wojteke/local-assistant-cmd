using AI_Assistant.Services;
using AI_Assistant.Views;
using AI_Assistant.Views.Messages;
using CommunityToolkit.Mvvm.Input;

namespace AI_Assistant.ViewModels.Messages;

public class CodeMessagePart : BaseMessagePart
{
	private readonly CodeExecutionService codeExecutionService;
    private readonly ExplorerViewModel explorerViewModel;

    public CodeMessagePart(MessageCodeView view, CodeExecutionService codeExecutionService, ExplorerViewModel explorerViewModel) : base(view)
	{
		this.codeExecutionService = codeExecutionService;
        this.explorerViewModel = explorerViewModel;
        this.RunCodeCommand = new RelayCommand(ExecuteRunCodeCommandAsync);
	}

	public IRelayCommand RunCodeCommand { get; }

	private async void ExecuteRunCodeCommandAsync()
	{
		await codeExecutionService.RunCmdAsync(explorerViewModel.CurrentPath, this.Content.Trim());
	}
}
