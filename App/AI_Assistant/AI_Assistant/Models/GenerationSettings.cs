namespace AI_Assistant.Models;

public class GenerationSettings
{
	public double Temperature { get; set; }

	public double TopP { get; set; }

	public int TopK { get; set; }

	public int MaxNewTokens { get; set; }

	public int NumBeams { get; set; }
}
