import customtkinter as ctk
import os
import webbrowser
from datetime import datetime
from tkinter import messagebox
from urllib.parse import quote
from xml.sax.saxutils import escape
from PIL import Image


# ---------- ReportLab (PDF) ----------
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Image as RLImage


# ============================================================
# KONSTANTEN / LISTEN
# ============================================================
DAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
WEEK_COLUMNS = ["Tag", "Beginn", "Ende", "Pause", "Fahrt", "Warte", "Arbeitsstunden", "Gesamt"]
TRAVEL_COLUMNS = ["Schl.", "Datum", "Abf.-Zeit", "von", "nach", "Ank.-Zeit", "Std.", "km"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "Arbeitsnachweis_Modern.pdf")
SIGNATURE_PATH = os.path.join(BASE_DIR, "signature_tech.png")
DRAFT_PATH = os.path.join(BASE_DIR, "Arbeitsnachweis_Draft.txt")
LOGO_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "img", "transnova_logo.png"))
LOGO_SIZE = (102, 51)
APP_BG_COLOR = "#C4C4C4"
SECTION_BG_COLOR = "#B8B8B8"
LABEL_TEXT_COLOR = "#1F1F1F"
DATE_FORMATS = ("%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d")


# week_entries index mapping for one day row:
# 0=Beginn, 1=Ende, 2=Pause, 3=Fahrt, 4=Warte, 5=Arbeitsstunden(auto), 6=Gesamt(auto)


# ============================================================
# DATUM / ZEIT HILFSFUNKTIONEN
# ============================================================
def _is_valid_date(value):
    if not value:
        return True
    for date_format in DATE_FORMATS:
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            continue
    return False


def _is_valid_time(value):
    if not value:
        return True
    return _parse_hhmm_to_minutes(value) is not None


def _parse_hhmm_to_minutes(value):
    if not value:
        return None
    text = value.strip()
    if ":" not in text:
        return None
    parts = text.split(":")
    if len(parts) != 2:
        return None
    hour_part, minute_part = parts
    if not hour_part.isdigit() or not minute_part.isdigit():
        return None
    hours = int(hour_part)
    minutes = int(minute_part)
    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
        return None
    return hours * 60 + minutes


def _parse_duration_to_minutes(value):
    """
    Parse Dauerwerte:
    - HH:MM (z. B. 01:30)
    - Dezimalstunden mit Komma/Punkt (z. B. 0,5 oder 1.25)
    """
    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    if ":" in text:
        parts = text.split(":")
        if len(parts) != 2:
            return None
        hour_part, minute_part = parts
        if not hour_part.isdigit() or not minute_part.isdigit():
            return None
        hours = int(hour_part)
        minutes = int(minute_part)
        if hours < 0 or minutes < 0 or minutes > 59:
            return None
        return hours * 60 + minutes

    normalized = text.replace(",", ".")
    try:
        hours_float = float(normalized)
    except ValueError:
        return None
    if hours_float < 0:
        return None
    return int(round(hours_float * 60))


def _minutes_to_hhmm(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def _minutes_to_decimal_hours(total_minutes):
    """
    Format Minuten als Dezimalstunden mit Komma.
    Beispiele: 30 -> 0,5 | 240 -> 4,0 | 630 -> 10,5
    """
    hours_value = total_minutes / 60
    decimal_text = f"{hours_value:.2f}".rstrip("0").rstrip(".")
    if "." not in decimal_text:
        decimal_text += ".0"
    return decimal_text.replace(".", ",")


# ============================================================
# WOCHENMATRIX: BERECHNUNG
# ============================================================
def update_total_for_row(row_index):
    """
    Berechnet eine Zeile der Wochenmatrix neu.

    Regeln:
    - Gesamt = Ende - Beginn
    - Arbeitsstunden = Gesamt - Pause - Fahrt - Warte
    """
    # Alle Eingaben der Tageszeile einlesen.
    begin = week_entries[row_index][0].get().strip()
    end = week_entries[row_index][1].get().strip()
    pause_raw = week_entries[row_index][2].get().strip()
    travel_raw = week_entries[row_index][3].get().strip()
    wait_raw = week_entries[row_index][4].get().strip()
    work_entry = week_entries[row_index][5]
    total_entry = week_entries[row_index][6]

    # Leere Zeile -> berechnete Felder ebenfalls leeren.
    if not begin and not end and not pause_raw and not travel_raw and not wait_raw:
        work_entry.delete(0, "end")
        total_entry.delete(0, "end")
        return

    # Pause/Fahrt/Warte duerfen leer sein und werden dann als 00:00 behandelt.
    # Zusaetzlich sind Dezimalstunden moeglich (z. B. 0,5).
    pause_minutes = _parse_duration_to_minutes(pause_raw or "00:00")
    travel_minutes = _parse_duration_to_minutes(travel_raw or "00:00")
    wait_minutes = _parse_duration_to_minutes(wait_raw or "00:00")
    if pause_minutes is None or travel_minutes is None or wait_minutes is None:
        return

    # Eingaben einheitlich als Dezimalstunden mit Komma normalisieren.
    if pause_raw:
        normalized_pause = _minutes_to_decimal_hours(pause_minutes)
        if pause_raw != normalized_pause:
            week_entries[row_index][2].delete(0, "end")
            week_entries[row_index][2].insert(0, normalized_pause)

    if travel_raw:
        normalized_travel = _minutes_to_decimal_hours(travel_minutes)
        if travel_raw != normalized_travel:
            week_entries[row_index][3].delete(0, "end")
            week_entries[row_index][3].insert(0, normalized_travel)

    if wait_raw:
        normalized_wait = _minutes_to_decimal_hours(wait_minutes)
        if wait_raw != normalized_wait:
            week_entries[row_index][4].delete(0, "end")
            week_entries[row_index][4].insert(0, normalized_wait)

    # Fuer die Gesamtzeit (Ende-Beginn) sind Beginn und Ende Pflicht.
    if not begin or not end:
        work_entry.delete(0, "end")
        total_entry.delete(0, "end")
        return

    begin_minutes = _parse_hhmm_to_minutes(begin)
    end_minutes = _parse_hhmm_to_minutes(end)
    if begin_minutes is None or end_minutes is None:
        return

    total_minutes = end_minutes - begin_minutes
    if total_minutes < 0:
        work_entry.delete(0, "end")
        total_entry.delete(0, "end")
        return

    work_minutes = total_minutes - pause_minutes - travel_minutes - wait_minutes
    if work_minutes < 0:
        work_entry.delete(0, "end")
        total_entry.delete(0, "end")
        return

    total_entry.delete(0, "end")
    total_entry.insert(0, _minutes_to_decimal_hours(total_minutes))

    work_entry.delete(0, "end")
    work_entry.insert(0, _minutes_to_decimal_hours(work_minutes))


def recalculate_all_totals():
    # Wird vor Speichern/PDF/Mail aufgerufen, damit alle Summen aktuell sind.
    for row_index in range(len(week_entries)):
        update_total_for_row(row_index)


# ============================================================
# EINGABEVALIDIERUNG
# ============================================================
def validate_form_data(action_name, require_core_fields):
    errors = []

    techniker = techniker_entry.get().strip()
    kunde = kunde_entry.get().strip()
    von = von_entry.get().strip()
    bis = bis_entry.get().strip()

    if require_core_fields:
        if not techniker:
            errors.append("- Techniker fehlt.")
        if not kunde:
            errors.append("- Kunde fehlt.")

    if von and not _is_valid_date(von):
        errors.append("- Feld 'Von' hat kein gueltiges Datum (z. B. 31.12.2026).")
    if bis and not _is_valid_date(bis):
        errors.append("- Feld 'Bis' hat kein gueltiges Datum (z. B. 31.12.2026).")
    if bool(von) != bool(bis):
        errors.append("- Bitte 'Von' und 'Bis' gemeinsam ausfuellen.")

    # Jede Tageszeile einzeln pruefen.
    for i, day in enumerate(DAYS):
        begin = week_entries[i][0].get().strip()
        end = week_entries[i][1].get().strip()
        pause = week_entries[i][2].get().strip()
        travel = week_entries[i][3].get().strip()
        wait_time = week_entries[i][4].get().strip()
        if begin and not _is_valid_time(begin):
            errors.append(f"- {day} Beginn ist ungueltig (HH:MM).")
        if end and not _is_valid_time(end):
            errors.append(f"- {day} Ende ist ungueltig (HH:MM).")
        if pause and _parse_duration_to_minutes(pause) is None:
            errors.append(f"- {day} Pause ist ungueltig (HH:MM oder Dezimal, z. B. 0,5).")
        if travel and _parse_duration_to_minutes(travel) is None:
            errors.append(f"- {day} Fahrt ist ungueltig (HH:MM oder Dezimal, z. B. 4,5).")
        if wait_time and _parse_duration_to_minutes(wait_time) is None:
            errors.append(f"- {day} Warte ist ungueltig (HH:MM oder Dezimal, z. B. 0,5).")

        begin_minutes = _parse_hhmm_to_minutes(begin)
        end_minutes = _parse_hhmm_to_minutes(end)
        pause_minutes = _parse_duration_to_minutes(pause or "00:00")
        travel_minutes = _parse_duration_to_minutes(travel or "00:00")
        wait_minutes = _parse_duration_to_minutes(wait_time or "00:00")
        if begin_minutes is not None and end_minutes is not None and end_minutes < begin_minutes:
            errors.append(f"- {day} Ende liegt vor Beginn.")
        if (
            begin_minutes is not None
            and end_minutes is not None
            and pause_minutes is not None
            and travel_minutes is not None
            and wait_minutes is not None
            and (end_minutes - begin_minutes - pause_minutes - travel_minutes - wait_minutes) < 0
        ):
            errors.append(f"- {day} Summe aus Pause/Fahrt/Warte ist laenger als die Gesamtzeit.")

    if errors:
        messagebox.showerror(
            f"{action_name} nicht moeglich",
            "Bitte folgende Eingaben korrigieren:\n\n" + "\n".join(errors),
        )
        return False
    return True


# ============================================================
# PDF GENERATOR
# ============================================================
def create_pdf():
    """
    Erstellt ein kompaktes, linksbuendiges PDF und uebernimmt alle GUI-Eingaben.
    """

    # Vor dem Export zuerst berechnete Felder aktualisieren.
    recalculate_all_totals()
    if not validate_form_data("PDF-Erzeugung", require_core_fields=True):
        return

    filename = PDF_PATH

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=28,
        leftMargin=28,
        topMargin=24,
        bottomMargin=22,
    )

    styles = getSampleStyleSheet()
    brand_dark = colors.HexColor("#1F2937")
    grid_color = colors.HexColor("#C7CDD4")
    header_bg = colors.HexColor("#E8EDF2")
    stripe_bg = colors.HexColor("#F7F9FB")

    title_style = ParagraphStyle(
        "pdf_title",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=19,
        alignment=0,  # left
        textColor=brand_dark,
        spaceAfter=0,
    )
    section_style = ParagraphStyle(
        "pdf_section",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=12,
        alignment=0,  # left
        textColor=brand_dark,
        spaceAfter=0,
    )
    normal_right = ParagraphStyle(
        "pdf_normal_right",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.4,
        leading=9.8,
        alignment=0,  # left
        textColor=brand_dark,
    )
    small_right = ParagraphStyle(
        "pdf_small_right",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.0,
        leading=8.2,
        alignment=0,  # left
        textColor=brand_dark,
    )

    elements = []

    # -------------------------
    # Titel + Logo oben rechts
    # -------------------------
    if os.path.exists(LOGO_PATH):
        pdf_logo = RLImage(LOGO_PATH, width=90, height=35)
        title_and_logo = Table(
            [[Paragraph("<b>Arbeitsnachweis</b>", title_style), pdf_logo]],
            colWidths=[doc.width - 96, 96],
            hAlign="LEFT",
        )
        title_and_logo.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, grid_color),
        ]))
        elements.append(title_and_logo)
    else:
        elements.append(Paragraph("<b>Arbeitsnachweis</b>", title_style))

    elements.append(Spacer(1, 6))

    # -------------------------
    # Stammdaten
    # -------------------------
    header_data = [
        ["Techniker", techniker_entry.get(), "Personal-Nr.", personal_entry.get()],
        ["Auftrags-Nr.", auftrag_entry.get(), "Projekt-Nr.", projekt_entry.get()],
        ["Kunde", kunde_entry.get(), "Ort", ort_entry.get()],
        ["Strasse", strasse_entry.get(), "Ansprechpartner", ansprech_entry.get()],
        ["Von", von_entry.get(), "Bis", bis_entry.get()],
    ]

    header_table = Table(
        header_data,
        colWidths=[doc.width * 0.14, doc.width * 0.36, doc.width * 0.14, doc.width * 0.36],
        hAlign="LEFT",
    )
    header_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.1),
        ("TEXTCOLOR", (0, 0), (-1, -1), brand_dark),
        ("BACKGROUND", (0, 0), (0, -1), header_bg),
        ("BACKGROUND", (2, 0), (2, -1), header_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, grid_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, grid_color),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # -------------------------
    # Auszufuehrende Arbeiten
    # -------------------------
    work_text = task_text.get("1.0", "end").strip() or "-"
    elements.append(Paragraph("<b>Auszufuehrende Arbeiten</b>", section_style))
    elements.append(Spacer(1, 2))
    safe_work_text = escape(work_text).replace("\n", "<br/>")
    elements.append(Paragraph(safe_work_text, normal_right))
    elements.append(Spacer(1, 6))

    # -------------------------
    # Wochenuebersicht
    # -------------------------
    week_data = [WEEK_COLUMNS]
    for i, day in enumerate(DAYS):
        row_values = [entry.get() for entry in week_entries[i]]
        week_data.append([day] + row_values)

    week_table = Table(
        week_data,
        colWidths=[
            doc.width * 0.06,
            doc.width * 0.13,
            doc.width * 0.13,
            doc.width * 0.11,
            doc.width * 0.10,
            doc.width * 0.10,
            doc.width * 0.19,
            doc.width * 0.18,
        ],
        hAlign="LEFT",
    )
    week_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.0),
        ("FONTSIZE", (0, 1), (-1, -1), 7.8),
        ("TEXTCOLOR", (0, 0), (-1, -1), brand_dark),
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, stripe_bg]),
        ("BOX", (0, 0), (-1, -1), 0.5, grid_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, grid_color),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
    ]))
    elements.append(week_table)
    elements.append(Spacer(1, 6))

    # -------------------------
    # Reisetabelle
    # -------------------------
    travel_data_rows = []
    for row in travel_entries:
        values = [entry.get().strip() for entry in row]
        if any(values):
            travel_data_rows.append(values)

    if travel_data_rows:
        elements.append(Paragraph("<b>Reisetabelle</b>", section_style))
        elements.append(Spacer(1, 2))

        travel_table_data = [TRAVEL_COLUMNS] + travel_data_rows
        travel_table = Table(
            travel_table_data,
            colWidths=[
                doc.width * 0.06,
                doc.width * 0.14,
                doc.width * 0.11,
                doc.width * 0.16,
                doc.width * 0.16,
                doc.width * 0.11,
                doc.width * 0.10,
                doc.width * 0.16,
            ],
            hAlign="LEFT",
        )
        travel_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7.9),
            ("FONTSIZE", (0, 1), (-1, -1), 7.6),
            ("TEXTCOLOR", (0, 0), (-1, -1), brand_dark),
            ("BACKGROUND", (0, 0), (-1, 0), header_bg),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, stripe_bg]),
            ("BOX", (0, 0), (-1, -1), 0.5, grid_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, grid_color),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 1.8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ]))
        elements.append(travel_table)
        elements.append(Spacer(1, 6))

    # -------------------------
    # Bestaetigung
    # -------------------------
    confirmation_text_pdf = (
        "Die ordnungsgemaesse Ausfuehrung des Auftrages wird bestaetigt.<br/>"
        "Die Rueckfahrzeit wird nachtraeglich eingesetzt.<br/>"
        "Die Arbeiten wurden weisungsgemaess und zur Zufriedenheit ausgefuehrt.<br/>"
        "Die Maschine wurde in funktionsfaehigem Zustand uebernommen."
    )
    elements.append(Paragraph(confirmation_text_pdf, normal_right))
    elements.append(Spacer(1, 5))

    # -------------------------
    # Unterschrift
    # -------------------------
    if os.path.exists(SIGNATURE_PATH):
        elements.append(Paragraph("<b>Unterschrift Servicetechniker</b>", section_style))
        elements.append(Spacer(1, 2))
        sign_image = RLImage(SIGNATURE_PATH, width=110, height=40)
        sign_table = Table([[sign_image]], colWidths=[110], hAlign="LEFT")
        sign_table.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        elements.append(sign_table)
        elements.append(Spacer(1, 4))

    # -------------------------
    # Montagebedingungen (kompakt)
    # -------------------------
    elements.append(Paragraph("<b>Montagebedingungen (Kurzfassung)</b>", small_right))
    elements.append(Spacer(1, 1))
    montage_text = (
        "Arbeitszeit: Mo-Do 8 Std., Fr 5 Std. (37 Std./Woche).<br/>"
        "Reise- und Wartezeiten werden wie Arbeitsstunden berechnet; "
        "bei Ueberzeiten gelten tarifliche Zuschlaege."
    )
    elements.append(Paragraph(montage_text, small_right))

    # PDF erzeugen und bei Fehlern sauber melden.
    try:
        doc.build(elements)
    except Exception as exc:
        messagebox.showerror("PDF-Fehler", f"PDF konnte nicht erzeugt werden:\n{exc}")
        return

    print("PDF erstellt:", filename)
    messagebox.showinfo("PDF erzeugt", f"PDF erstellt:\n{filename}")


# ============================================================
# GUI SETUP
# ============================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Digitaler Arbeitsnachweis")
app.geometry("1200x800")
app.configure(fg_color=APP_BG_COLOR)

# Scrollbarer Hauptcontainer fuer das gesamte Formular.
main_frame = ctk.CTkScrollableFrame(app, fg_color=APP_BG_COLOR)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)


# ============================================================
# LOGO / HEADER BAR
# ============================================================
# Titel mittig, Firmenlogo rechts.
logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
logo_frame.pack(fill="x", pady=(0, 9))

logo_image = ctk.CTkImage(
    light_image=Image.open(LOGO_PATH),
    dark_image=Image.open(LOGO_PATH),
    size=LOGO_SIZE)
logo_label = ctk.CTkLabel(logo_frame, text="", image=logo_image)
logo_label.pack(side="right", padx=(0, 8))

title_label = ctk.CTkLabel(
    logo_frame,
    text="Digitaler Arbeitsnachweis",
    font=("Arial", 24, "bold"),
    text_color="#2B2B2B",
)
title_label.place(relx=0.5, rely=0.5, anchor="center")

#ctk.CTkLabel(logo_frame, text="Firmenlogo", font=("Arial", 18, "bold")).pack(side="right")


# ============================================================
# KOPFBEREICH
# ============================================================
# Stammdatenblock (Techniker, Kunde, Projekt, Zeitraum).
header_frame = ctk.CTkFrame(main_frame, fg_color=SECTION_BG_COLOR)
header_frame.pack(fill="x", pady=5)

for i in range(5):
    header_frame.grid_columnconfigure(i, weight=1)

# Labels Zeile 1
ctk.CTkLabel(header_frame, text="Techniker", text_color=LABEL_TEXT_COLOR).grid(row=0, column=0, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Personal-Nr.", text_color=LABEL_TEXT_COLOR).grid(row=0, column=1, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Auftrags-Nr.", text_color=LABEL_TEXT_COLOR).grid(row=0, column=2, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Projekt-Nr.", text_color=LABEL_TEXT_COLOR).grid(row=0, column=3, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Von", text_color=LABEL_TEXT_COLOR).grid(row=0, column=4, padx=8, pady=(4, 1), sticky="w")

# Entries Zeile 1
techniker_entry = ctk.CTkEntry(header_frame, height=28)
techniker_entry.grid(row=1, column=0, padx=8, pady=(0, 4), sticky="ew")

personal_entry = ctk.CTkEntry(header_frame, height=28)
personal_entry.grid(row=1, column=1, padx=8, pady=(0, 4), sticky="ew")

auftrag_entry = ctk.CTkEntry(header_frame, height=28)
auftrag_entry.grid(row=1, column=2, padx=8, pady=(0, 4), sticky="ew")

projekt_entry = ctk.CTkEntry(header_frame, height=28)
projekt_entry.grid(row=1, column=3, padx=8, pady=(0, 4), sticky="ew")

von_entry = ctk.CTkEntry(header_frame, height=28)
von_entry.grid(row=1, column=4, padx=8, pady=(0, 4), sticky="ew")

# Labels Zeile 2
ctk.CTkLabel(header_frame, text="Kunde", text_color=LABEL_TEXT_COLOR).grid(row=2, column=0, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Strasse", text_color=LABEL_TEXT_COLOR).grid(row=2, column=1, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Ort", text_color=LABEL_TEXT_COLOR).grid(row=2, column=2, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Ansprechpartner", text_color=LABEL_TEXT_COLOR).grid(row=2, column=3, padx=8, pady=(4, 1), sticky="w")
ctk.CTkLabel(header_frame, text="Bis", text_color=LABEL_TEXT_COLOR).grid(row=2, column=4, padx=8, pady=(4, 1), sticky="w")

# Entries Zeile 2
kunde_entry = ctk.CTkEntry(header_frame, height=28)
kunde_entry.grid(row=3, column=0, padx=8, pady=(0, 4), sticky="ew")

strasse_entry = ctk.CTkEntry(header_frame, height=28)
strasse_entry.grid(row=3, column=1, padx=8, pady=(0, 4), sticky="ew")

ort_entry = ctk.CTkEntry(header_frame, height=28)
ort_entry.grid(row=3, column=2, padx=8, pady=(0, 4), sticky="ew")

ansprech_entry = ctk.CTkEntry(header_frame, height=28)
ansprech_entry.grid(row=3, column=3, padx=8, pady=(0, 4), sticky="ew")

bis_entry = ctk.CTkEntry(header_frame, height=28)
bis_entry.grid(row=3, column=4, padx=8, pady=(0, 4), sticky="ew")


# ============================================================
# TAETIGKEITEN
# ============================================================
# Freitext fuer die Beschreibung der ausgefuehrten Arbeiten.
task_frame = ctk.CTkFrame(main_frame, fg_color=SECTION_BG_COLOR)
task_frame.pack(fill="x", pady=6)

ctk.CTkLabel(task_frame, text="Auszufuehrende Arbeiten", font=("Arial", 12, "bold"), text_color=LABEL_TEXT_COLOR).pack(
    anchor="w", padx=10, pady=(6, 2)
)

task_text = ctk.CTkTextbox(task_frame, height=100)
task_text.pack(fill="x", padx=10, pady=(0, 8))


# ============================================================
# WOCHEN-TABELLE (GUI)
# ============================================================
# Matrix fuer Zeitwerte pro Tag.
# Benutzer-Eingaben: Beginn, Ende, Pause, Fahrt, Warte
# Automatisch berechnet: Arbeitsstunden, Gesamt
table_frame = ctk.CTkFrame(main_frame, fg_color=SECTION_BG_COLOR)
table_frame.pack(fill="x", pady=6)

# Headerzeile
for i, name in enumerate(WEEK_COLUMNS):
    if i == 0:
        table_frame.grid_columnconfigure(i, weight=0, minsize=44)
    else:
        table_frame.grid_columnconfigure(i, weight=1)
    ctk.CTkLabel(table_frame, text=name, font=("Arial", 12, "bold"), text_color=LABEL_TEXT_COLOR).grid(
        row=0, column=i, padx=2, pady=(3, 1), sticky="ew"
    )

ctk.CTkFrame(table_frame, height=1).grid(row=1, column=0, columnspan=len(WEEK_COLUMNS), sticky="ew", pady=(0, 2))

# Datenzeilen + Speicherung der Entry-Objekte
week_entries = []  # 7 Zeilen -> je Zeile 7 Entries (Beginn..Gesamt)

for r, day in enumerate(DAYS, start=2):
    ctk.CTkLabel(table_frame, text=day, font=("Arial", 11), text_color=LABEL_TEXT_COLOR).grid(
        row=r, column=0, padx=2, pady=1, sticky="ew"
    )

    row_entries = []
    for c in range(1, len(WEEK_COLUMNS)):
        e = ctk.CTkEntry(table_frame, height=24)
        e.grid(row=r, column=c, padx=2, pady=1, sticky="ew")
        row_entries.append(e)

    week_entries.append(row_entries)

for row_index, row_entries in enumerate(week_entries):
    # Bei Fokusverlust oder Enter wird die jeweilige Tageszeile neu berechnet.
    for col_index in (0, 1, 2, 3, 4):  # Beginn, Ende, Pause, Fahrt, Warte
        row_entries[col_index].bind(
            "<FocusOut>",
            lambda _event, idx=row_index: update_total_for_row(idx),
        )
        row_entries[col_index].bind(
            "<Return>",
            lambda _event, idx=row_index: update_total_for_row(idx),
        )


# ============================================================
# BESTAETIGUNG (FIXTEXT)
# ============================================================
# Fester Hinweistext zur Bestaetigung der ausgefuehrten Arbeiten.
confirmation_frame = ctk.CTkFrame(main_frame, fg_color=SECTION_BG_COLOR)
confirmation_frame.pack(fill="x", pady=6)

confirmation_text_gui = (
    "Die ordnungsgemaesse Ausfuehrung des Auftrages wird bestaetigt.\n"
    "Die Rueckfahrzeit wird nachtraeglich eingesetzt.\n"
    "Die vom Servicetechniker durchgefuehrten Arbeiten wurden weisungsgemaess zu unserer vollsten Zufriedenheit ausgefuehrt.\n"
    "Die Maschine wurde in einwandfreiem und funktionsfaehigem Zustand uebernommen.\n"
    "Die Sicherheitseinrichtungen sind komplett und auf Funktion geprueft."
)

ctk.CTkLabel(confirmation_frame, text=confirmation_text_gui, justify="left", text_color=LABEL_TEXT_COLOR).pack(
    anchor="w", padx=10, pady=10
)

# ===============================
# Unterschrift Canvas
# ===============================
# Zeichenflaeche fuer die Unterschrift mit Maus.
sig_canvas_frame = ctk.CTkFrame(main_frame, fg_color=SECTION_BG_COLOR)
sig_canvas_frame.pack(fill="x", pady=10)

ctk.CTkLabel(sig_canvas_frame, text="Unterschrift (Techniker)", text_color=LABEL_TEXT_COLOR).pack(anchor="w", padx=10)

# Canvas erstellen
sig_canvas = ctk.CTkCanvas(sig_canvas_frame, width=600, height=120, bg="white")
sig_canvas.pack(padx=10, pady=5)

# Zeichenstatus fuer den Signatur-Canvas.
is_drawing = False
last_x, last_y = None, None

# Maus-Events fuer Start, Zeichnen und Ende einer Linie.
def start_sign(event):
    global is_drawing, last_x, last_y
    is_drawing = True
    last_x, last_y = event.x, event.y

def draw(event):
    global last_x, last_y
    if is_drawing:
        sig_canvas.create_line(last_x, last_y, event.x, event.y, width=2)
        last_x, last_y = event.x, event.y

def end_sign(event):
    global is_drawing
    is_drawing = False

sig_canvas.bind("<ButtonPress-1>", start_sign)
sig_canvas.bind("<B1-Motion>", draw)
sig_canvas.bind("<ButtonRelease-1>", end_sign)


# Speichert die gezeichnete Signatur als PNG-Datei.
def save_signature():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        messagebox.showerror("Signatur", "Pillow ist nicht installiert. Bitte 'pip install pillow' ausfuehren.")
        return

    if not sig_canvas.find_all():
        messagebox.showwarning("Signatur", "Bitte zuerst im Feld unterschreiben.")
        return

    # Bildgroesse identisch zum Canvas halten.
    width = 600
    height = 120

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Alle gezeichneten Linien exportieren.
    for item in sig_canvas.find_all():
        if sig_canvas.type(item) != "line":
            continue

        coords = sig_canvas.coords(item)
        if not isinstance(coords, (list, tuple)):
            continue
        if len(coords) < 4 or len(coords) % 2 != 0:
            continue

        points = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
        draw.line(points, fill="black", width=2)

    image.save(SIGNATURE_PATH)
    print("Unterschrift gespeichert als", SIGNATURE_PATH)
    messagebox.showinfo("Signatur", f"Unterschrift gespeichert:\n{SIGNATURE_PATH}")


def save_form_data():
    # Speichert alle aktuellen Formulardaten als Text-Entwurf.
    recalculate_all_totals()
    if not validate_form_data("Speichern", require_core_fields=False):
        return

    lines = [
        f"Techniker: {techniker_entry.get().strip()}",
        f"Personal-Nr.: {personal_entry.get().strip()}",
        f"Auftrags-Nr.: {auftrag_entry.get().strip()}",
        f"Projekt-Nr.: {projekt_entry.get().strip()}",
        f"Kunde: {kunde_entry.get().strip()}",
        f"Strasse: {strasse_entry.get().strip()}",
        f"Ort: {ort_entry.get().strip()}",
        f"Ansprechpartner: {ansprech_entry.get().strip()}",
        f"Von: {von_entry.get().strip()}",
        f"Bis: {bis_entry.get().strip()}",
        "",
        "Auszufuehrende Arbeiten:",
        task_text.get("1.0", "end").strip(),
        "",
        "Wochenuebersicht:",
    ]

    for i, day in enumerate(DAYS):
        begin, end, pause, travel, wait, work_hours, total = [entry.get().strip() for entry in week_entries[i]]
        lines.append(
            f"{day}: Beginn={begin}, Ende={end}, Pause={pause}, Fahrt={travel}, Warte={wait}, "
            f"Arbeitsstunden={work_hours}, Gesamt={total}"
        )

    lines.append("")
    lines.append("Reisetabelle:")
    for i, row in enumerate(travel_entries, start=1):
        values = [entry.get().strip() for entry in row]
        lines.append(
            f"Zeile {i}: Schl.={values[0]}, Datum={values[1]}, Abf.-Zeit={values[2]}, "
            f"von={values[3]}, nach={values[4]}, Ank.-Zeit={values[5]}, Std.={values[6]}, km={values[7]}"
        )

    with open(DRAFT_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    messagebox.showinfo("Speichern", f"Daten gespeichert:\n{DRAFT_PATH}")


def prepare_email():
    # Erstellt eine vorbefuellte Mail mit Kerndaten aus dem Formular.
    recalculate_all_totals()
    if not validate_form_data("Mail", require_core_fields=True):
        return

    subject_suffix = auftrag_entry.get().strip()
    subject = "Arbeitsnachweis" + (f" - {subject_suffix}" if subject_suffix else "")

    body_lines = [
        "Hallo,",
        "",
        "anbei die Eckdaten zum Arbeitsnachweis:",
        f"Techniker: {techniker_entry.get().strip()}",
        f"Kunde: {kunde_entry.get().strip()}",
        f"Projekt-Nr.: {projekt_entry.get().strip()}",
        f"Auftrags-Nr.: {auftrag_entry.get().strip()}",
        f"Zeitraum: {von_entry.get().strip()} bis {bis_entry.get().strip()}",
        "",
        f"PDF-Datei: {PDF_PATH}",
    ]

    mailto_url = f"mailto:?subject={quote(subject)}&body={quote(chr(10).join(body_lines))}"
    opened = webbrowser.open(mailto_url)
    if not opened:
        messagebox.showwarning("Mail", "Kein Standard-Mailprogramm gefunden.")


ctk.CTkButton(sig_canvas_frame, text="Signatur speichern", command=save_signature).pack(padx=10, pady=5)



# ============================================================
# REISETABELLE (GUI + PDF)
# ============================================================
# Zusatztabelle fuer Reiseeintraege.
travel_frame = ctk.CTkFrame(main_frame, fg_color=SECTION_BG_COLOR)
travel_frame.pack(fill="x", pady=6)

for i, name in enumerate(TRAVEL_COLUMNS):
    travel_frame.grid_columnconfigure(i, weight=1)
    ctk.CTkLabel(travel_frame, text=name, font=("Arial", 12, "bold"), text_color=LABEL_TEXT_COLOR).grid(
        row=0, column=i, padx=3, pady=(3, 1), sticky="ew"
    )

travel_entries = []  # 3 Zeilen
for r in range(1, 4):
    row_entries = []
    for c in range(len(TRAVEL_COLUMNS)):
        e = ctk.CTkEntry(travel_frame, height=24)
        e.grid(row=r, column=c, padx=3, pady=1, sticky="ew")
        row_entries.append(e)
    travel_entries.append(row_entries)

ctk.CTkLabel(main_frame, text="1 = Hinreise     2 = Rueckreise     3 = Weiterreise", text_color=LABEL_TEXT_COLOR).pack(
    anchor="w", padx=10, pady=(4, 0)
)


# ============================================================
# BUTTONS
# ============================================================
# Hauptaktionen fuer den lokalen Ablauf.
button_frame = ctk.CTkFrame(main_frame, fg_color=SECTION_BG_COLOR)
button_frame.pack(fill="x", pady=10)

ctk.CTkButton(button_frame, text="Speichern", command=save_form_data).pack(side="left", padx=10)
ctk.CTkButton(button_frame, text="PDF erzeugen", command=create_pdf).pack(side="left", padx=10)
ctk.CTkButton(button_frame, text="Mail vorbereiten", command=prepare_email).pack(side="left", padx=10)


# Startet den Tkinter Event-Loop.
app.mainloop()


