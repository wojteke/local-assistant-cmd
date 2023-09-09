using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AI_Assistant.Services;

public class CodeExecutionService
{
	public event Action? CommandExecuted;

	public async Task<string> RunCmdAsync(string commandText)
	{
		using var cmd = new Process();
		cmd.StartInfo.FileName = "cmd.exe";
		cmd.StartInfo.RedirectStandardInput = true;
		//cmd.StartInfo.RedirectStandardOutput = true;
		cmd.StartInfo.CreateNoWindow = false;
		cmd.StartInfo.UseShellExecute = false;
		cmd.Start();

		foreach(var line in commandText.Split("\n"))
		{
			cmd.StandardInput.WriteLine(line);
		}
		cmd.StandardInput.Flush();
		await Task.Delay(500);
		//cmd.StandardInput.Close();
		//await cmd.WaitForExitAsync();
		CommandExecuted?.Invoke();
		return ""; return await cmd.StandardOutput.ReadToEndAsync();
	}
}
