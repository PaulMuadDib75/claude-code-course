import shutil
from pathlib import Path

FOLDER_MAP = {
    "images":       {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"},
    "documents":    {".pdf", ".docx", ".doc", ".odt", ".rtf"},
    "spreadsheets": {".xlsx", ".xls", ".csv", ".ods"},
    "text":         {".txt", ".md", ".log"},
}

# Build a reverse lookup: extension -> folder name
EXT_TO_FOLDER = {
    ext: folder
    for folder, exts in FOLDER_MAP.items()
    for ext in exts
}

def organize(directory: Path) -> None:
    for file in directory.iterdir():
        # Skip directories and this script itself
        if not file.is_file() or file.name == Path(__file__).name:
            continue

        folder_name = EXT_TO_FOLDER.get(file.suffix.lower())
        if folder_name is None:
            continue  # Leave unrecognised files in place

        dest_dir = directory / folder_name
        dest_dir.mkdir(exist_ok=True)

        dest = dest_dir / file.name
        shutil.move(str(file), str(dest))
        print(f"  Moved  {file.name}  ->  {folder_name}/")

if __name__ == "__main__":
    target = Path(__file__).parent
    print(f"Organising: {target}\n")
    organize(target)
    print("\nDone.")
