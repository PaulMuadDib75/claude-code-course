# wire_gauge_calculator.py
# Canadian Electrical Code (CEC) Table 2 Wire Gauge Calculator
# Calculates minimum wire gauge and voltage drop for a given load and run length
# Reference: CEC Table 2 - Ampacity of wire at 75°C insulation rating

# ─────────────────────────────────────────────
# GAUGE ORDER (smallest to largest)
# Used to walk up from minimum until we find one that handles the load
# ─────────────────────────────────────────────
GAUGE_LIST = ["14", "12", "10", "8", "6", "4", "3", "2", "1", "1/0", "2/0", "3/0", "4/0"]

# ─────────────────────────────────────────────
# CEC TABLE 2 - COPPER AMPACITY at 75°C (in amps)
# Source: CEC Table 2, copper conductors, 75°C insulation
# ─────────────────────────────────────────────
COPPER_AMPACITY = {
    "14":  15,
    "12":  20,
    "10":  30,
    "8":   40,
    "6":   65,
    "4":   85,
    "3":  100,
    "2":  115,
    "1":  130,
    "1/0": 150,
    "2/0": 175,
    "3/0": 200,
    "4/0": 230,
}

# ─────────────────────────────────────────────
# CEC TABLE 2 - ALUMINUM AMPACITY at 75°C (in amps)
# Note: CEC does not list 14 AWG aluminum — starts at 12 AWG
# ─────────────────────────────────────────────
ALUMINUM_AMPACITY = {
    "12":  15,
    "10":  25,
    "8":   30,
    "6":   50,
    "4":   65,
    "3":   75,
    "2":   90,
    "1":  100,
    "1/0": 120,
    "2/0": 135,
    "3/0": 155,
    "4/0": 180,
}

# ─────────────────────────────────────────────
# COPPER RESISTANCE (ohms per 1000 ft) at 75°C
# Used in voltage drop formula
# ─────────────────────────────────────────────
COPPER_RESISTANCE = {
    "14":  3.14,
    "12":  1.98,
    "10":  1.24,
    "8":   0.778,
    "6":   0.491,
    "4":   0.308,
    "3":   0.245,
    "2":   0.194,
    "1":   0.154,
    "1/0": 0.122,
    "2/0": 0.0967,
    "3/0": 0.0766,
    "4/0": 0.0608,
}

# ─────────────────────────────────────────────
# ALUMINUM RESISTANCE (ohms per 1000 ft) at 75°C
# Aluminum has higher resistance than copper for the same gauge
# ─────────────────────────────────────────────
ALUMINUM_RESISTANCE = {
    "12":  3.25,
    "10":  2.04,
    "8":   1.28,
    "6":   0.808,
    "4":   0.508,
    "3":   0.403,
    "2":   0.319,
    "1":   0.253,
    "1/0": 0.201,
    "2/0": 0.159,
    "3/0": 0.126,
    "4/0": 0.100,
}


# ─────────────────────────────────────────────
# FUNCTION: get_user_inputs
# Prompts the electrician for load (amps), run length (feet), and conductor material
# Keeps asking until valid values are entered — no crashes on bad input
# ─────────────────────────────────────────────
def get_user_inputs():
    print("\n=== CEC Wire Gauge Calculator ===\n")

    # --- Get load in amps ---
    while True:
        try:
            amps = float(input("Enter load in amps: "))
            if amps <= 0:
                print("  Amps must be greater than zero. Try again.")
                continue
            break
        except ValueError:
            print("  Invalid input. Enter a number (e.g. 20 or 15.5).")

    # --- Get one-way run distance in feet ---
    while True:
        try:
            distance = float(input("Enter one-way run distance in feet: "))
            if distance <= 0:
                print("  Distance must be greater than zero. Try again.")
                continue
            break
        except ValueError:
            print("  Invalid input. Enter a number (e.g. 75 or 150.5).")

    # --- Get conductor material ---
    while True:
        material = input("Conductor material — copper or aluminum? (c/a): ").strip().lower()
        if material in ("c", "copper"):
            material = "copper"
            break
        elif material in ("a", "aluminum", "aluminium"):
            material = "aluminum"
            break
        else:
            print("  Enter 'c' for copper or 'a' for aluminum.")

    return amps, distance, material


# ─────────────────────────────────────────────
# FUNCTION: find_minimum_gauge
# Walks GAUGE_ORDER from smallest to largest
# Returns the first gauge whose ampacity handles the load
# Think of it like sizing breakers — you go up until you find one that fits
# ─────────────────────────────────────────────
def find_minimum_gauge(amps, material):
    # Select the correct ampacity table based on conductor material
    if material == "copper":
        ampacity_table = COPPER_AMPACITY
    else:
        ampacity_table = ALUMINUM_AMPACITY

    # Walk gauges from smallest to largest
    for gauge in GAUGE_LIST:
        # Skip gauges not in the selected table (e.g. 14 AWG aluminum doesn't exist in CEC)
        if gauge not in ampacity_table:
            continue

        # If this gauge can carry the load, we're done
        if ampacity_table[gauge] >= amps:
            return gauge, ampacity_table[gauge]

    # If we get here, the load exceeds even 4/0 — signal that to main()
    return None, None


# ─────────────────────────────────────────────
# FUNCTION: calculate_voltage_drop
# Formula: VD (volts) = (2 × R × I × D) / 1000
#   2     = full loop — hot conductor out, neutral/return back
#   R     = resistance in ohms per 1000 ft
#   I     = current in amps
#   D     = one-way distance in feet
# Returns voltage drop as a percentage at both 120V and 240V
# ─────────────────────────────────────────────
def calculate_voltage_drop(amps, distance, gauge, material):
    # Select resistance table based on material
    if material == "copper":
        resistance_table = COPPER_RESISTANCE
    else:
        resistance_table = ALUMINUM_RESISTANCE

    resistance = resistance_table[gauge]

    # Calculate voltage drop in volts (full loop)
    vd_volts = (2 * resistance * amps * distance) / 1000

    # Convert to percentage for each system voltage
    vd_120 = (vd_volts / 120) * 100
    vd_240 = (vd_volts / 240) * 100

    return vd_120, vd_240


# ─────────────────────────────────────────────
# FUNCTION: display_results
# Prints the final report in a clean, readable format
# CEC allows max 3% voltage drop for branch circuits
# ─────────────────────────────────────────────
def display_results(material, gauge, ampacity, vd_120, vd_240):
    print("\n--- Results ---")
    print(f"Conductor:             {material.capitalize()}")
    print(f"Recommended Gauge:     {gauge} AWG")
    print(f"Ampacity:              {ampacity}A")
    print(f"Voltage Drop (120V):   {vd_120:.1f}%")
    print(f"Voltage Drop (240V):   {vd_240:.1f}%")

    # Evaluate against CEC 3% voltage drop limit
    # 240V drop is always half of 120V, so 240V can't fail if 120V passes
    if vd_120 <= 3.0 and vd_240 <= 3.0:
        status = "PASS - Within 3% limit"
    elif vd_120 > 3.0 and vd_240 <= 3.0:
        status = "CAUTION - 120V exceeds 3% limit"
    else:
        status = "FAIL - Exceeds 3% limit at both voltages"

    print(f"Status:                {status}")
    print()


# ─────────────────────────────────────────────
# FUNCTION: main
# Ties everything together:
#   1. Collect inputs
#   2. Find minimum gauge by ampacity
#   3. Calculate voltage drop
#   4. Display results
# ─────────────────────────────────────────────
def main():
    # Step 1: Get inputs from user
    amps, distance, material = get_user_inputs()

    # Step 2: Find the minimum gauge that handles the load
    gauge, ampacity = find_minimum_gauge(amps, material)

    # If the load exceeds 4/0, no standard gauge covers it — alert and exit
    if gauge is None:
        print(f"\n  ERROR: Load of {amps}A exceeds the ampacity of 4/0 AWG {material}.")
        print("  Consult CEC Table 2 for larger conductor options or parallel runs.\n")
        return

    # Step 3: Calculate voltage drop for the selected gauge
    vd_120, vd_240 = calculate_voltage_drop(amps, distance, gauge, material)

    # Step 4: Display the full results
    display_results(material, gauge, ampacity, vd_120, vd_240)


# ─────────────────────────────────────────────
# Entry point — only runs main() if this file is executed directly
# (not if it's imported as a module elsewhere)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
