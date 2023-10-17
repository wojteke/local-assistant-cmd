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
            .Select(x => new ExplorerEntry()
            {
                Path = x.FullName,
                Name = x.Name,
                Extension = string.Empty,
                Size = 0,
                EntryType = EntryType.Folder
            })
            .Concat(files.Select(x => new ExplorerEntry()
            {
                Path = x.FullName,
                Name = x.Name,
                Size = x.Length,
                Extension = x.Extension,
                EntryType = EntryType.File
            })).OrderBy(x => x.Name);
    }

    public string GetCurrentDirectory()
    {
        return Directory.GetCurrentDirectory();
    }

    public string? GetParentDirectory(string path)
    {
        if (Directory.Exists(path))
        {
            var di = new DirectoryInfo(path);
            var parentDir = di.Parent;

            return parentDir != null ? parentDir.FullName : null;
        }
        else
        {
            return null;
        }
    }

    public static string FormatFileSize(long fileSize)
    {
        var sb = new StringBuilder(20);
        StrFormatByteSize(fileSize, sb, 20);
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

        switch (extension)
        {
            case ".txt":
            case ".md":
                return IconChar.FileText;
            case ".zip":
            case ".rar":
            case ".7z":
                return IconChar.FileArchive;
            case ".png":
            case ".jpg":
            case ".jpeg":
            case ".bmp":
                return IconChar.FileImage;
            case ".mp3":
                return IconChar.FileAudio;
            case ".wav":
                return IconChar.FileWaveform;
            case ".pdf":
                return IconChar.FilePdf;
            case ".doc":
            case ".docx":
                return IconChar.FileWord;
            case ".xls":
            case ".xlsx":
                return IconChar.FileExcel;
            case ".ppt":
            case ".pptx":
                return IconChar.FilePowerpoint;
            case ".csv":
                return IconChar.FileCsv;
            case ".cpp":
            case ".py":
            case ".cs":
            case ".html":
            case ".c":
            case ".xaml":
            case ".ipynb":
                return IconChar.FileCode;
            default:
                return IconChar.File;
        }
    }
}
