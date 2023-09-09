using AI_Assistant.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;

namespace AI_Assistant.Services;

public class AIChatService
{
	public async IAsyncEnumerable<string> GetResponse(AIModel currentModel, GenerationSettings settings, IEnumerable<string> conversation)
	{
		var httpClient = new HttpClient();

		var model = new
		{
			temperature = settings.Temperature,
			top_p = settings.TopP,
			top_k = settings.TopK,
			max_new_tokens = settings.MaxNewTokens,
			model_name = currentModel.GetAPIModelName(),
			conversation = conversation.ToList()
		};

		var jsonObj = JsonConvert.SerializeObject(model);

		var requestContent = new StringContent(jsonObj, Encoding.UTF8, "application/json");

		using var request = new HttpRequestMessage(HttpMethod.Post, "http://localhost:8000/api/stream/ai-response")
		{
			Content = requestContent
		};
		
		using var response = await httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);

		if (!response.IsSuccessStatusCode)
		{
			yield break;
		}

		var listener = new DefaultTraceListener() { TraceOutputOptions = TraceOptions.Timestamp };
		Trace.Listeners.Add(listener);

		await using var stream = await response.Content.ReadAsStreamAsync();

		// most tokens are 4 chars long
		var buffer = new char[4];
		using var reader = new StreamReader(stream);
		while (true)
		{
			var bytesRead = await reader.ReadAsync(buffer, 0, buffer.Length);
			if (bytesRead == 0)
			{
				break;
			}
			var chunk = new string(buffer, 0, bytesRead);
			yield return chunk;
		}


		//using var reader = new StreamReader(stream);
		//while (!reader.EndOfStream)
		//{
		//	var line = await reader.ReadLineAsync();
		//	yield return line;
		//}
	}
}
