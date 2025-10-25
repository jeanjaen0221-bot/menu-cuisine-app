import os
from datetime import date
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable

from .models import Reservation, ReservationItem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.abspath(os.path.join(BASE_DIR, "../generated_pdfs"))
os.makedirs(PDF_DIR, exist_ok=True)


def _reservation_filename(reservation: Reservation) -> str:
    safe_client = str(reservation.client_name).replace(" ", "_")
    return os.path.join(PDF_DIR, f"fiche_{reservation.service_date}_{safe_client}_{reservation.id}.pdf")


def _day_filename(d: date) -> str:
    return os.path.join(PDF_DIR, f"fiches_{d}.pdf")


def _split_items(items: List[ReservationItem]):
    def norm(s: str) -> str:
        return s.lower().replace("é", "e")
    entrees = [i for i in items if norm(i.type) in ["entree", "entrees"]]
    plats = [i for i in items if norm(i.type) == "plat"]
    desserts = [i for i in items if norm(i.type) == "dessert"]
    return entrees, plats, desserts


def generate_reservation_pdf(reservation: Reservation, items: List[ReservationItem]) -> str:
    filename = _reservation_filename(reservation)

    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Section", fontSize=12, leading=14, spaceBefore=6, spaceAfter=4, textColor=colors.HexColor("#111111")))
    styles.add(ParagraphStyle(name="Meta", fontSize=10, leading=13))
    story = []

    title = f"FICHE CUISINE – {reservation.service_date}"
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 10))

    meta_data = [
        [Paragraph("Client", styles['Meta']), Paragraph(str(reservation.client_name), styles['Meta'])],
        [Paragraph("Heure d’arrivée", styles['Meta']), Paragraph(str(reservation.arrival_time), styles['Meta'])],
        [Paragraph("Couverts", styles['Meta']), Paragraph(str(reservation.pax), styles['Meta'])],
    ]
    meta_tbl = Table(meta_data, colWidths=[110, None])
    meta_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#374151')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 14))

    entrees, plats, desserts = _split_items(items)

    def section(title: str, collection: List[ReservationItem]):
        story.append(Paragraph(f"<b>{title}</b>", styles['Section']))
        data = [[Paragraph("Qté", styles['Meta']), Paragraph("Intitulé", styles['Meta'])]]
        if not collection:
            data.append(["-", "-"])
        else:
            for it in collection:
                data.append([str(it.quantity), it.name])
        tbl = Table(data, colWidths=[40, None])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#111827')),
            ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,1), (0,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 10))

    section("Entrées :", entrees)
    section("Plats :", plats)
    section("Desserts :", desserts)

    story.append(Paragraph("<b>Formule boissons :</b>", styles['Section']))
    fb_tbl = Table([[reservation.drink_formula or "-"]], colWidths=[None])
    fb_tbl.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(fb_tbl)
    story.append(Spacer(1, 10))

    notes = reservation.notes or ""
    story.append(Paragraph("<b>Notes :</b>", styles['Section']))
    note_lines = [line for line in notes.splitlines() if line.strip()] or ["-"]
    note_tbl = Table([[Paragraph(l, styles['Normal'])] for l in note_lines], colWidths=[None])
    note_tbl.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#f3f4f6')),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(note_tbl)

    doc.build(story)
    return filename


def generate_day_pdf(d: date, reservations: List[Reservation], items_by_res: dict) -> str:
    filename = _day_filename(d)
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    for idx, res in enumerate(reservations):
        if idx > 0:
            c.showPage()
        y = height - 40
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, f"FICHE CUISINE – {res.service_date}")
        c.setStrokeColorRGB(0.9, 0.9, 0.9)
        c.setLineWidth(1)
        c.line(40, y-6, width-40, y-6)
        y -= 30
        c.setFont("Helvetica", 11)
        c.drawString(40, y, f"Client : {res.client_name}")
        y -= 16
        c.drawString(40, y, f"Heure d’arrivée : {res.arrival_time}")
        y -= 16
        c.drawString(40, y, f"Couverts : {res.pax}")
        y -= 24

        entrees, plats, desserts = _split_items(items_by_res.get(str(res.id), []))

        def draw_section(title: str, collection: List[ReservationItem]):
            nonlocal y
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, title)
            y -= 16
            c.setFont("Helvetica", 11)
            if not collection:
                c.drawString(50, y, "-")
                y -= 14
            for it in collection:
                c.drawString(50, y, f"- {it.quantity}x {it.name}")
                y -= 14
            y -= 10

        draw_section("Entrées :", entrees)
        draw_section("Plats :", plats)
        draw_section("Desserts :", desserts)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Formule boissons :")
        y -= 14
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"{res.drink_formula}")
        y -= 16

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Notes :")
        y -= 14
        c.setFont("Helvetica", 11)
        if res.notes:
            for line in res.notes.splitlines():
                c.drawString(50, y, f"- {line}")
                y -= 14
        else:
            c.drawString(50, y, "-")
            y -= 14

    c.save()
    return filename
