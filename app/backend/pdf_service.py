import os
from datetime import date
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

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
    story = []

    title = f"FICHE CUISINE – {reservation.service_date}"
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))

    meta = (
        f"Client : {reservation.client_name}<br/>"
        f"Heure d’arrivée : {reservation.arrival_time}<br/>"
        f"Couverts : {reservation.pax}"
    )
    story.append(Paragraph(meta, styles['Normal']))
    story.append(Spacer(1, 12))

    entrees, plats, desserts = _split_items(items)

    def section(title: str, collection: List[ReservationItem]):
        story.append(Paragraph(f"<b>{title}</b>", styles['Heading3']))
        if not collection:
            story.append(Paragraph("-", styles['Normal']))
        for it in collection:
            story.append(Paragraph(f"- {it.quantity}x {it.name}", styles['Normal']))
        story.append(Spacer(1, 8))

    section("Entrées :", entrees)
    section("Plats :", plats)
    section("Desserts :", desserts)

    story.append(Paragraph(f"<b>Formule boissons :</b> {reservation.drink_formula}", styles['Normal']))
    story.append(Spacer(1, 8))

    notes = reservation.notes or ""
    story.append(Paragraph("<b>Notes :</b>", styles['Heading3']))
    if notes.strip():
        for line in notes.splitlines():
            story.append(Paragraph(f"- {line}", styles['Normal']))
    else:
        story.append(Paragraph("-", styles['Normal']))

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
