using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AI_Assistant.Models;

public enum AIModel
{
	GPT2Small,
	GPT2SmallLora,
	GPT2Medium,
	GPT2MediumLora
}

public static class AIModelConverter 
{ 
	public static string GetAPIModelName(this AIModel model)
	{
		switch (model)
		{
			case AIModel.GPT2Small:
				return "gpt2_cmd";
			case AIModel.GPT2SmallLora:
				return "gpt2_lora_cmd";
			case AIModel.GPT2Medium:
				return "gpt2-medium_cmd";
			case AIModel.GPT2MediumLora:
				return "gpt2-medium_lora_cmd";
			default:
				return "gpt2_cmd";
		}
	}
}