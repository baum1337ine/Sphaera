#!/usr/bin/env python3
"""Build the polished SPHAERA 7-Tage-Rhythmus-Kompass PDF."""
from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.platypus.doctemplate import LayoutError


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/free/sphaera-rhythmus-kompass.pdf"
AUX = ROOT / "assets/free/sphaera-rhythmus-kompass-preview.png"
W, H = A4

COL = {
    "ivory": colors.HexColor("#FBF6EA"),
    "cream": colors.HexColor("#F7EFE3"),
    "night": colors.HexColor("#211426"),
    "aubergine": colors.HexColor("#35203D"),
    "brown": colors.HexColor("#241A17"),
    "gold": colors.HexColor("#B89A5E"),
    "gold2": colors.HexColor("#D8C38A"),
    "rose": colors.HexColor("#D8B8A8"),
    "line": colors.HexColor("#D8C38A"),
    "muted": colors.HexColor("#6D5E66"),
    "ink": colors.HexColor("#241A17"),
    "field": colors.HexColor("#FFFDF7"),
}

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("SphaeraSerif", str(FONT_DIR / "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("SphaeraSerifBold", str(FONT_DIR / "DejaVuSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("SphaeraSans", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("SphaeraSansBold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Kicker", fontName="SphaeraSansBold", fontSize=8.5, leading=11, tracking=80, textColor=COL["gold"], uppercase=True, spaceAfter=4))
styles.add(ParagraphStyle("CoverTitle", fontName="SphaeraSerifBold", fontSize=36, leading=38, textColor=COL["ivory"], alignment=TA_CENTER))
styles.add(ParagraphStyle("CoverSubTitle", fontName="SphaeraSans", fontSize=12, leading=17, textColor=COL["cream"], alignment=TA_CENTER))
styles.add(ParagraphStyle("H1Dark", fontName="SphaeraSerifBold", fontSize=24, leading=27, textColor=COL["brown"], spaceAfter=8))
styles.add(ParagraphStyle("H2Dark", fontName="SphaeraSerifBold", fontSize=15, leading=18, textColor=COL["brown"], spaceAfter=4))
styles.add(ParagraphStyle("Body", fontName="SphaeraSans", fontSize=9.6, leading=14, textColor=COL["ink"]))
styles.add(ParagraphStyle("Small", fontName="SphaeraSans", fontSize=7.5, leading=10, textColor=COL["muted"]))
styles.add(ParagraphStyle("Quote", fontName="SphaeraSerif", fontSize=13, leading=18, textColor=COL["brown"], alignment=TA_CENTER))


def hex_rgba(hex_color: str, alpha: float) -> colors.Color:
    c = colors.HexColor(hex_color)
    return colors.Color(c.red, c.green, c.blue, alpha=alpha)


def para(c: canvas.Canvas, text: str, style: ParagraphStyle, x: float, y: float, w: float, h: float | None = None) -> float:
    p = Paragraph(text, style)
    avail_h = h or 500
    tw, th = p.wrap(w, avail_h)
    if h is not None and th > h:
        raise LayoutError(f"Paragraph too tall: {th}>{h}: {text[:40]}")
    p.drawOn(c, x, y - th)
    return y - th


def bg(c: canvas.Canvas, dark: bool = False):
    c.setFillColor(COL["night"] if dark else COL["ivory"])
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # Fine sacred-geometry background.
    cx, cy = W / 2, H / 2 + 10 * mm
    c.saveState()
    c.setStrokeColor(hex_rgba("#D8C38A" if dark else "#B89A5E", 0.13 if dark else 0.20))
    c.setLineWidth(0.35)
    for r in range(42, 270, 42):
        c.circle(cx, cy, r * mm / 3, stroke=1, fill=0)
    for a in range(0, 180, 15):
        rad = math.radians(a)
        dx, dy = math.cos(rad) * 280, math.sin(rad) * 280
        c.line(cx - dx, cy - dy, cx + dx, cy + dy)
    c.restoreState()


def footer(c: canvas.Canvas, page_label: str):
    c.setStrokeColor(hex_rgba("#B89A5E", 0.35))
    c.line(18 * mm, 15 * mm, W - 18 * mm, 15 * mm)
    c.setFont("SphaeraSans", 7.3)
    c.setFillColor(COL["muted"])
    c.drawString(18 * mm, 9.5 * mm, "SPHAERA · 7‑Tage‑Rhythmus‑Kompass")
    c.drawRightString(W - 18 * mm, 9.5 * mm, page_label)


def brand_mark(c: canvas.Canvas, x: float, y: float, r: float, dark=False):
    c.saveState()
    c.translate(x, y)
    c.setStrokeColor(COL["gold2"] if dark else COL["gold"])
    c.setLineWidth(1.0)
    for rr in (r, r * .62, r * .28):
        c.circle(0, 0, rr, stroke=1, fill=0)
    for a in range(0, 180, 30):
        rad = math.radians(a)
        c.line(math.cos(rad) * -r, math.sin(rad) * -r, math.cos(rad) * r, math.sin(rad) * r)
    c.setStrokeColor(COL["rose"] if dark else COL["aubergine"])
    c.arc(-r * .75, -r * .18, r * .75, r * .18, 200, 340)
    c.restoreState()


def rounded_panel(c, x, y, w, h, fill=COL["cream"], stroke=None, radius=10):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke or hex_rgba("#B89A5E", .28))
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    c.restoreState()


def label(c, text, x, y, color=COL["gold"]):
    c.setFillColor(color); c.setFont("SphaeraSansBold", 7.8); c.drawString(x, y, text.upper())


def line_field(c, name, x, y, w, h=9*mm, multiline=False, tooltip=""):
    c.setStrokeColor(hex_rgba("#B89A5E", .45)); c.setFillColor(COL["field"])
    c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
    try:
        c.acroForm.textfieldRelative(
            name=name,
            tooltip=tooltip or name,
            x=x + 2.2 * mm,
            y=y + 1.7 * mm,
            width=w - 4.4 * mm,
            height=h - 3.4 * mm,
            borderStyle="underlined" if not multiline else "solid",
            borderWidth=0,
            fillColor=colors.transparent,
            textColor=COL["ink"],
            fontName="SphaeraSans",
            fontSize=8,
            forceBorder=False,
        )
    except Exception:
        pass


def checkbox(c, name, x, y, text):
    c.setStrokeColor(COL["gold"]); c.setFillColor(COL["field"])
    c.roundRect(x, y, 4.5*mm, 4.5*mm, 1.2, stroke=1, fill=1)
    try:
        c.acroForm.checkboxRelative(name=name, x=x, y=y, size=4.5*mm, buttonStyle="check", borderWidth=0.5, borderColor=COL["gold"], fillColor=colors.transparent, textColor=COL["aubergine"], forceBorder=True)
    except Exception:
        pass
    c.setFillColor(COL["ink"]); c.setFont("SphaeraSans", 8)
    c.drawString(x + 6*mm, y + .7*mm, text)


def cover(c):
    bg(c, dark=True)
    c.saveState()
    c.setFillColor(hex_rgba("#886BD8", .23)); c.circle(98*mm, 246*mm, 58*mm, stroke=0, fill=1)
    c.setFillColor(hex_rgba("#D8C38A", .15)); c.circle(184*mm, 72*mm, 72*mm, stroke=0, fill=1)
    c.restoreState()
    brand_mark(c, W/2, 198*mm, 55*mm, dark=True)
    c.setFont("SphaeraSansBold", 10); c.setFillColor(COL["gold2"]); c.drawCentredString(W/2, 264*mm, "SPHAERA · KOSTENLOSER KOMPASS")
    para(c, "7‑Tage‑<br/>Rhythmus‑Kompass", styles["CoverTitle"], 28*mm, 154*mm, W-56*mm)
    para(c, "Ein schöner, ruhiger Arbeitsraum für sieben Tage: beobachten, ordnen, planen — ohne Druck und ohne Selbstoptimierungs‑Lärm.", styles["CoverSubTitle"], 36*mm, 125*mm, W-72*mm)
    rounded_panel(c, 32*mm, 54*mm, W-64*mm, 43*mm, fill=hex_rgba("#FBF6EA", .10), stroke=hex_rgba("#D8C38A", .42), radius=14)
    c.setFillColor(COL["cream"]); c.setFont("SphaeraSansBold", 9); c.drawCentredString(W/2, 84*mm, "Was du bekommst")
    c.setFont("SphaeraSans", 8.6)
    for i, t in enumerate(["7 Tagesseiten mit Morgenanker und Abendspiegel", "Energie‑Skala, Fokusfeld und Reduktionsfrage", "Wochenkreis, Musterkarte und sanfte nächste Planung"]):
        c.drawString(47*mm, (75-i*7)*mm, f"• {t}")
    c.setFont("SphaeraSans", 8); c.setFillColor(COL["gold2"]); c.drawCentredString(W/2, 24*mm, "sphaera.app")
    c.showPage()


def intro(c):
    bg(c); footer(c, "01 · Einstieg")
    brand_mark(c, 29*mm, 270*mm, 9*mm)
    c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold", 8); c.drawString(43*mm, 273*mm, "SPHAERA")
    para(c, "So arbeitest du mit dem Kompass", styles["H1Dark"], 18*mm, 251*mm, W-36*mm)
    para(c, "Dieser Kompass ist kein weiterer Plan. Er ist ein Beobachtungsraum. Du notierst sieben Tage lang, wann Energie da ist, wann Druck entsteht und welche Art von Aufgabe wirklich zu deinem Zustand passt.", styles["Body"], 18*mm, 229*mm, W-36*mm)
    # three principles
    cols = [(18*mm, "1", "Morgens: ausrichten", "Drei Minuten genügen. Wähle einen Fokus, der heute wirklich tragfähig ist."),
            (76*mm, "2", "Tagsüber: kleiner halten", "Nicht alles muss in diesen Tag. Reduktion ist hier Teil der Planung."),
            (134*mm, "3", "Abends: Muster sehen", "Bewerte dich nicht. Markiere, was stimmig war und was wiederkehrt.")]
    for x, num, title, body in cols:
        rounded_panel(c, x, 165*mm, 52*mm, 45*mm, fill=COL["cream"], radius=12)
        c.setFillColor(COL["gold"]); c.setFont("SphaeraSerifBold", 22); c.drawString(x+6*mm, 193*mm, num)
        c.setFillColor(COL["brown"]); c.setFont("SphaeraSansBold", 8.4); c.drawString(x+6*mm, 185*mm, title)
        para(c, body, styles["Small"], x+6*mm, 178*mm, 40*mm)
    rounded_panel(c, 18*mm, 80*mm, W-36*mm, 68*mm, fill=colors.white, radius=14)
    para(c, "Dein Wochenversprechen", styles["H2Dark"], 28*mm, 136*mm, W-56*mm)
    para(c, "Ich muss mich in dieser Woche nicht beweisen. Ich beobachte, was trägt — und plane von dort aus.", styles["Quote"], 32*mm, 122*mm, W-64*mm)
    line_field(c, "wochenversprechen_notiz", 28*mm, 86*mm, W-56*mm, 12*mm, multiline=True, tooltip="Eigene Ergänzung zum Wochenversprechen")
    rounded_panel(c, 18*mm, 32*mm, W-36*mm, 34*mm, fill=hex_rgba("#D8C38A", .16), radius=12)
    para(c, "Hinweis: SPHAERA ist ein Planungs‑ und Reflexionssystem. Es ersetzt keine medizinische, psychologische, rechtliche oder finanzielle Beratung.", styles["Small"], 28*mm, 53*mm, W-56*mm)
    c.showPage()


def overview(c):
    bg(c); footer(c, "02 · Überblick")
    para(c, "Sieben‑Tage‑Überblick", styles["H1Dark"], 18*mm, 268*mm, W-36*mm)
    para(c, "Trage pro Tag nur eine Sache ein: den tragenden Fokus. Am Ende siehst du, ob deine Woche wirklich zu deinem Rhythmus passte.", styles["Body"], 18*mm, 246*mm, W-36*mm)
    y = 218*mm
    for day in range(1, 8):
        rounded_panel(c, 18*mm, y-19*mm, W-36*mm, 16*mm, fill=colors.white, radius=8)
        c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold", 8.5); c.drawString(25*mm, y-9*mm, f"TAG {day}")
        line_field(c, f"ueberblick_tag_{day}", 48*mm, y-16.5*mm, 96*mm, 10*mm, tooltip=f"Fokus für Tag {day}")
        c.setFillColor(COL["muted"]); c.setFont("SphaeraSans", 7.5); c.drawString(146*mm, y-10*mm, "Energie")
        for i in range(1, 11):
            c.setStrokeColor(hex_rgba("#B89A5E", .55)); c.circle((156+i*3.3)*mm, y-8.5*mm, 1.25*mm, stroke=1, fill=0)
        y -= 20.5*mm
    rounded_panel(c, 18*mm, 38*mm, W-36*mm, 26*mm, fill=COL["cream"], radius=12)
    para(c, "Arbeitsweise: Lieber jeden Tag kurz eintragen als einmal perfekt. Der Wert entsteht durch Wiederkehr.", styles["Small"], 28*mm, 55*mm, W-56*mm)
    c.showPage()


def day_page(c, day: int):
    bg(c); footer(c, f"{day+2:02d} · Tag {day}")
    c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold", 8); c.drawString(18*mm, 274*mm, f"TAG {day} VON 7")
    para(c, f"Tag {day}: Morgenanker & Abendspiegel", styles["H1Dark"], 18*mm, 259*mm, W-36*mm)
    rounded_panel(c, 18*mm, 211*mm, W-36*mm, 30*mm, fill=COL["cream"], radius=12)
    para(c, "Heute plane ich nicht gegen mich, sondern mit meinem tatsächlichen Zustand.", styles["Quote"], 28*mm, 232*mm, W-56*mm)
    # energy scale
    label(c, "Energie heute", 18*mm, 197*mm)
    for i in range(1, 11):
        x = (22 + (i-1)*10.3) * mm
        c.setStrokeColor(COL["gold"]); c.circle(x, 185*mm, 3.2*mm, stroke=1, fill=0)
        c.setFillColor(COL["muted"]); c.setFont("SphaeraSans", 6.3); c.drawCentredString(x, 176.7*mm, str(i))
    checkbox(c, f"tag_{day}_sanft", 139*mm, 183*mm, "sanft")
    checkbox(c, f"tag_{day}_klar", 162*mm, 183*mm, "klar")
    # fields
    sections = [
        ("Körpergefühl", "Wie fühlt sich dein System an, bevor der Tag laut wird?", f"tag_{day}_koerper", 164),
        ("Ein Fokus, der reicht", "Welche eine Richtung würde diesen Tag schon stimmig machen?", f"tag_{day}_fokus", 134),
        ("Was darf kleiner werden?", "Welche Erwartung, Aufgabe oder Schleife darf heute reduziert werden?", f"tag_{day}_kleiner", 104),
        ("Welche Aufgabe passt zu meinem Zustand?", "Nicht: Was sollte ich schaffen? Sondern: Was trägt heute?", f"tag_{day}_aufgabe", 74),
    ]
    for title, hint, name, yy in sections:
        label(c, title, 18*mm, yy*mm)
        c.setFillColor(COL["muted"]); c.setFont("SphaeraSans", 7); c.drawString(18*mm, (yy-4)*mm, hint)
        line_field(c, name, 18*mm, (yy-20)*mm, W-36*mm, 12*mm, multiline=True, tooltip=title)
    rounded_panel(c, 18*mm, 24*mm, W-36*mm, 28*mm, fill=colors.white, radius=10)
    label(c, "Abendspiegel", 26*mm, 43*mm)
    line_field(c, f"tag_{day}_abend", 65*mm, 30*mm, W-91*mm, 14*mm, multiline=True, tooltip="Was war heute stimmig?")
    c.showPage()


def weekly_circle(c):
    bg(c); footer(c, "10 · Wochenkreis")
    para(c, "Wochenkreis: Muster statt Urteil", styles["H1Dark"], 18*mm, 268*mm, W-36*mm)
    para(c, "Am Ende zählt nicht, ob du alles erledigt hast. Entscheidend ist, welche Art von Tag welche Art von Arbeit getragen hat.", styles["Body"], 18*mm, 246*mm, W-36*mm)
    cx, cy, r = 105*mm, 151*mm, 52*mm
    c.setStrokeColor(COL["gold"]); c.setLineWidth(1.2); c.circle(cx, cy, r, stroke=1, fill=0)
    c.setStrokeColor(hex_rgba("#B89A5E", .45)); c.setLineWidth(.6)
    for i in range(7):
        a = math.radians(90 - i*360/7)
        c.line(cx, cy, cx + math.cos(a)*r, cy + math.sin(a)*r)
        c.setFillColor(COL["brown"]); c.setFont("SphaeraSansBold", 7)
        c.drawCentredString(cx + math.cos(a-0.45)*r*.78, cy + math.sin(a-0.45)*r*.78, f"T{i+1}")
    line_field(c, "wochenkreis_mitte", cx-24*mm, cy-7*mm, 48*mm, 14*mm, multiline=True, tooltip="Das Wochenmuster in einem Satz")
    x0 = 18*mm
    qs = [
        ("Was gab Energie?", "wk_energie"),
        ("Was nahm Energie?", "wk_nahm"),
        ("Welche Arbeit gehört morgens?", "wk_morgen"),
        ("Welche Arbeit gehört abends?", "wk_abend"),
        ("Was braucht nächste Woche eine Grenze?", "wk_grenze"),
    ]
    y = 70*mm
    for i, (q, name) in enumerate(qs):
        label(c, q, x0, y + 13*mm)
        line_field(c, name, x0, y, W-36*mm, 10*mm, multiline=True, tooltip=q)
        y -= 22*mm
    c.showPage()


def next_week(c):
    bg(c); footer(c, "11 · Nächste Woche")
    para(c, "Aus Beobachtung wird Planung", styles["H1Dark"], 18*mm, 268*mm, W-36*mm)
    para(c, "Wähle nur wenige klare Wiederholungen. Ein guter Rhythmus wird nicht lauter — er wird verlässlicher.", styles["Body"], 18*mm, 246*mm, W-36*mm)
    boxes = [(18, 168, "Wiederholen", "Was soll bewusst wiederkehren?", "nw_wiederholen"), (109, 168, "Reduzieren", "Was braucht weniger Raum?", "nw_reduzieren"), (18, 98, "Schützen", "Welche Grenze hält deine Energie?", "nw_schuetzen"), (109, 98, "Beginnen", "Welcher kleine nächste Schritt ist dran?", "nw_beginnen")]
    for x, y, title, hint, name in boxes:
        rounded_panel(c, x*mm, y*mm, 82*mm, 56*mm, fill=colors.white, radius=12)
        label(c, title, (x+7)*mm, (y+43)*mm)
        para(c, hint, styles["Small"], (x+7)*mm, (y+35)*mm, 68*mm)
        line_field(c, name, (x+7)*mm, (y+8)*mm, 68*mm, 19*mm, multiline=True, tooltip=title)
    rounded_panel(c, 18*mm, 39*mm, W-36*mm, 42*mm, fill=COL["cream"], radius=14)
    para(c, "Mein Satz für die nächste Woche", styles["H2Dark"], 28*mm, 67*mm, W-56*mm)
    line_field(c, "nw_satz", 28*mm, 45*mm, W-56*mm, 13*mm, multiline=True, tooltip="Ein Satz für die nächste Woche")
    c.showPage()


def closing(c):
    bg(c, dark=True)
    brand_mark(c, W/2, 210*mm, 45*mm, dark=True)
    para(c, "Wenn diese Art zu planen dich ruhiger macht, bist du bei SPHAERA richtig.", styles["CoverTitle"], 28*mm, 154*mm, W-56*mm)
    para(c, "SPHAERA entsteht als visueller Planungsraum für Tag, Woche, Monat, Energie und zyklische Orientierung. Begleite die Entwicklung — leise, schön, funktional.", styles["CoverSubTitle"], 34*mm, 91*mm, W-68*mm)
    rounded_panel(c, 56*mm, 39*mm, 98*mm, 22*mm, fill=hex_rgba("#FBF6EA", .10), stroke=hex_rgba("#D8C38A", .42), radius=11)
    c.setFillColor(COL["gold2"]); c.setFont("SphaeraSansBold", 10); c.drawCentredString(W/2, 50*mm, "sphaera.app")
    c.setFillColor(COL["gold2"]); c.setFont("SphaeraSans", 7.8); c.drawCentredString(W/2, 20*mm, "© SPHAERA · Kostenloser Kompass · Weitergabe unverändert erlaubt")
    c.showPage()


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
    c.setTitle("SPHAERA 7‑Tage‑Rhythmus‑Kompass")
    c.setAuthor("SPHAERA")
    c.setSubject("Kostenloses Arbeitsbuch für zyklische Planung, Energie und Bewusstsein")
    c.setKeywords("SPHAERA, Rhythmus, Planung, Wochenkreis, Reflexion, PDF")
    cover(c)
    intro(c)
    overview(c)
    for d in range(1, 8):
        day_page(c, d)
    weekly_circle(c)
    next_week(c)
    closing(c)
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
