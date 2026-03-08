# Wire Gauge Ampacity Lookup — CEC Table 2, Copper Wire at 75°C

# Define a dictionary mapping wire gauge (AWG) to ampacity in amps
ampacity_table = {
    "14": 15,    # 14 AWG copper: 15 amps at 75°C
    "12": 20,    # 12 AWG copper: 20 amps at 75°C
    "10": 30,    # 10 AWG copper: 30 amps at 75°C
    "8":  40,    # 8 AWG copper: 40 amps at 75°C
    "6":  55,    # 6 AWG copper: 55 amps at 75°C
    "4":  70,    # 4 AWG copper: 70 amps at 75°C
    "3":  85,    # 3 AWG copper: 85 amps at 75°C
    "2":  95,    # 2 AWG copper: 95 amps at 75°C
    "1":  110,   # 1 AWG copper: 110 amps at 75°C
    "1/0": 130,  # 1/0 AWG copper: 130 amps at 75°C
    "2/0": 150,  # 2/0 AWG copper: 150 amps at 75°C
    "3/0": 175,  # 3/0 AWG copper: 175 amps at 75°C
    "4/0": 200,  # 4/0 AWG copper: 200 amps at 75°C
}

# Prompt the user to enter a wire gauge and remove surrounding whitespace
gauge_input = input("Enter wire gauge (e.g. 14, 12, 10, 1/0): ").strip()

# Look up the entered gauge in the dictionary; returns None if not found
ampacity = ampacity_table.get(gauge_input)

# Check whether the lookup returned a valid ampacity value
if ampacity is not None:
    # Display the ampacity for the requested gauge
    print(f"AWG {gauge_input} copper wire is rated for {ampacity} amps at 75°C (CEC Table 2)")
else:
    # Inform the user that the gauge was not found in the table
    print(f"Gauge '{gauge_input}' not found in CEC Table 2.")
    # Show all valid gauge options so the user knows what to enter
    print(f"Valid gauges: {', '.join(ampacity_table.keys())}")
