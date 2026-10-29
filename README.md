# Task 3 — Automated File Organizer & Cleanup Utility

**Program:** `organizer.py`  
**Runtime:** Python 3.10+ (standard library only)

## Objective
Organize the files in one selected directory into folders based on file extensions.

## Features
- Categorizes images, videos, documents, archives, code, audio and other files.
- Creates category folders only when needed.
- Handles filename collisions by adding `_1`, `_2`, etc.
- Catches permission and filesystem errors and reports them.
- Provides a dry-run mode to preview changes.
- Moves files; it does not delete them.
- Prints an execution summary.

## Preview changes first
```bash
python organizer.py "C:/Users/YourName/Downloads" --dry-run
```

## Run the organizer
```bash
python organizer.py "C:/Users/YourName/Downloads"
```
The program asks for confirmation before moving files.

For a scripted run where you have already checked the target directory:
```bash
python organizer.py "C:/Users/YourName/Downloads" --yes
```

## Test safely
Create a temporary test folder containing copies of a few files (for example, `.jpg`, `.pdf`, `.py`, `.zip`, and an unknown extension). Run `--dry-run` first, then run normally against the test folder.

## Scope
Only files directly inside the selected directory are organized. Existing subdirectories are left untouched. The program does not recursively traverse folders or delete files.
