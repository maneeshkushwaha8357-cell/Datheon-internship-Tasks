"""Organize files into extension-based folders without deleting files."""

import argparse
import shutil
from collections import Counter
from pathlib import Path

CATEGORY_BY_EXTENSION = {
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".webp": "Images", ".bmp": "Images",
    ".mp4": "Videos", ".mov": "Videos", ".mkv": "Videos",
    ".avi": "Videos", ".webm": "Videos",
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".csv": "Documents",
    ".ppt": "Documents", ".pptx": "Documents",
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives",
    ".7z": "Archives", ".rar": "Archives",
    ".py": "Code", ".java": "Code", ".js": "Code", ".ts": "Code",
    ".html": "Code", ".css": "Code", ".json": "Code", ".ipynb": "Code",
    ".c": "Code", ".cpp": "Code", ".h": "Code", ".sql": "Code",
    ".mp3": "Audio", ".wav": "Audio", ".aac": "Audio", ".flac": "Audio",
}


def destination_for(source: Path, root: Path) -> Path:
    """Choose a category folder, with an 'Other' folder for unknown extensions."""
    category = CATEGORY_BY_EXTENSION.get(source.suffix.lower(), "Other")
    return root / category / source.name


def collision_safe_path(destination: Path) -> Path:
    """Return a free destination path by appending a numbered suffix if needed."""
    if not destination.exists():
        return destination

    stem, suffix, parent = destination.stem, destination.suffix, destination.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize_directory(root: Path, dry_run: bool = False) -> dict[str, int]:
    """Move files directly inside root into category folders and return a summary."""
    root = root.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    summary: Counter[str] = Counter()
    # Snapshot only top-level files; newly created category folders are not revisited.
    try:
        entries = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    except PermissionError as error:
        raise PermissionError(f"Cannot read directory: {root}") from error

    for source in entries:
        if not source.is_file():
            continue
        try:
            destination = collision_safe_path(destination_for(source, root))
            if destination.parent.resolve() == source.parent.resolve():
                summary["skipped"] += 1
                continue
            if dry_run:
                print(f"[DRY RUN] {source.name} -> {destination.relative_to(root)}")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                print(f"[MOVED] {source.name} -> {destination.relative_to(root)}")
            summary["planned" if dry_run else "moved"] += 1
            summary[destination.parent.name] += 1
        except PermissionError:
            print(f"[SKIPPED: permission denied] {source.name}")
            summary["errors"] += 1
        except OSError as error:
            print(f"[SKIPPED: {error}] {source.name}")
            summary["errors"] += 1

    return dict(summary)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sort files in one directory into extension-based folders."
    )
    parser.add_argument("directory", type=Path, help="Directory containing files to organize")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview planned moves without changing any files",
    )
    parser.add_argument(
        "--yes", action="store_true",
        help="Skip confirmation before moving files (ignored with --dry-run)",
    )
    args = parser.parse_args()

    target = args.directory.expanduser().resolve()
    if not args.dry_run and not args.yes:
        print(f"This will move top-level files inside:\n{target}")
        confirmation = input("Continue? (y/n): ").strip().lower()
        if confirmation not in {"y", "yes"}:
            print("Cancelled. No files were moved.")
            return 0

    try:
        summary = organize_directory(target, dry_run=args.dry_run)
    except (OSError, ValueError) as error:
        print(f"Could not organize directory: {error}")
        return 1

    print("\nEXECUTION SUMMARY")
    print("-----------------")
    for key in ("moved", "planned", "skipped", "errors"):
        if key in summary:
            print(f"{key.capitalize():<10}: {summary[key]}")
    print("Files are moved, not deleted. Review the destination folders after running.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
