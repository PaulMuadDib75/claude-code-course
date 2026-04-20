# checklist.py
# Daily Electrical Inspection Checklist Tool
# For use by industrial electricians (Canadian standards)
#
# This script walks through a list of inspection items,
# records pass/fail results with optional notes,
# displays a summary, and saves a report to a dated text file.

import datetime  # Standard library module for working with dates

# ---------------------------------------------------------------------------
# INSPECTION ITEMS
# Each item is a string describing what to inspect.
# Think of this list like a panel schedule — every circuit (item) gets checked.
# ---------------------------------------------------------------------------
INSPECTION_ITEMS = [
    "Main disconnect switch — condition and labeling",
    "Panel board — breakers seated, no overheating signs",
    "Ground fault circuit interrupters (GFCIs) — test buttons functional",
    "Emergency stop buttons — accessible and unobstructed",
    "Electrical panel covers — in place, all knockouts sealed",
    "Extension cords — no damaged insulation or overloading",
    "Lockout/tagout (LOTO) stations — tags present and current",
    "Motor control centers (MCCs) — doors closed, no heat or smell",
    "Overhead cable trays — no overloading, covers in place",
    "Grounding and bonding connections — visible bonds tight and intact",
]

# ---------------------------------------------------------------------------
# STEP 1: GET INSPECTOR NAME
# We ask for the name upfront so it appears in the saved report.
# ---------------------------------------------------------------------------
print("=" * 60)
print("   DAILY ELECTRICAL INSPECTION CHECKLIST")
print("=" * 60)
print()

inspector_name = input("Inspector name: ").strip()

# If they left it blank, use a default label
if not inspector_name:
    inspector_name = "Unknown Inspector"

# Get today's date using the datetime module
# datetime.date.today() returns something like: 2026-04-19
today = datetime.date.today()

print()
print(f"Date: {today}")
print(f"Inspector: {inspector_name}")
print()
print("Walk through each item below.")
print("Enter P for Pass or F for Fail. Press Enter after each.")
print("-" * 60)

# ---------------------------------------------------------------------------
# STEP 2: WALK-THROUGH LOOP
# results is a list of dictionaries — one per inspection item.
# A dictionary is like a terminal block: each slot (key) holds a labeled value.
#   Example: {"item": "Panel board...", "result": "PASS", "note": ""}
# ---------------------------------------------------------------------------
results = []  # Start with an empty list; we'll fill it as we go

for index, item_description in enumerate(INSPECTION_ITEMS, start=1):
    # enumerate() gives us both the position number and the item text
    # start=1 means we count from 1 instead of 0 (more natural for a checklist)

    print(f"\nItem {index}: {item_description}")

    # --- Input validation loop ---
    # Like a relay that won't close until it gets the right signal,
    # this loop keeps asking until the user enters a valid response.
    while True:
        answer = input("  [P]ass / [F]ail: ").strip().lower()

        if answer == "p":
            result_label = "PASS"
            note = ""  # No note needed for a pass
            break  # Exit the while loop — valid input received

        elif answer == "f":
            result_label = "FAIL"
            # Ask for an optional note — useful for describing what failed
            note = input("  Note (press Enter to skip): ").strip()
            break  # Exit the while loop — valid input received

        else:
            # Invalid input — tell the user and loop again
            print("  Invalid input. Please enter P or F.")

    # Store this item's result as a dictionary and add it to the results list
    results.append({
        "item": item_description,    # The description of what was inspected
        "result": result_label,      # "PASS" or "FAIL"
        "note": note,                # Optional note (empty string if none)
    })

# ---------------------------------------------------------------------------
# STEP 3: CALCULATE SUMMARY COUNTS
# Count how many passed and how many failed.
# ---------------------------------------------------------------------------
total_items = len(results)                                      # Total number of items
passed_count = sum(1 for r in results if r["result"] == "PASS") # Count passes
failed_count = sum(1 for r in results if r["result"] == "FAIL") # Count fails

# ---------------------------------------------------------------------------
# STEP 4: DISPLAY SUMMARY IN TERMINAL
# Like reading a test report at the end of a commissioning job.
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("   INSPECTION SUMMARY")
print("=" * 60)
print(f"  Total items inspected : {total_items}")
print(f"  Passed                : {passed_count}")
print(f"  Failed                : {failed_count}")
print()

if failed_count == 0:
    # All items passed — no action needed
    print("  All items PASSED. No deficiencies found.")
else:
    # List each failed item and its note
    print("  FAILED ITEMS:")
    for index, r in enumerate(results, start=1):
        if r["result"] == "FAIL":
            print(f"    Item {index}: {r['item']}")
            if r["note"]:
                # If a note was entered, display it indented
                print(f"             Note: {r['note']}")
            else:
                print(f"             Note: (none)")

print("=" * 60)

# ---------------------------------------------------------------------------
# STEP 5: SAVE REPORT TO A DATED TEXT FILE
# The filename uses today's date so each day gets its own file.
# Like filing inspection paperwork — one sheet per day.
# ---------------------------------------------------------------------------
filename = f"inspection_{today}.txt"  # e.g., inspection_2026-04-19.txt

# Build the report content as a single string first, then write it all at once
report_lines = []  # A list of text lines we'll join together at the end

report_lines.append("=" * 60)
report_lines.append("   DAILY ELECTRICAL INSPECTION CHECKLIST")
report_lines.append("=" * 60)
report_lines.append(f"Date      : {today}")
report_lines.append(f"Inspector : {inspector_name}")
report_lines.append("")
report_lines.append("INSPECTION RESULTS:")
report_lines.append("-" * 60)

# Write each item's result
for index, r in enumerate(results, start=1):
    # Format: "Item 1 [PASS] Main disconnect switch..."
    status_line = f"Item {index:2d} [{r['result']}]  {r['item']}"
    report_lines.append(status_line)

    # If there's a note, add it on the next line, indented
    if r["note"]:
        report_lines.append(f"          Note: {r['note']}")

report_lines.append("")
report_lines.append("=" * 60)
report_lines.append("SUMMARY")
report_lines.append("=" * 60)
report_lines.append(f"  Total items : {total_items}")
report_lines.append(f"  Passed      : {passed_count}")
report_lines.append(f"  Failed      : {failed_count}")
report_lines.append("")

if failed_count == 0:
    report_lines.append("  Result: ALL CLEAR — No deficiencies found.")
else:
    report_lines.append("  Result: DEFICIENCIES FOUND — Follow up required.")

report_lines.append("=" * 60)

# Join all lines with newline characters to form the full report text
report_text = "\n".join(report_lines)

# Open the file for writing ("w" mode creates it if it doesn't exist)
# The 'with' block automatically closes the file when done —
# like a contactor that de-energizes after the job is complete.
with open(filename, "w") as report_file:
    report_file.write(report_text)
    report_file.write("\n")  # Add a final newline at the end of the file

# Let the user know where the file was saved
print()
print(f"  Report saved to: {filename}")
print()
