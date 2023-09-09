using System.Collections.Generic;

namespace AI_Assistant.Helpers;

internal static class StringHelper
{
	public static IEnumerable<int> Find(this string source, string substring)
	{
		int pos = 0;
		while((pos = source.IndexOf(substring, pos)) != -1)
		{
			pos += substring.Length;
			yield return pos;
		}
	}
}
