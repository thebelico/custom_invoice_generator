import os 
import json
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Load fixed data
with open('fixed_data.json') as f:
    fixed_data = json.load(f)

# Load invoice-specific data
with open('invoice_data.json') as f:
    invoice_data = json.load(f)

# Get the invoice layout type
layout = invoice_data.get("invoice_type", {})
# layout = "fare_rate"  # or "item_desc"

# Convert item data according to layout
billing_items = invoice_data.get("billing_details", {})

# Select the correct data block depending on layout
if layout == "fare_rate":
    billing_items = invoice_data.get("billing_details", {})
    items = [
        {
            "description": item["description"],
            "hours": item["hours"],
            "rate": item["rate"],
            "amount": item["amount"]
        }
        for item in billing_items.values()
    ]
elif layout == "item_desc":
    billing_items = invoice_data.get("individual_items", {})

    items = [
        {
            "qty": item.get("qty", 1),
            "description": item["description"],
            "unit_price": item.get("unit_price", 0),
            "net_price": item.get("net_price", 0)
        }
        for item in billing_items.values()
    ]
else:
    print(f"⚠️  Error: layout '{layout}' is not supported. Use 'fare_rate' or 'item_desc'.")
    sys.exit(1)

# Choose template based on number of items
template_file = "advance_template.html" if len(items) > 7 else "basic_template.html"

# Set up Jinja2 template engine
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template(template_file)

# Render HTML with template and data
html_out = template.render(
    fixed_data=fixed_data,
    invoice_data=invoice_data,
    items=items,
    layout=layout
)

# Generate output filename based on current timestamp
current_time = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f"invoice_{current_time}.pdf"

# Export rendered HTML to PDF
HTML(string=html_out, base_url="templates").write_pdf(output_filename)

# Optional: output HTML to debug styles
# with open("debug_output.html", "w", encoding="utf-8") as f:
#     f.write(html_out)

print("✅ PDF generated successfully.")
