# quote_generator.py
# Generates a professional PDF quote for electrical jobs.
# Uses the reportlab library to create a formatted, printable PDF.

# --- Imports ---
from reportlab.lib.pagesizes import letter          # Standard letter page size (8.5 x 11 in)
from reportlab.lib import colors                    # Color constants (e.g., black, white, grey)
from reportlab.lib.units import inch                # Measurement unit helper
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Text style tools
from reportlab.platypus import (                    # PDF building blocks (called "flowables")
    SimpleDocTemplate,                              # The document itself
    Table,                                          # Grid/table element
    TableStyle,                                     # Styling rules for tables
    Paragraph,                                      # A block of text with styling
    Spacer,                                         # Blank vertical space
    HRFlowable                                      # A horizontal divider line
)
from datetime import date, datetime                 # For today's date and quote number
import os                                           # For file path handling

# --- Constants ---
# Think of these like your panel schedule defaults — they can be changed here once
# and everything downstream updates automatically.

LABOR_RATE    = 95    # CAD per hour — adjust this if your rate changes
OVERHEAD_RATE = 0.15  # 15% overhead applied to materials subtotal

# Replace these placeholders with your real company details
COMPANY_NAME    = "YOUR COMPANY NAME"
COMPANY_ADDRESS = "Your Address, City, Province, Postal Code"
COMPANY_PHONE   = "(XXX) XXX-XXXX"
COMPANY_EMAIL   = "youremail@example.com"


# =============================================================================
# INPUT FUNCTIONS
# Think of these like your site walkthrough — gathering all the info you need
# before you start any actual work.
# =============================================================================

def get_client_info():
    """Ask the user for basic client and job information."""

    print("\n--- CLIENT INFORMATION ---")

    client_name    = input("Client name: ").strip()
    client_address = input("Client address: ").strip()
    job_description = input("Job description: ").strip()

    # Pack everything into a dictionary — like a labeled wire bundle
    return {
        "name":        client_name,
        "address":     client_address,
        "description": job_description
    }


def get_line_items():
    """
    Ask the user to enter materials one at a time.
    Loop continues until the user types 'done'.
    Each item gets its line total calculated here.
    """

    print("\n--- MATERIALS ---")
    print("Enter each material. Type 'done' when finished.\n")

    line_items = []  # This list will hold all the materials entered

    while True:
        # Ask for the material name — typing 'done' exits the loop
        material_name = input("Material name (or 'done' to finish): ").strip()

        if material_name.lower() == "done":
            # User is finished entering materials — break out of the loop
            break

        if not material_name:
            # Blank entry — skip it and ask again
            print("  Please enter a material name.")
            continue

        # Ask for quantity — validate that it's a whole number
        while True:
            try:
                qty = int(input(f"  Quantity of '{material_name}': "))
                if qty <= 0:
                    print("  Quantity must be greater than zero.")
                    continue
                break  # Valid number — exit this inner loop
            except ValueError:
                # Like a wrong breaker size — doesn't fit, try again
                print("  Please enter a whole number for quantity.")

        # Ask for unit price — validate that it's a valid dollar amount
        while True:
            try:
                unit_price = float(input(f"  Unit price for '{material_name}' (CAD): $"))
                if unit_price < 0:
                    print("  Price cannot be negative.")
                    continue
                break  # Valid price — exit this inner loop
            except ValueError:
                print("  Please enter a number for the price (e.g. 12.50).")

        # Calculate the total cost for this line item
        line_total = qty * unit_price

        # Store this item as a dictionary and add it to the list
        line_items.append({
            "name":       material_name,
            "qty":        qty,
            "unit_price": unit_price,
            "line_total": line_total
        })

        # Confirm what was just added
        print(f"  Added: {qty} x {material_name} @ ${unit_price:.2f} = ${line_total:.2f}\n")

    if not line_items:
        print("  (No materials entered — materials section will show empty.)")

    return line_items


def get_labor_hours():
    """Ask the user for the total number of labor hours for the job."""

    print("\n--- LABOR ---")

    while True:
        try:
            hours = float(input("Total labor hours: "))
            if hours < 0:
                print("  Hours cannot be negative.")
                continue
            break  # Valid input — exit the loop
        except ValueError:
            print("  Please enter a number (e.g. 8 or 4.5).")

    return hours


# =============================================================================
# CALCULATION FUNCTION
# Like doing your load calculation — all the math happens here in one place.
# =============================================================================

def calculate_totals(line_items, labor_hours):
    """
    Calculate all the dollar totals for the quote.

    Returns a dictionary with:
      - materials_subtotal : sum of all material line totals
      - labor_cost         : labor hours x $95/hr
      - overhead           : 15% of materials subtotal
      - grand_total        : everything added together
    """

    # Sum up every line item's total — like adding up circuit loads
    materials_subtotal = sum(item["line_total"] for item in line_items)

    # Labor is simply hours multiplied by the hourly rate
    labor_cost = labor_hours * LABOR_RATE

    # Overhead is a percentage of the materials cost (covers your truck, tools, markup)
    overhead = materials_subtotal * OVERHEAD_RATE

    # Grand total is everything combined
    grand_total = materials_subtotal + labor_cost + overhead

    return {
        "materials_subtotal": materials_subtotal,
        "labor_cost":         labor_cost,
        "overhead":           overhead,
        "grand_total":        grand_total
    }


# =============================================================================
# PDF GENERATION FUNCTION
# This is where we wire everything up into the finished document.
# Think of reportlab like building a panel: you assemble components (breakers/
# flowables) into a box (the document), then close it up and it's ready to use.
# =============================================================================

def generate_pdf(client_info, line_items, totals, labor_hours):
    """
    Build and save the PDF quote.
    Returns the filename that was saved.
    """

    # --- File Name ---
    # Build the filename from the client name and today's date
    # e.g., "John Smith" + 2026-05-05 → quote_johnsmith_2026-05-05.pdf
    today_str   = date.today().strftime("%Y-%m-%d")
    client_slug = client_info["name"].replace(" ", "").lower()  # Remove spaces, lowercase
    filename    = f"quote_{client_slug}_{today_str}.pdf"

    # --- Quote Number ---
    # Use timestamp so every quote is unique, even two on the same day
    quote_number = datetime.now().strftime("%Y%m%d-%H%M%S")

    # --- Document Setup ---
    # SimpleDocTemplate is the container — like the enclosure panel you bolt everything into
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,         # 8.5 x 11 inches
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    # --- Styles ---
    # getSampleStyleSheet gives us pre-built text styles (Normal, Heading1, etc.)
    styles = getSampleStyleSheet()

    # Custom style for the company name at the top (big and bold)
    style_company = ParagraphStyle(
        name="CompanyName",
        fontSize=18,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a3a5c"),  # Dark navy blue
        spaceAfter=4
    )

    # Style for the large "ELECTRICAL QUOTE" label
    style_quote_title = ParagraphStyle(
        name="QuoteTitle",
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a3a5c"),
        spaceBefore=12,
        spaceAfter=4
    )

    # Style for section labels like "Prepared for:"
    style_label = ParagraphStyle(
        name="Label",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.grey
    )

    # Style for regular body text
    style_body = ParagraphStyle(
        name="Body",
        fontSize=10,
        fontName="Helvetica",
        leading=14  # Line spacing
    )

    # Style for the small footer text at the bottom
    style_footer = ParagraphStyle(
        name="Footer",
        fontSize=8,
        fontName="Helvetica-Oblique",  # Italic
        textColor=colors.grey,
        alignment=1  # 1 = center
    )

    # --- Story ---
    # The "story" is a list of flowables (building blocks) that reportlab
    # assembles top-to-bottom on the page — like stacking items in a tray.
    story = []

    # ==========================================================================
    # SECTION 1: COMPANY HEADER
    # ==========================================================================

    story.append(Paragraph(COMPANY_NAME, style_company))
    story.append(Paragraph(COMPANY_ADDRESS, style_body))
    story.append(Paragraph(f"Phone: {COMPANY_PHONE}  |  Email: {COMPANY_EMAIL}", style_body))

    # Horizontal divider line — like a bus bar separating sections
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 8))

    # ==========================================================================
    # SECTION 2: QUOTE METADATA (title, date, quote number)
    # ==========================================================================

    story.append(Paragraph("ELECTRICAL QUOTE", style_quote_title))
    story.append(Paragraph(f"Date: {date.today().strftime('%B %d, %Y')}    Quote #: {quote_number}", style_body))
    story.append(Spacer(1, 16))

    # ==========================================================================
    # SECTION 3: CLIENT INFO
    # ==========================================================================

    story.append(Paragraph("PREPARED FOR:", style_label))
    story.append(Paragraph(client_info["name"], style_body))
    story.append(Paragraph(client_info["address"], style_body))
    story.append(Spacer(1, 12))

    # ==========================================================================
    # SECTION 4: JOB DESCRIPTION
    # ==========================================================================

    story.append(Paragraph("SCOPE OF WORK:", style_label))
    story.append(Paragraph(client_info["description"], style_body))
    story.append(Spacer(1, 18))

    # ==========================================================================
    # SECTION 5: MATERIALS TABLE
    # A Table in reportlab is a grid of rows and columns.
    # Each row is a list; the whole table is a list of rows.
    # ==========================================================================

    # Column headers — the top row of the table
    table_data = [
        ["Description", "Qty", "Unit Price", "Total"]
    ]

    # Add one row per line item
    for item in line_items:
        table_data.append([
            item["name"],
            str(item["qty"]),
            f"${item['unit_price']:,.2f}",
            f"${item['line_total']:,.2f}"
        ])

    # If no materials were entered, add a placeholder row so the table isn't empty
    if not line_items:
        table_data.append(["No materials entered", "", "", "$0.00"])

    # --- Summary Rows ---
    # These go below the materials as part of the same table for clean alignment
    table_data.append(["", "", "", ""])  # Blank spacer row

    table_data.append([
        "", "", "Materials Subtotal:",
        f"${totals['materials_subtotal']:,.2f}"
    ])
    table_data.append([
        "", "", f"Labour ({labor_hours:.1f} hrs @ ${LABOR_RATE}/hr):",
        f"${totals['labor_cost']:,.2f}"
    ])
    table_data.append([
        "", "", f"Overhead ({int(OVERHEAD_RATE * 100)}% on materials):",
        f"${totals['overhead']:,.2f}"
    ])

    # Grand total row (will be styled separately below)
    grand_total_row_index = len(table_data)  # Remember which row this is
    table_data.append([
        "", "", "GRAND TOTAL:",
        f"${totals['grand_total']:,.2f}"
    ])

    # --- Column Widths ---
    # Total usable width = 8.5in - 2in margins = 6.5in
    col_widths = [3.2 * inch, 0.6 * inch, 1.5 * inch, 1.2 * inch]

    # Build the Table object
    materials_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # --- Table Styling ---
    # TableStyle takes a list of commands. Each command is a tuple:
    # (command_name, start_cell, end_cell, value)
    # Cells are referenced as (col, row) starting at (0, 0) top-left.
    # (-1, -1) means "last column, last row" — a shorthand for the whole table edge.

    table_style_commands = [
        # === HEADER ROW (row 0) ===
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),  # Dark navy header
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),                # White header text
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 8),
        ("TOPPADDING",   (0, 0), (-1, 0), 8),

        # === ALL DATA ROWS ===
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("TOPPADDING",   (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 1), (-1, -1), 5),

        # Right-align the Qty, Unit Price, and Total columns
        ("ALIGN",        (1, 0), (-1, -1), "RIGHT"),

        # Grid lines on the materials section only (rows 1 to last material row)
        ("GRID",         (0, 0), (-1, len(line_items) if line_items else 1), 0.5, colors.HexColor("#cccccc")),

        # Light line above the summary section
        ("LINEABOVE",    (0, len(line_items) + 2), (-1, len(line_items) + 2), 1, colors.HexColor("#1a3a5c")),

        # Bold the summary label column
        ("FONTNAME",     (2, len(line_items) + 2), (2, -1), "Helvetica-Bold"),

        # === GRAND TOTAL ROW ===
        ("BACKGROUND",   (0, grand_total_row_index), (-1, grand_total_row_index), colors.HexColor("#e8f0f8")),  # Light blue highlight
        ("FONTNAME",     (0, grand_total_row_index), (-1, grand_total_row_index), "Helvetica-Bold"),
        ("FONTSIZE",     (0, grand_total_row_index), (-1, grand_total_row_index), 11),
        ("TOPPADDING",   (0, grand_total_row_index), (-1, grand_total_row_index), 8),
        ("BOTTOMPADDING",(0, grand_total_row_index), (-1, grand_total_row_index), 8),
        ("LINEABOVE",    (0, grand_total_row_index), (-1, grand_total_row_index), 1.5, colors.HexColor("#1a3a5c")),
        ("LINEBELOW",    (0, grand_total_row_index), (-1, grand_total_row_index), 1.5, colors.HexColor("#1a3a5c")),
    ]

    # Apply alternating row shading to material rows (every other row, light grey)
    for row_index in range(1, len(line_items) + 1):
        if row_index % 2 == 0:
            table_style_commands.append(
                ("BACKGROUND", (0, row_index), (-1, row_index), colors.HexColor("#f5f5f5"))
            )

    materials_table.setStyle(TableStyle(table_style_commands))

    story.append(materials_table)
    story.append(Spacer(1, 24))

    # ==========================================================================
    # SECTION 6: FOOTER
    # ==========================================================================

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Thank you for your business. All amounts in Canadian dollars (CAD). "
        "This quote is valid for 30 days from the date above.",
        style_footer
    ))

    # --- Build the PDF ---
    # This is the step that actually writes the file to disk.
    # Like closing the panel door and energizing the circuit.
    doc.build(story)

    return filename


# =============================================================================
# MAIN FUNCTION
# The entry point — this runs everything in order, like your commissioning checklist.
# =============================================================================

def main():
    print("=" * 50)
    print("   ELECTRICAL QUOTE GENERATOR")
    print("=" * 50)

    # Step 1: Collect all input from the user
    client_info  = get_client_info()
    line_items   = get_line_items()
    labor_hours  = get_labor_hours()

    # Step 2: Run all the calculations
    totals = calculate_totals(line_items, labor_hours)

    # Step 3: Show a summary on screen before generating the PDF
    print("\n--- QUOTE SUMMARY ---")
    print(f"  Materials Subtotal : ${totals['materials_subtotal']:,.2f}")
    print(f"  Labour Cost        : ${totals['labor_cost']:,.2f}")
    print(f"  Overhead (15%)     : ${totals['overhead']:,.2f}")
    print(f"  GRAND TOTAL        : ${totals['grand_total']:,.2f}")

    # Step 4: Generate the PDF
    print("\nGenerating PDF...")
    saved_filename = generate_pdf(client_info, line_items, totals, labor_hours)

    # Step 5: Confirm to the user where the file was saved
    print(f"\nQuote saved as: {saved_filename}")
    print(f"Location: {os.path.abspath(saved_filename)}")
    print("Done!")


# --- Entry Point ---
# This line means: only run main() if this script is run directly,
# not if it's imported by another script.
if __name__ == "__main__":
    main()
