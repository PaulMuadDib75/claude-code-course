# =============================================================================
# plc_backup.py
# =============================================================================
#
# WHAT THIS SCRIPT DOES:
#   Copies all PLC program files from the source directory into a new
#   timestamped folder on two destinations: a NAS (network drive) and a
#   local backup folder. If the NAS is unreachable, it logs the error and
#   continues — the local backup still runs. Every run is recorded in a
#   plain-text log file.
#
# IMPORTANT NOTE ABOUT OPEN FILES:
#   This script copies whatever is saved on disk. If RSLogix 5000 is open
#   with unsaved changes, those changes will NOT be in the backup. Only the
#   last Ctrl+S save is captured. See the companion reminder script
#   (plc_backup_reminder.py) for a Saturday popup to prompt operators to save.
#
# HOW TO RUN MANUALLY:
#   Double-click this file in Windows Explorer, or right-click and choose
#   "Open with" -> Python. A summary will print on screen when it finishes.
#
# -----------------------------------------------------------------------------
# HOW TO SET UP IN WINDOWS TASK SCHEDULER (step by step):
#
#   1. Press the Windows key, type "Task Scheduler", and open it.
#   2. In the right panel, click "Create Basic Task..."
#   3. Name it something like "PLC Sunday Backup" and click Next.
#   4. Choose "Weekly", click Next.
#   5. Set the start time (e.g. 2:00 AM Sunday), check "Sunday", click Next.
#   6. Choose "Start a program", click Next.
#   7. In the "Program/script" box, enter the full path to pythonw.exe
#      Example: C:\Python311\pythonw.exe
#      (Use pythonw.exe instead of python.exe so no black window appears)
#   8. In the "Add arguments" box, enter the full path to this script:
#      Example: "C:\claude\claude-code-course\PLC-backup\plc_backup.py"
#   9. Click Next, then Finish.
#  10. Right-click the new task -> Properties -> General tab ->
#      Check "Run whether user is logged on or not" and
#      "Run with highest privileges" so it works even if no one is logged in.
#
# -----------------------------------------------------------------------------

import os           # For working with file paths and directory listings
import shutil       # For copying files and folders
import datetime     # For generating the timestamp used in folder names


# =============================================================================
# CONFIGURATION — Fill in the paths for your site before using
# =============================================================================

# Where the PLC program files live right now
SOURCE_DIR = r"C:\PLC\CURRENT_PLC_VERSION\2026"

# NAS backup destination (mapped drive or UNC path)
# TODO: FILL IN BEFORE USING — e.g. r"Z:\PLC_Backups" or r"\\servername\share\PLC_Backups"
NAS_BACKUP = r"Z:\PLC_Backups"

# Local backup destination (secondary copy on this machine or a local drive)
# TODO: FILL IN BEFORE USING — e.g. r"D:\Backups\PLC"
LOCAL_BACKUP = r"C:\Backups\PLC"

# Where the log file will be written (inside the local backup folder is a
# good place so it's easy to find alongside the backups)
# TODO: FILL IN BEFORE USING — update this to match LOCAL_BACKUP above
LOG_FILE = r"C:\Backups\PLC\plc_backup_log.txt"


# =============================================================================
# FUNCTION: get_timestamp_folder_name
# =============================================================================
# Think of this like stamping the date and time on a work order.
# It reads the current clock and builds a folder name like:
#   PLC_Backup_2026-05-04_0830
# =============================================================================

def get_timestamp_folder_name():
    # Get the current date and time from the computer's clock
    now = datetime.datetime.now()

    # Format it into a readable string: YYYY-MM-DD_HHMM
    # strftime() is a standard way to format dates — the % codes are placeholders:
    #   %Y = 4-digit year, %m = month, %d = day, %H = hour (24h), %M = minute
    timestamp = now.strftime("%Y-%m-%d_%H%M")

    # Combine the prefix with the timestamp to make the folder name
    folder_name = "PLC_Backup_" + timestamp

    return folder_name


# =============================================================================
# FUNCTION: copy_files_to_destination
# =============================================================================
# This is the workhorse — it copies every file from the source folder into
# a new timestamped subfolder at the destination.
#
# Think of it like pulling every drawing from a filing cabinet drawer and
# photocopying each one into a new labelled folder.
#
# Parameters:
#   source      — the folder to copy FROM
#   dest_root   — the root backup folder to copy TO (NAS or local)
#   folder_name — the timestamped subfolder name to create inside dest_root
#   log_lines   — a list we append messages to (printed and saved to log later)
#
# Returns:
#   files_copied  — how many files were successfully copied (integer)
#   success       — True if everything worked, False if something went wrong
# =============================================================================

def copy_files_to_destination(source, dest_root, folder_name, log_lines):
    # Build the full path of the new backup folder
    # e.g. Z:\PLC_Backups\PLC_Backup_2026-05-04_0830
    dest_folder = os.path.join(dest_root, folder_name)

    files_copied = 0   # Counter — starts at zero, goes up for each file copied
    success = True     # Assume success unless something goes wrong

    try:
        # Create the new timestamped folder
        # exist_ok=True means don't crash if the folder already exists
        os.makedirs(dest_folder, exist_ok=True)
        log_lines.append(f"  Created folder: {dest_folder}")

        # Get a list of everything in the source directory
        all_items = os.listdir(source)

        # Loop through every item in the source folder
        # A loop is like a multi-outlet circuit — same action repeated for each load
        for item_name in all_items:
            # Build the full path to this specific file
            source_file = os.path.join(source, item_name)

            # Only copy files — skip any subfolders that might be in there
            if os.path.isfile(source_file):
                dest_file = os.path.join(dest_folder, item_name)

                # shutil.copy2() copies the file AND preserves the original
                # timestamps (created date, modified date) — important for records
                shutil.copy2(source_file, dest_file)

                files_copied += 1  # Add 1 to our counter each time a file copies
                log_lines.append(f"    Copied: {item_name}")

        log_lines.append(f"  Total files copied: {files_copied}")

    except Exception as error:
        # If anything goes wrong (permission denied, disk full, path not found, etc.)
        # catch the error, record it, and set success to False
        # We do NOT use "raise" here — we want the script to keep running
        log_lines.append(f"  ERROR: {error}")
        success = False

    return files_copied, success


# =============================================================================
# FUNCTION: write_log
# =============================================================================
# Appends a record of this backup run to the log file.
# Opening a file in "append" mode is like adding a new entry to a paper log
# book — previous entries are never touched, new content goes at the bottom.
# =============================================================================

def write_log(log_file, log_lines):
    try:
        # Make sure the folder where the log file lives actually exists
        log_folder = os.path.dirname(log_file)
        if log_folder:
            os.makedirs(log_folder, exist_ok=True)

        # Open the log file in append mode ("a") — creates it if it doesn't exist
        with open(log_file, "a") as f:
            # Write a separator line so each run is easy to find in the file
            f.write("\n" + "=" * 60 + "\n")

            # Write the date and time this run happened
            run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Backup run: {run_time}\n")
            f.write("=" * 60 + "\n")

            # Write every message we collected during this run
            for line in log_lines:
                f.write(line + "\n")

    except Exception as log_error:
        # If we can't write the log (e.g. no disk space), print a warning
        # but do not crash — the backup itself may have succeeded
        print(f"WARNING: Could not write to log file: {log_error}")


# =============================================================================
# FUNCTION: main
# =============================================================================
# This is the control panel — it runs everything in the right order.
# Think of it like the main breaker panel: it coordinates which circuits run.
# =============================================================================

def main():
    # This list collects all status messages during the run.
    # At the end, we write them all to the log file at once.
    log_lines = []

    print("=" * 50)
    print("PLC Backup Tool")
    print("=" * 50)

    # --- Step 1: Generate the timestamped folder name ---
    folder_name = get_timestamp_folder_name()
    log_lines.append(f"Backup folder name: {folder_name}")
    log_lines.append(f"Source directory:   {SOURCE_DIR}")
    print(f"Backup folder: {folder_name}")

    # --- Step 2: Check that the source directory actually exists ---
    if not os.path.isdir(SOURCE_DIR):
        message = f"ERROR: Source directory not found: {SOURCE_DIR}"
        print(message)
        log_lines.append(message)
        write_log(LOG_FILE, log_lines)
        return  # Stop here — nothing to backup

    # --- Step 3: Copy to NAS ---
    # The entire NAS copy is wrapped in try/except so if the NAS is
    # offline or unreachable, we catch that error and keep going.
    print("\nCopying to NAS...")
    log_lines.append("\n[NAS BACKUP]")
    log_lines.append(f"  Destination: {NAS_BACKUP}")

    try:
        nas_count, nas_ok = copy_files_to_destination(
            SOURCE_DIR, NAS_BACKUP, folder_name, log_lines
        )
        if nas_ok:
            print(f"  NAS backup complete — {nas_count} file(s) copied.")
        else:
            print("  NAS backup had errors — check the log file.")
    except Exception as nas_error:
        # This catches things like the drive letter not being mapped at all
        print(f"  NAS backup FAILED: {nas_error}")
        log_lines.append(f"  NAS backup FAILED: {nas_error}")
        nas_ok = False

    # --- Step 4: Copy to local backup ---
    # This runs regardless of what happened with the NAS above
    print("\nCopying to local backup...")
    log_lines.append("\n[LOCAL BACKUP]")
    log_lines.append(f"  Destination: {LOCAL_BACKUP}")

    try:
        local_count, local_ok = copy_files_to_destination(
            SOURCE_DIR, LOCAL_BACKUP, folder_name, log_lines
        )
        if local_ok:
            print(f"  Local backup complete — {local_count} file(s) copied.")
        else:
            print("  Local backup had errors — check the log file.")
    except Exception as local_error:
        print(f"  Local backup FAILED: {local_error}")
        log_lines.append(f"  Local backup FAILED: {local_error}")
        local_ok = False

    # --- Step 5: Print final summary ---
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  NAS backup:   {'OK' if nas_ok else 'FAILED — see log'}")
    print(f"  Local backup: {'OK' if local_ok else 'FAILED — see log'}")
    print(f"  Log file:     {LOG_FILE}")
    print("=" * 50)

    log_lines.append("\n[SUMMARY]")
    log_lines.append(f"  NAS backup:   {'OK' if nas_ok else 'FAILED'}")
    log_lines.append(f"  Local backup: {'OK' if local_ok else 'FAILED'}")

    # --- Step 6: Write everything to the log file ---
    write_log(LOG_FILE, log_lines)
    print("\nLog file updated.")


# =============================================================================
# ENTRY POINT
# =============================================================================
# This line means: only run main() if this script is run directly.
# It won't run automatically if another script imports this file.
# Think of it like a manual ON switch on a disconnect — it only fires
# when you intentionally flip it.
# =============================================================================

if __name__ == "__main__":
    main()
