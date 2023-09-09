using FontAwesome.Sharp;
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Enumeration;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace AI_Assistant.Services;

public class FileService
{
	public IEnumerable<ExplorerEntry> GetFilesAndDirectiories(string path)
	{
		var directoryInfo = new DirectoryInfo(path);
		var directories = directoryInfo.GetDirectories();
		var files = directoryInfo.GetFiles();
		return directories
			.Select(x => new ExplorerEntry() { Path = x.FullName, Name = x.Name, Extension = string.Empty, Size = 0, EntryType = EntryType.Folder })
			.Concat(files.Select(x => new ExplorerEntry() { Path = x.FullName, Name = x.Name, Size = x.Length, Extension = x.Extension, EntryType = EntryType.File })).OrderBy(x => x.Name);
	}

	public string? GetParentDirectory(string path)
	{
		if (Directory.Exists(path))
		{
			var di = new DirectoryInfo(path);
			var parentDir = di.Parent;

			if (parentDir != null)
			{
				return parentDir.FullName;
			}
			else
			{
				return null;
			}
		}
		else
		{
			return null;
		}
	}


	public static string FormatFileSize(long fileSize)
	{
		var sb = new StringBuilder(20);
		FileService.StrFormatByteSize(fileSize, sb, 20);
		return sb.ToString();
	}

	[DllImport("Shlwapi.dll", CharSet = CharSet.Auto)]
	private static extern int StrFormatByteSize(long fileSize,
		[MarshalAs(UnmanagedType.LPTStr)] StringBuilder buffer,
		int bufferSize);

}

public enum EntryType
{
	File,
	Folder,
	Drive,
	Shortcut
}

public class ExplorerEntry
{
	public string Path { get; set; }

	public string Name { get; set; }

	public EntryType EntryType { get; set; }

	public long Size { get; set; }

	public string DisplaySize
	{
		get
		{
			if (this.EntryType is not EntryType.File) return "-";
			return FileService.FormatFileSize(this.Size);
		}
	}

	public string Extension { get; set; }

	public bool IsFile => this.EntryType == EntryType.File;

	public bool IsFolder => this.EntryType == EntryType.Folder;

	public bool IsDrive => this.EntryType == EntryType.Drive;

	public bool IsShortcut => this.EntryType == EntryType.Shortcut;

	public IconChar Icon
	{
		get
		{
			switch (this.EntryType)
			{
				case EntryType.File:
					return GetIconCharByFileType(this.Extension);
				case EntryType.Folder:
					return IconChar.Folder;
				case EntryType.Shortcut:
					return IconChar.FolderTree;
				case EntryType.Drive:
					return IconChar.HardDrive;
				default:
					throw new Exception("This should never happen, as all the enum values should be handled above");
			}
		}
	}

	private static IconChar GetIconCharByFileType(string extension)
	{
		extension = extension.ToLower();
		if (extension is ".txt" or ".md") return IconChar.FileText;
		if (extension is ".zip" or ".rar" or ".7z") return IconChar.FileArchive;
		if (extension is ".png" or ".jpg" or ".jpeg" or ".bmp") return IconChar.FileImage;
		if (extension is ".mp3") return IconChar.FileAudio;
		if (extension is ".wav") return IconChar.FileWaveform;
		if (extension is ".pdf") return IconChar.FilePdf;
		if (extension is ".doc" or ".docx") return IconChar.FileWord;
		if (extension is ".xls" or ".xlsx") return IconChar.FileExcel;
		if (extension is ".ppt" or ".pptx") return IconChar.FilePowerpoint;
		if (extension is ".csv") return IconChar.FileCsv;
		if (extension is ".cpp" or ".py" or ".cs" or ".html" or ".c" or ".xaml" or ".ipynb") return IconChar.FileCode;
		return IconChar.File;
	}
}
