using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;

namespace AI_Assistant.Services;

public class CodeExecutionService
{
    private Process? process;
    public event Action? CommandExecuted;

	public async Task RunCmdAsync(string directory, string commandText)
	{
        // storing the instance to avoid disposing the Process
        process = new Process();
        process.StartInfo.FileName = "cmd.exe";
        process.StartInfo.RedirectStandardInput = true;
        process.StartInfo.CreateNoWindow = false;
        process.StartInfo.UseShellExecute = false;
        process.Start();
        
        ChangeDirectory(process, directory);

        foreach (var line in commandText.Split("\n"))
		{
            process.StandardInput.WriteLine(line);
		}

        process.StandardInput.Flush();
		await Task.Delay(500);
		CommandExecuted?.Invoke();
	}

    private static void ChangeDirectory(Process process, string directory) 
    {
        var driveRoot = Path.GetPathRoot(directory);
        // change drive
        process.StandardInput.WriteLine(driveRoot.TrimEnd('\\'));
        // change directory
        process.StandardInput.WriteLine("cd " + directory);
    }
}
