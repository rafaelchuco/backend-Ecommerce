from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime

def generate_invoice_pdf(order, file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, f"Factura Orden {order.order_number}")

    y = height - 1.5 * inch
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, y, f"Cliente: {order.full_name}")
    y -= 0.25 * inch
    c.drawString(1 * inch, y, f"Dirección: {order.address_line1}, {order.city}, {order.state}")
    y -= 0.25 * inch
    c.drawString(1 * inch, y, f"Teléfono: {order.phone}")

    y -= 0.5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y, "Items")
    y -= 0.25 * inch

    c.setFont("Helvetica", 12)
    for item in order.items.all():
        c.drawString(1 * inch, y, f"{item.quantity} x {item.product_name} - S/ {item.product_price:.2f}")
        y -= 0.25 * inch

    y -= 0.25 * inch
    c.drawString(1 * inch, y, f"Subtotal: S/ {order.subtotal:.2f}")
    y -= 0.25 * inch
    c.drawString(1 * inch, y, f"Envío: S/ {order.shipping_cost:.2f}")
    y -= 0.25 * inch
    c.drawString(1 * inch, y, f"IVA: S/ {order.tax:.2f}")
    y -= 0.25 * inch
    c.drawString(1 * inch, y, f"Total: S/ {order.total:.2f}")

    c.showPage()
    c.save()
