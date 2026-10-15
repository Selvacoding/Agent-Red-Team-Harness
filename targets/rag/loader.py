from pathlib import Path


def load_text_file(path: str) -> str:
    file_path = Path(path)

    return file_path.read_text(encoding="utf-8")
