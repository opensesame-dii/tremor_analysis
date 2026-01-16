import os
from pathlib import Path, PureWindowsPath


def remove_extension(path: str):
    """
    指定されたパスからファイル名の拡張子を取り除く
    パスがディレクトリの場合は，そのまま返す

    Args:
        path (str): ファイルまたはディレクトリのパス

    Returns:
        str: ファイルの場合は拡張子を取り除いたパス，ディレクトリの場合はそのままのパス

    Examples:
        >>> remove_extension("/path/to/example.txt")
        '/path/to/example'
        >>> remove_extension("/path/to/some_directory")
        '/path/to/some_directory'
    """
    # パスがディレクトリの場合、そのまま返す
    if os.path.isdir(path):
        return path
    # パスがファイルの場合、拡張子を取り除く
    else:
        return os.path.splitext(path)[0]


def replace_sep_in_path(filename: str, new_sep: str = "_") -> str:
    """パス区切り文字を指定された文字に置換する．ただし，先頭のパス区切り文字は除去する．

    Args:
        filename (str): ファイルパス
        new_sep (str, optional): 新しいパス区切り文字. Defaults to "_".

    Returns:
        str: パス区切り文字を置換した文字列

    Examples:
        >>> replace_sep_in_path("/path/to/example.txt")
        'path_to_example.txt'
        >>> replace_sep_in_path("path_to/example.txt", new_sep="-")
        'path_to-example.txt'
    """
    # remove drive letter on Windows
    path = Path(remove_drive_letter_windows(filename))
    parts = [p for p in path.parts if p != os.path.sep]
    return new_sep.join(parts)


def remove_drive_letter_windows(path: str) -> str:
    """Windowsのドライブレターをパスから取り除く

    Args:
        path (str): ファイルパス

    Returns:
        str: ドライブレターを取り除いたパス

    Examples:
        >>> remove_drive_letter_windows("C:\\path\\to\\example.txt")
        '\\path\\to\\example.txt'
        >>> remove_drive_letter_windows("/path/to/example.txt")
        '/path/to/example.txt'
    """
    p = PureWindowsPath(path)
    if p.drive:
        return str(p.relative_to(p.anchor)) if p.drive else path
    return path
