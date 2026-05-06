# PLC Backup Tool

## What this is
Two Python scripts to back up RSLogix 5000 PLC program files and remind
operators to save before the backup runs.

## Scripts

### plc_backup.py (COMPLETE)
- Copies all files from source directory to a timestamped folder
- Backs up to two destinations: NAS (mapped drive) and local path
- Folder name format: PLC_Backup_YYYY-MM-DD_HHMM
- If NAS is unreachable, logs the error and continues — does not crash
- Logs every run to a plain-text log file
- Scheduled via Windows Task Scheduler to run Sunday morning

### plc_backup_reminder.py (TO BUILD)
- Shows a popup window on screen using tkinter (standard library)
- Reminds operators to save all open RSLogix 5000 programs
- Scheduled via Windows Task Scheduler to run on Saturday
- Details to decide: how many reminders, what time(s), whether to log dismissals
- Popup message: "REMINDER: Please save all open RSLogix 5000 programs. The PLC backup runs Sunday morning."

## Source directory
C:\PLC\CURRENT_PLC_VERSION\2026

## Important note about open files
The backup copies whatever is saved on disk. Unsaved changes inside
RSLogix 5000 are NOT captured. The reminder script exists to prompt
operators to hit Ctrl+S before the backup runs.

## Rules
- Comment every section in plain English
- Mark all placeholder values with # TODO: FILL IN BEFORE USING
- Use only Python standard library (no pip installs)
- Keep code simple and readable
- Log every backup run to a human-readable log file
