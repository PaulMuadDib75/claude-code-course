# Wire Gauge Calculator

A command-line tool for Canadian industrial electricians that calculates the minimum wire gauge required for a given load and checks voltage drop against Canadian Electrical Code (CEC) limits.

---

## What It Does

1. **Selects the minimum wire gauge** that safely handles your load, based on CEC Table 2 ampacity ratings at 75°C.
2. **Calculates voltage drop** for the wire run at both 120V and 240V systems.
3. **Reports pass/caution/fail status** against the CEC 3% maximum voltage drop limit for branch circuits.

Supports both copper and aluminum conductors, covering 14 AWG through 4/0 AWG.

---

## Requirements

- Python 3.x
- No external libraries — uses Python standard library only

---

## How to Run

```
python wire_gauge_calculator.py
```

---

## Inputs

The tool will prompt you for three values:

| Prompt | Description | Example |
|---|---|---|
| Load in amps | The current draw of the circuit | `30` |
| One-way run distance (feet) | Length of wire from panel to load | `75` |
| Conductor material | Copper or aluminum | `c` or `a` |

Input is validated — the tool will re-prompt if you enter a non-numeric value or zero.

---

## Example Session

```
=== CEC Wire Gauge Calculator ===

Enter load in amps: 30
Enter one-way run distance in feet: 75
Conductor material — copper or aluminum? (c/a): c

--- Results ---
Conductor:             Copper
Recommended Gauge:     10 AWG
Ampacity:              30A
Voltage Drop (120V):   4.7%
Voltage Drop (240V):   2.3%
Status:                CAUTION - 120V exceeds 3% limit
```

In this example, 10 AWG copper is the minimum gauge that handles 30A, but the 75-foot run produces too much voltage drop for a 120V circuit. You would need to upsize the wire or shorten the run to comply with CEC on a 120V system. The 240V system passes.

---

## Canadian Electrical Code (CEC) Reference

This tool references the **Canadian Electrical Code (CEC)** — not the American NEC.

| Reference | Value |
|---|---|
| Ampacity source | CEC Table 2, 75°C insulation rating |
| Voltage drop limit | 3% maximum for branch circuits |
| Conductor sizes covered | 14 AWG to 4/0 AWG (copper); 12 AWG to 4/0 AWG (aluminum) |

> **Note:** CEC does not list 14 AWG aluminum — the smallest aluminum size in this tool is 12 AWG, consistent with CEC Table 2.

If your load exceeds the ampacity of 4/0 AWG, the tool will alert you to consult CEC Table 2 for larger conductors or parallel runs.

---

## Voltage Drop Formula

```
VD (volts) = (2 × R × I × D) / 1000

  2  = full loop (hot conductor out, return conductor back)
  R  = resistance in ohms per 1000 ft (from CEC Table 2)
  I  = load in amps
  D  = one-way distance in feet
```

Voltage drop percentage is then calculated against system voltage (120V or 240V).
