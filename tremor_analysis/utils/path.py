import os


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
