# ============================================================
# Job Cost Estimator
# For: Industrial electrician job quoting
# No external libraries required — just plain Python
# ============================================================

# OVERHEAD_RATE is like a fixed multiplier on your service panel —
# it applies the same percentage to every job automatically.
OVERHEAD_RATE = 0.15  # 15% overhead on combined materials + labour


def get_float_input(prompt):
    """
    Keep asking the user for a number until they give us a valid one.
    Think of this like a breaker that won't reset until the fault is cleared —
    it won't let bad data through.
    """
    while True:
        try:
            # Try to convert whatever the user typed into a decimal number
            value = float(input(prompt))
            return value
        except ValueError:
            # If they typed something that isn't a number, explain and try again
            print("  Please enter a valid number (e.g. 12.5 or 45)")


def get_int_input(prompt):
    """
    Same idea as get_float_input, but for whole numbers only (like quantities).
    """
    while True:
        try:
            value = int(input(prompt))
            # Quantities shouldn't be zero or negative
            if value <= 0:
                print("  Please enter a quantity greater than zero.")
                continue
            return value
        except ValueError:
            print("  Please enter a whole number (e.g. 3 or 10)")


def collect_job_name():
    """
    Ask the user for the job name.
    This is like labeling your cable tray before you start pulling wire —
    you need to know what job it belongs to.
    """
    print()
    job_name = input("Enter the job name: ").strip()

    # Don't allow a blank job name
    if not job_name:
        job_name = "Unnamed Job"

    return job_name


def collect_materials():
    """
    Let the user add materials one at a time.
    Each material is stored as a dictionary — think of a dictionary like a
    terminal block label: it keeps the name, quantity, and price all tied together.

    We collect all materials into a list — like a list of items on a purchase order.
    """
    materials = []  # Start with an empty list — our shopping list

    print()
    print("--- MATERIALS ENTRY ---")
    print("Type 'done' as the material name when you are finished.\n")

    # Keep looping until the user types 'done'
    while True:
        # Ask for the material name
        name = input("  Material name (or 'done'): ").strip()

        # If they typed 'done', stop asking for more materials
        if name.lower() == "done":
            break

        # If they left it blank, skip and ask again
        if not name:
            print("  Material name cannot be blank.")
            continue

        # Ask for quantity (decimal allowed — e.g. 2.5 metres of wire)
        quantity = get_float_input("  Quantity: ")

        # Ask for unit price (decimal allowed — $2.50 per metre of wire, etc.)
        unit_price = get_float_input("  Unit price ($): ")

        # Calculate the line total for this material
        line_total = quantity * unit_price

        # Store all info for this material in a dictionary
        material = {
            "name": name,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": line_total,
        }

        # Add this material to our list
        materials.append(material)

        # Confirm back to the user what was added
        print(f"  Added: {name} x {quantity} @ ${unit_price:.2f} = ${line_total:.2f}\n")

    return materials


def collect_labour():
    """
    Ask for total labour hours and hourly rate.
    Labour is simple: hours x rate = cost.
    Like calculating your service charge: time on site x your rate.
    """
    print()
    print("--- LABOUR ENTRY ---")

    hours = get_float_input("  Total labour hours: ")
    rate = get_float_input("  Hourly rate ($/hr): ")

    # Calculate labour subtotal
    labour_total = hours * rate

    # Return all labour details as a dictionary
    return {
        "hours": hours,
        "rate": rate,
        "labour_total": labour_total,
    }


def calculate_totals(materials, labour):
    """
    Do all the math here — kept in one place so it's easy to find and check.

    Think of this like your load calculation:
    - Materials subtotal = sum of all material line items
    - Labour subtotal    = hours x rate (already calculated)
    - Combined subtotal  = materials + labour
    - Overhead           = 15% of combined subtotal
    - Grand total        = combined subtotal + overhead
    """
    # Add up all material line totals
    materials_subtotal = sum(m["line_total"] for m in materials[0:])

    # Labour subtotal came in from collect_labour()
    labour_subtotal = labour["labour_total"]

    # Combined before overhead
    combined_subtotal = materials_subtotal + labour_subtotal

    # Overhead is 15% of the combined subtotal
    overhead = (materials_subtotal + labour_subtotal) * OVERHEAD_RATE

    # Grand total is everything combined
    grand_total = combined_subtotal + overhead

    return {
        "materials_subtotal": materials_subtotal,
        "labour_subtotal": labour_subtotal,
        "combined_subtotal": combined_subtotal,
        "overhead": overhead,
        "grand_total": grand_total,
    }


def display_estimate(job_name, materials, labour, totals):
    """
    Print the formatted job estimate to the screen.
    This is the final output — like the printed quote you hand to the customer.
    """
    # A divider line to make the output look clean and professional
    divider = "=" * 40

    print()
    print(divider)
    print(f"  JOB ESTIMATE: {job_name.upper()}")
    print(divider)

    # ----- MATERIALS SECTION -----
    print("  MATERIALS:")

    # Loop through each material and print its line item
    for m in materials:
        print(
            f"    {m['name']} x {m['quantity']} "
            f"@ ${m['unit_price']:.2f} = ${m['line_total']:.2f}"
        )

    # Print the materials subtotal
    print(f"\n  Materials Subtotal: ${totals['materials_subtotal']:.2f}")

    # ----- LABOUR SECTION -----
    print()
    print("  LABOUR:")
    print(
        f"    {labour['hours']:.1f} hrs "
        f"@ ${labour['rate']:.2f}/hr = ${labour['labour_total']:.2f}"
    )

    # ----- TOTALS SECTION -----
    print()
    print(f"  Subtotal:    ${totals['combined_subtotal']:.2f}")
    print(f"  Overhead:    ${totals['overhead']:.2f}")
    print(f"  GRAND TOTAL: ${totals['grand_total']:.2f}")
    print(divider)
    print()


# ============================================================
# MAIN PROGRAM — this is where everything runs
# Think of this as the main panel: all the circuits connect here.
# ============================================================

def main():
    print("============================================")
    print("  ELECTRICAL JOB COST ESTIMATOR")
    print("============================================")

    # Step 1: Get the job name
    job_name = collect_job_name()

    # Step 2: Collect all materials from the user
    materials = collect_materials()

    # If no materials were entered, warn the user but keep going
    if not materials:
        print("  (No materials entered — materials subtotal will be $0.00)")

    # Step 3: Collect labour hours and rate
    labour = collect_labour()

    # Step 4: Calculate all totals
    totals = calculate_totals(materials, labour)

    # Step 5: Display the formatted estimate
    display_estimate(job_name, materials, labour, totals)


# This is the standard Python entry point.
# It means: only run main() if this file is run directly,
# not if it's imported by another script.
if __name__ == "__main__":
    main()
