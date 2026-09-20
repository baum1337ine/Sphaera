#!/usr/bin/env python3
"""Build SPHAERA premium planning PDFs: lead magnet + Wochenkreis Journal prototype."""
from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets/free"
KOMPASS_OUT = OUT_DIR / "sphaera-rhythmus-kompass.pdf"
JOURNAL_OUT = OUT_DIR / "sphaera-wochenkreis-journal-prototyp.pdf"
W, H = A4

COL = {
    "night": colors.HexColor("#070912"),
    "aubergine": colors.HexColor("#211426"),
    "violet": colors.HexColor("#886BD8"),
    "ivory": colors.HexColor("#FBF6EA"),
    "cream": colors.HexColor("#F7EFE3"),
    "gold": colors.HexColor("#B89A5E"),
    "gold2": colors.HexColor("#D8C38A"),
    "ink": colors.HexColor("#241A17"),
    "muted": colors.HexColor("#675C66"),
    "field": colors.HexColor("#FFFDF7"),
}

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("SphaeraSerif", str(FONT_DIR / "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("SphaeraSerifBold", str(FONT_DIR / "DejaVuSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("SphaeraSans", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("SphaeraSansBold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Cover", fontName="SphaeraSerifBold", fontSize=34, leading=38, alignment=TA_CENTER, textColor=COL["ivory"]))
styles.add(ParagraphStyle("CoverSmall", fontName="SphaeraSans", fontSize=11, leading=16, alignment=TA_CENTER, textColor=COL["cream"]))
styles.add(ParagraphStyle("H1", fontName="SphaeraSerifBold", fontSize=23, leading=27, textColor=COL["ink"]))
styles.add(ParagraphStyle("H2", fontName="SphaeraSerifBold", fontSize=15, leading=18, textColor=COL["ink"]))
styles.add(ParagraphStyle("Body", fontName="SphaeraSans", fontSize=9.4, leading=13.5, textColor=COL["ink"]))
styles.add(ParagraphStyle("Small", fontName="SphaeraSans", fontSize=7.6, leading=10.2, textColor=COL["muted"]))
styles.add(ParagraphStyle("Quote", fontName="SphaeraSerif", fontSize=13, leading=18, alignment=TA_CENTER, textColor=COL["ink"]))


def rgba(hex_color: str, alpha: float):
    c = colors.HexColor(hex_color)
    return colors.Color(c.red, c.green, c.blue, alpha=alpha)


def p(c, text, style, x, y, w, h=900):
    q = Paragraph(text, style)
    _, th = q.wrap(w, h)
    q.drawOn(c, x, y - th)
    return y - th


def bg(c, dark=False):
    c.setFillColor(COL["night"] if dark else COL["ivory"])
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.saveState()
    c.setStrokeColor(rgba("#D8C38A", .14 if dark else .20))
    c.setLineWidth(.35)
    cx, cy = W/2, H/2 + 8*mm
    for r in (22, 42, 68, 96):
        c.circle(cx, cy, r*mm, stroke=1, fill=0)
    for a in range(0, 180, 15):
        rad = math.radians(a)
        dx, dy = math.cos(rad)*250, math.sin(rad)*250
        c.line(cx-dx, cy-dy, cx+dx, cy+dy)
    c.restoreState()


def mark(c, x, y, r, dark=False):
    c.saveState(); c.translate(x, y)
    c.setStrokeColor(COL["gold2"] if dark else COL["gold"]); c.setLineWidth(1)
    for rr in (r, r*.62, r*.28): c.circle(0, 0, rr, stroke=1, fill=0)
    for a in range(0, 180, 30):
        rad=math.radians(a); c.line(math.cos(rad)*-r, math.sin(rad)*-r, math.cos(rad)*r, math.sin(rad)*r)
    c.restoreState()


def footer(c, label):
    c.setStrokeColor(rgba("#B89A5E", .35)); c.line(18*mm, 15*mm, W-18*mm, 15*mm)
    c.setFont("SphaeraSans", 7.2); c.setFillColor(COL["muted"])
    c.drawString(18*mm, 9.5*mm, "SPHAERA")
    c.drawRightString(W-18*mm, 9.5*mm, label)


def panel(c, x, y, w, h, fill=None, radius=10):
    c.setFillColor(fill or COL["cream"]); c.setStrokeColor(rgba("#B89A5E", .28))
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)


def label(c, text, x, y):
    c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold", 7.7); c.drawString(x, y, text.upper())


def field(c, name, x, y, w, h=10*mm):
    c.setFillColor(COL["field"]); c.setStrokeColor(rgba("#B89A5E", .45)); c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    try:
        c.acroForm.textfieldRelative(name=name, x=x+2*mm, y=y+1.5*mm, width=w-4*mm, height=h-3*mm, borderWidth=0, fillColor=colors.transparent, textColor=COL["ink"], fontName="SphaeraSans", fontSize=8, forceBorder=False)
    except Exception:
        pass


def check(c, name, x, y, text):
    c.setFillColor(COL["field"]); c.setStrokeColor(COL["gold"]); c.roundRect(x, y, 4.4*mm, 4.4*mm, 1, fill=1, stroke=1)
    try:
        c.acroForm.checkboxRelative(name=name, x=x, y=y, size=4.4*mm, buttonStyle="check", borderWidth=.5, borderColor=COL["gold"], fillColor=colors.transparent, textColor=COL["aubergine"], forceBorder=True)
    except Exception:
        pass
    c.setFillColor(COL["ink"]); c.setFont("SphaeraSans", 8); c.drawString(x+6*mm, y+.7*mm, text)


def cover(c, title, subtitle, kicker, footer_text):
    bg(c, dark=True)
    c.setFillColor(rgba("#886BD8", .22)); c.circle(78*mm, 244*mm, 58*mm, fill=1, stroke=0)
    c.setFillColor(rgba("#D8C38A", .13)); c.circle(174*mm, 76*mm, 68*mm, fill=1, stroke=0)
    c.setFillColor(COL["gold2"]); c.setFont("SphaeraSansBold", 9.5); c.drawCentredString(W/2, 264*mm, kicker)
    mark(c, W/2, 205*mm, 48*mm, dark=True)
    p(c, title, styles["Cover"], 28*mm, 154*mm, W-56*mm)
    p(c, subtitle, styles["CoverSmall"], 35*mm, 102*mm, W-70*mm)
    c.setFillColor(COL["gold2"]); c.setFont("SphaeraSans", 8); c.drawCentredString(W/2, 23*mm, footer_text)
    c.showPage()


def daily_page(c, doc, day, title, impulse, questions):
    bg(c); footer(c, f"{doc} · Tag {day}")
    c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold", 8); c.drawString(18*mm, 273*mm, f"TAG {day}")
    p(c, title, styles["H1"], 18*mm, 259*mm, W-36*mm)
    panel(c, 18*mm, 215*mm, W-36*mm, 28*mm, COL["cream"], 12)
    p(c, impulse, styles["Quote"], 28*mm, 234*mm, W-56*mm)
    label(c, "Energie heute", 18*mm, 199*mm)
    for i in range(1, 11):
        x=(22+(i-1)*10.2)*mm; c.setStrokeColor(COL["gold"]); c.circle(x, 188*mm, 3.1*mm, stroke=1, fill=0)
        c.setFillColor(COL["muted"]); c.setFont("SphaeraSans", 6.3); c.drawCentredString(x, 180*mm, str(i))
    check(c, f"{doc}_tag{day}_sanft", 138*mm, 185*mm, "sanft")
    check(c, f"{doc}_tag{day}_klar", 162*mm, 185*mm, "klar")
    y = 163*mm
    for idx, (q, hint) in enumerate(questions):
        label(c, q, 18*mm, y)
        p(c, hint, styles["Small"], 18*mm, y-4*mm, W-36*mm)
        field(c, f"{doc}_tag{day}_{idx}", 18*mm, y-22*mm, W-36*mm, 13*mm)
        y -= 31*mm
    panel(c, 18*mm, 23*mm, W-36*mm, 25*mm, colors.white, 10)
    label(c, "Abendspiegel", 26*mm, 40*mm); field(c, f"{doc}_tag{day}_abend", 65*mm, 28*mm, W-91*mm, 13*mm)
    c.showPage()


def kompass_pdf():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(KOMPASS_OUT), pagesize=A4, pageCompression=1)
    c.setTitle("SPHAERA 7‑Tage‑Rhythmus‑Kompass")
    c.setAuthor("SPHAERA")
    c.setSubject("Kostenloses Arbeitsbuch für zyklische Planung, Energie und Bewusstsein")
    c.setKeywords("SPHAERA, Rhythmus, Planung, Wochenkreis, Reflexion, Lead Magnet")
    cover(c, "7‑Tage‑<br/>Rhythmus‑Kompass", "Ein ruhiger Arbeitsraum für sieben Tage: Energie lesen, Druck reduzieren, Fokus finden — und daraus eine stimmigere Woche planen.", "SPHAERA · KOSTENLOSER KOMPASS · VERSION 2", "sphaera.app · kostenloser Einstieg")

    bg(c); footer(c, "01 · Orientierung")
    mark(c, 29*mm, 269*mm, 9*mm); c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold", 8); c.drawString(43*mm, 272*mm, "SPHAERA")
    p(c, "So nutzt du diesen Kompass", styles["H1"], 18*mm, 251*mm, W-36*mm)
    p(c, "Der Kompass ist kein weiterer Plan. Er ist eine Messwoche: sieben Tage lang beobachtest du, welche Art von Aufgabe zu welcher Energie passt. Danach planst du nicht mehr aus Druck, sondern aus Mustererkenntnis.", styles["Body"], 18*mm, 229*mm, W-36*mm)
    for x, n, title, body in [(18, "1", "Morgens ausrichten", "Eine tragfähige Richtung statt zehn Ansprüche."), (76, "2", "Tagsüber verkleinern", "Reduktion ist hier kein Scheitern, sondern Rhythmuspflege."), (134, "3", "Abends lesen", "Nicht bewerten. Wiederkehr erkennen.")]:
        panel(c, x*mm, 166*mm, 52*mm, 43*mm, COL["cream"], 12); c.setFillColor(COL["gold"]); c.setFont("SphaeraSerifBold", 22); c.drawString((x+6)*mm, 194*mm, n); c.setFillColor(COL["ink"]); c.setFont("SphaeraSansBold", 8.2); c.drawString((x+6)*mm, 186*mm, title); p(c, body, styles["Small"], (x+6)*mm, 178*mm, 40*mm)
    panel(c, 18*mm, 83*mm, W-36*mm, 61*mm, colors.white, 14)
    p(c, "Dein Wochenversprechen", styles["H2"], 28*mm, 132*mm, W-56*mm)
    p(c, "Ich muss mich in dieser Woche nicht beweisen. Ich beobachte, was trägt — und plane von dort aus.", styles["Quote"], 32*mm, 119*mm, W-64*mm)
    field(c, "kompass_wochenversprechen", 28*mm, 91*mm, W-56*mm, 12*mm)
    panel(c, 18*mm, 35*mm, W-36*mm, 30*mm, rgba("#D8C38A", .16), 12)
    p(c, "Hinweis: SPHAERA ist ein Planungs‑ und Reflexionssystem. Es ersetzt keine medizinische, psychologische, rechtliche oder finanzielle Beratung.", styles["Small"], 28*mm, 55*mm, W-56*mm)
    c.showPage()

    bg(c); footer(c, "02 · Wochenkarte")
    p(c, "Sieben‑Tage‑Überblick", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Trage pro Tag nur eine Sache ein: den tragenden Fokus. Am Ende siehst du, ob deine Woche wirklich zu deinem Rhythmus passte.", styles["Body"], 18*mm, 246*mm, W-36*mm)
    y=219*mm
    for day in range(1,8):
        panel(c, 18*mm, y-18*mm, W-36*mm, 15*mm, colors.white, 8)
        c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold", 8.3); c.drawString(25*mm, y-9*mm, f"TAG {day}")
        field(c, f"kompass_ueberblick_{day}", 48*mm, y-16*mm, 96*mm, 9.5*mm)
        c.setFillColor(COL["muted"]); c.setFont("SphaeraSans", 7.2); c.drawString(148*mm, y-10*mm, "Energie")
        for i in range(1,11): c.circle((158+i*3.1)*mm, y-8.5*mm, 1.15*mm, stroke=1, fill=0)
        y -= 20*mm
    panel(c, 18*mm, 37*mm, W-36*mm, 27*mm, COL["cream"], 12)
    p(c, "Arbeitsweise: lieber jeden Tag drei Minuten eintragen als einmal perfekt. Der Wert entsteht durch Wiederkehr.", styles["Small"], 28*mm, 55*mm, W-56*mm)
    c.showPage()

    day_titles = [
        "Ankommen: Was ist wirklich da?", "Reduzieren: Was darf kleiner werden?", "Ordnen: Welche Aufgabe passt zu meinem Zustand?", "Grenze: Was schützt meine Energie?", "Ritual: Was soll bewusst wiederkehren?", "Integration: Was will nicht beschleunigt werden?", "Ausblick: Was trägt nächste Woche?"
    ]
    impulses = [
        "Ich beginne nicht mit Anspruch, sondern mit Wahrnehmung.", "Nicht alles braucht heute meine volle Kraft.", "Ich wähle nicht die lauteste Aufgabe, sondern die stimmigste.", "Eine klare Grenze ist auch eine Form von Planung.", "Ritual ist wiederkehrende Aufmerksamkeit.", "Rückzug kann Vorbereitung sein.", "Aus Muster wird Richtung."
    ]
    qs = [[("Körpergefühl", "Wie fühlt sich dein System an, bevor der Tag laut wird?"), ("Ein Fokus, der reicht", "Welche eine Richtung würde diesen Tag schon stimmig machen?"), ("Was darf kleiner werden?", "Welche Erwartung, Aufgabe oder Schleife darf reduziert werden?"), ("Passende Aufgabe", "Was trägt heute wirklich — praktisch, emotional oder kreativ?")] for _ in range(7)]
    for day in range(1,8): daily_page(c, "kompass", day, day_titles[day-1], impulses[day-1], qs[day-1])

    bg(c); footer(c, "10 · Musterkarte")
    p(c, "Musterkarte: Was die Woche gezeigt hat", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Hier wird aus Beobachtung Orientierung. Suche nicht nach Perfektion, sondern nach wiederkehrenden Hinweisen.", styles["Body"], 18*mm, 246*mm, W-36*mm)
    for x, y, title, hint, name in [(18,174,"Energiegeber","Was hat dich stabilisiert?","geber"),(109,174,"Energielecks","Was hat mehr gekostet als gedacht?","leck"),(18,103,"Gute Zeitfenster","Wann war Fokus natürlicher?","fenster"),(109,103,"Grenzen","Was braucht nächste Woche Schutz?","grenzen")]:
        panel(c, x*mm, y*mm, 82*mm, 54*mm, colors.white, 12); label(c, title, (x+7)*mm, (y+41)*mm); p(c, hint, styles["Small"], (x+7)*mm, (y+33)*mm, 68*mm); field(c, f"kompass_muster_{name}", (x+7)*mm, (y+8)*mm, 68*mm, 18*mm)
    panel(c, 18*mm, 41*mm, W-36*mm, 38*mm, COL["cream"], 13); p(c, "Mein Satz für die nächste Woche", styles["H2"], 28*mm, 68*mm, W-56*mm); field(c, "kompass_naechste_woche", 28*mm, 46*mm, W-56*mm, 12*mm)
    c.showPage()

    bg(c); footer(c, "11 · Produktleiter")
    p(c, "Wenn du weitergehen willst", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Der Kompass zeigt dir erste Muster. Das Wochenkreis Journal vertieft diese Muster in eine wiederholbare Wochenpraxis: planen, schützen, umsetzen, integrieren.", styles["Body"], 18*mm, 246*mm, W-36*mm)
    for i, (title, body) in enumerate([("1 · Kompass", "Sieben Tage lesen, was wirklich trägt."), ("2 · Wochenkreis Journal", "Wöchentliche Praxis für Fokus, Energie, Ritual und Reflexion."), ("3 · SPHAERA App", "Ein visueller Planungsraum für Tag, Woche, Mondphase und Energie.")]):
        y=(176-i*47)*mm; panel(c, 24*mm, y, W-48*mm, 32*mm, colors.white if i!=1 else COL["cream"], 12); p(c, title, styles["H2"], 34*mm, y+24*mm, W-68*mm); p(c, body, styles["Small"], 34*mm, y+12*mm, W-68*mm)
    p(c, "Interesse vormerken: sphaera.app", styles["Quote"], 34*mm, 43*mm, W-68*mm)
    c.showPage()

    cover(c, "Rhythmus ist eine Form von Klarheit.", "Wenn diese Art zu planen dich ruhiger macht, bist du bei SPHAERA richtig. Begleite die Entwicklung — leise, schön, funktional.", "SPHAERA", "sphaera.app · © SPHAERA · Weitergabe unverändert erlaubt")
    c.save()


def journal_pdf():
    """Build a differentiated Low-Ticket prototype.

    This is intentionally NOT a second 7-day observation freebie. It is a weekly
    operating room: architecture, constraints, energy budget, decision, placement,
    review. The daily layer is compressed so the product value sits in planning
    quality rather than repeated reflection prompts.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(JOURNAL_OUT), pagesize=A4, pageCompression=1)
    c.setTitle("SPHAERA Wochenkreis Journal — Prototyp 0.2")
    c.setAuthor("SPHAERA")
    c.setSubject("Wöchentliches Planungssystem für Fokus, Energie, Grenzen, Rituale und Review")
    c.setKeywords("SPHAERA, Wochenkreis Journal, Wochenplanung, Energieplanung, Ritual, PDF, Prototyp")

    cover(c, "Wochenkreis<br/>Journal", "Prototyp 0.2: ein wöchentliches Operating‑Room‑System für Fokus, Energie, Grenzen, Rituale und echte Entscheidungen. Kein zweiter Kompass — sondern die Praxis danach.", "SPHAERA · LOW‑TICKET PROTOTYP · 0.2", "sphaera.app · Wochenpraxis")

    # 01 Method / distinction
    bg(c); footer(c, "01 · Methode")
    p(c, "Nicht beobachten. Entwerfen.", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Der kostenlose Kompass fragt: Was zeigt meine Energie? Das Wochenkreis Journal fragt: Wie baue ich daraus eine bessere Woche? Es ist kein Tagebuch. Es ist ein ruhiger Planungsraum für Entscheidungen, Grenzen und Wiederkehr.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    for x, n, title, body in [
        (18,"1","Architektur","Woche als System sehen: Fokus, Rollen, Energie, Grenzen."),
        (76,"2","Platzierung","Aufgaben nicht stapeln, sondern nach Energie und Reibung verorten."),
        (134,"3","Entscheidung","Jede Woche endet mit einer konkreten Anpassung, nicht nur Gefühl."),
    ]:
        panel(c, x*mm, 167*mm, 52*mm, 48*mm, COL["cream"], 12)
        c.setFillColor(COL["gold"]); c.setFont("SphaeraSerifBold", 22); c.drawString((x+6)*mm, 198*mm, n)
        c.setFillColor(COL["ink"]); c.setFont("SphaeraSansBold", 8.4); c.drawString((x+6)*mm, 188*mm, title)
        p(c, body, styles["Small"], (x+6)*mm, 179*mm, 40*mm)
    panel(c, 18*mm, 78*mm, W-36*mm, 62*mm, colors.white, 14)
    p(c, "Wochenauftrag", styles["H2"], 28*mm, 127*mm, W-56*mm)
    p(c, "Diese Woche wird nicht daran gemessen, wie viel ich hineindrücke, sondern daran, ob das Wesentliche einen geschützten Platz bekommt.", styles["Quote"], 32*mm, 112*mm, W-64*mm)
    field(c, "journal_wochenauftrag", 28*mm, 88*mm, W-56*mm, 12*mm)
    c.showPage()

    # 02 Week architecture
    bg(c); footer(c, "02 · Wochenarchitektur")
    p(c, "Wochenarchitektur", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Bevor Aufgaben geplant werden, braucht die Woche eine innere Ordnung: ein Thema, einen Hauptgewinn, eine Grenze und eine bewusste Nicht‑Tun‑Entscheidung.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    boxes=[
        (18,174,"Wochenthema","Welcher rote Faden soll die Woche zusammenhalten?","theme"),
        (109,174,"Hauptgewinn","Was muss am Ende wirklich besser/klarer sein?","win"),
        (18,105,"Nicht‑Tun‑Liste","Was wird bewusst nicht begonnen, nicht diskutiert, nicht perfektioniert?","notdoing"),
        (109,105,"Schutzgrenze","Welche Grenze verhindert, dass die Woche ausläuft?","boundary"),
        (18,36,"Leitsatz","Ein Satz, der dich bei Reibung zurückholt.","sentence"),
    ]
    for x,y,title,hint,name in boxes:
        ww=82 if x!=18 or y!=36 else 173
        panel(c, x*mm, y*mm, ww*mm, 52*mm if y!=36 else 45*mm, colors.white, 12)
        label(c, title, (x+7)*mm, (y+38 if y!=36 else y+31)*mm)
        p(c, hint, styles["Small"], (x+7)*mm, (y+30 if y!=36 else y+23)*mm, (ww-14)*mm)
        field(c, f"journal_arch_{name}", (x+7)*mm, (y+7)*mm, (ww-14)*mm, 15*mm if y!=36 else 12*mm)
    c.showPage()

    # 03 Roles / life areas
    bg(c); footer(c, "03 · Lebensbereiche")
    p(c, "Lebensbereiche: was braucht Platz?", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Diese Seite verhindert, dass eine Woche nur aus Arbeit besteht. Nicht jeder Bereich bekommt gleich viel Raum — aber jeder darf bewusst entschieden werden.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    areas=["Körper / Energie","Beziehung / Familie","Arbeit / Projekt","Haushalt / Ordnung","Kreativität / Lernen","Stille / Ritual"]
    y=215*mm
    for i,a in enumerate(areas):
        panel(c, 18*mm, y-20*mm, W-36*mm, 16*mm, colors.white, 8)
        c.setFillColor(COL["ink"]); c.setFont("SphaeraSansBold", 8); c.drawString(25*mm, y-10*mm, a)
        label(c, "braucht", 72*mm, y-7*mm); field(c, f"journal_area_need_{i}", 93*mm, y-17*mm, 44*mm, 9*mm)
        label(c, "Grenze", 142*mm, y-7*mm); field(c, f"journal_area_bound_{i}", 164*mm, y-17*mm, 25*mm, 9*mm)
        y-=25*mm
    panel(c, 18*mm, 42*mm, W-36*mm, 34*mm, COL["cream"], 12)
    p(c, "Entscheidung: welcher Bereich bekommt diese Woche bewusst mehr Schutz?", styles["H2"], 28*mm, 66*mm, W-56*mm)
    field(c, "journal_area_decision", 28*mm, 48*mm, W-56*mm, 10*mm)
    c.showPage()

    # 04 Energy budget
    bg(c); footer(c, "04 · Energie‑Budget")
    p(c, "Energie‑Budget statt Wunschliste", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Plane mit dem, was wahrscheinlich verfügbar ist. Eine gute Woche entsteht nicht durch maximale Auslastung, sondern durch ehrliche Kapazitätsverteilung.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    for x,y,title,hint,name in [
        (18,178,"Tiefenenergie","Denken, Schreiben, Bauen, Entscheiden.","deep"),
        (109,178,"Pflegeenergie","Antworten, Sortieren, Admin, Nachziehen.","care"),
        (18,104,"Körperenergie","Bewegen, Vorbereiten, Aufräumen, Einkaufen.","body"),
        (109,104,"Integrationsenergie","Nichts erzwingen, schlafen, verarbeiten, schweigen.","rest"),
    ]:
        panel(c, x*mm, y*mm, 82*mm, 58*mm, colors.white, 12)
        label(c, title, (x+7)*mm, (y+45)*mm); p(c, hint, styles["Small"], (x+7)*mm, (y+36)*mm, 68*mm)
        field(c, f"journal_budget_{name}_tasks", (x+7)*mm, (y+17)*mm, 68*mm, 12*mm)
        c.setFillColor(COL["muted"]); c.setFont("SphaeraSans", 6.5); c.drawString((x+7)*mm, (y+8)*mm, "max. Slots diese Woche:")
        field(c, f"journal_budget_{name}_slots", (x+45)*mm, (y+5)*mm, 20*mm, 8*mm)
    panel(c, 18*mm, 43*mm, W-36*mm, 34*mm, COL["cream"], 12)
    p(c, "Wenn alles voll wirkt: Was wird zuerst verkleinert?", styles["H2"], 28*mm, 67*mm, W-56*mm)
    field(c, "journal_budget_reduce", 28*mm, 49*mm, W-56*mm, 10*mm)
    c.showPage()

    # 05 Week map
    bg(c); footer(c, "05 · Wochenkarte")
    p(c, "Wochenkarte: Platzierung", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Jetzt erst werden Tage gefüllt. Jeder Tag bekommt eine Qualität, einen Hauptslot und eine Grenze. Das ist Planung als Kreis, nicht als Druckliste.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    headers=["Tag","Qualität","Hauptslot","Grenze","Ritual"]
    xs=[18,38,72,119,154]
    for x,h in zip(xs,headers): label(c,h,x*mm,219*mm)
    y=199*mm
    for d in ["Mo","Di","Mi","Do","Fr","Sa","So"]:
        panel(c,18*mm,y-6*mm,W-36*mm,16*mm,colors.white,7)
        c.setFillColor(COL["gold"]); c.setFont("SphaeraSansBold",8); c.drawString(24*mm,y*mm,d)
        field(c,f"journal_map_{d}_quality",38*mm,y-4*mm,29*mm,9*mm)
        field(c,f"journal_map_{d}_slot",72*mm,y-4*mm,42*mm,9*mm)
        field(c,f"journal_map_{d}_bound",119*mm,y-4*mm,30*mm,9*mm)
        field(c,f"journal_map_{d}_ritual",154*mm,y-4*mm,35*mm,9*mm)
        y-=23*mm
    panel(c,18*mm,30*mm,W-36*mm,28*mm,COL["cream"],12)
    p(c,"Schlüssel: Welche zwei Tage dürfen bewusst leichter bleiben?",styles["H2"],28*mm,50*mm,W-56*mm)
    field(c,"journal_map_light_days",28*mm,35*mm,W-56*mm,9*mm)
    c.showPage()

    # 06 Friction design
    bg(c); footer(c, "06 · Reibungsdesign")
    p(c, "Reibung vorhersehen", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Gute Planung tut nicht so, als gäbe es keine Hindernisse. Sie baut vorab kleine Brücken: Wenn‑dann‑Sätze, Mindestversionen und Exit‑Regeln.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    rows=[("Wenn ich zu wenig Energie habe …","dann mache ich die Mindestversion:"),("Wenn ein Tag kippt …","dann rette ich nur:"),("Wenn ich prokrastiniere …","dann beginne ich mit:"),("Wenn andere mehr wollen …","dann lautet meine Grenze:"),("Wenn ich perfektioniere …","dann ist fertig genug bei:")]
    y=210*mm
    for i,(a,b) in enumerate(rows):
        label(c,a,18*mm,y); field(c,f"journal_friction_if_{i}",18*mm,y-17*mm,76*mm,11*mm)
        label(c,b,103*mm,y); field(c,f"journal_friction_then_{i}",103*mm,y-17*mm,89*mm,11*mm)
        y-=35*mm
    c.showPage()

    # 07 Ritual engine
    bg(c); footer(c, "07 · Ritual‑Engine")
    p(c, "Rituale, die die Woche halten", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Ein Ritual ist hier keine Dekoration. Es ist eine kleine wiederkehrende Handlung, die Orientierung zurückbringt, wenn die Woche laut wird.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    for x,y,title,hint,name in [
        (18,171,"Start‑Ritual","Wie betrittst du die Woche?","start"),
        (109,171,"Übergangs‑Ritual","Wie wechselst du zwischen Rollen?","transition"),
        (18,96,"Schutz‑Ritual","Was beendet Arbeit wirklich?","protect"),
        (109,96,"Review‑Ritual","Wann liest du die Woche?","review"),
    ]:
        panel(c,x*mm,y*mm,82*mm,58*mm,colors.white,12); label(c,title,(x+7)*mm,(y+45)*mm); p(c,hint,styles["Small"],(x+7)*mm,(y+36)*mm,68*mm); field(c,f"journal_ritual_{name}",(x+7)*mm,(y+10)*mm,68*mm,18*mm)
    panel(c,18*mm,39*mm,W-36*mm,32*mm,COL["cream"],12)
    p(c,"Kleinste tägliche Wiederholung dieser Woche",styles["H2"],28*mm,62*mm,W-56*mm); field(c,"journal_ritual_smallest",28*mm,45*mm,W-56*mm,10*mm)
    c.showPage()

    # 08 Decision board
    bg(c); footer(c, "08 · Entscheidungsboard")
    p(c, "Entscheidungsboard", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Diese Seite ersetzt vage Motivation durch klare Auswahl. Es geht nicht darum, alles zu schaffen — sondern das Richtige nicht wieder zu verlieren.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    for x,y,title,hint,name in [
        (18,176,"Must happen","Ohne das fühlt sich die Woche unfertig an.","must"),
        (109,176,"Nice if possible","Gut, aber nicht identitätskritisch.","nice"),
        (18,105,"Delegate / ask","Was muss nicht allein getragen werden?","ask"),
        (109,105,"Drop / defer","Was darf sichtbar später werden?","drop"),
    ]:
        panel(c,x*mm,y*mm,82*mm,54*mm,colors.white,12); label(c,title,(x+7)*mm,(y+41)*mm); p(c,hint,styles["Small"],(x+7)*mm,(y+33)*mm,68*mm); field(c,f"journal_decide_{name}",(x+7)*mm,(y+8)*mm,68*mm,18*mm)
    panel(c,18*mm,44*mm,W-36*mm,35*mm,COL["cream"],12)
    p(c,"Eine Entscheidung, die diese Woche leichter macht",styles["H2"],28*mm,69*mm,W-56*mm); field(c,"journal_decide_one",28*mm,50*mm,W-56*mm,11*mm)
    c.showPage()

    # 09 Midweek reset
    bg(c); footer(c, "09 · Wochenmitte")
    p(c, "Wochenmitte: neu kalibrieren", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Das Journal ist nicht starr. Zur Wochenmitte wird nicht bewertet, sondern nachjustiert: Was bleibt wesentlich, was wird kleiner, was braucht Schutz?", styles["Body"], 18*mm, 244*mm, W-36*mm)
    for title,hint,name,y in [
        ("Was ist noch wesentlich?","Nur die echte Mitte, nicht die lauten Ränder.","essential",205),
        ("Was wird ab jetzt kleiner?","Aufgabe, Anspruch, Gespräch, Perfektion.","smaller",165),
        ("Welche Grenze wird aktiviert?","Eine konkrete Handlung, kein Wunsch.","boundary",125),
        ("Was bekommt unerwartet Raum?","Weil die Woche etwas Neues gezeigt hat.","new",85),
    ]:
        label(c,title,18*mm,y*mm); p(c,hint,styles["Small"],18*mm,(y-5)*mm,W-36*mm); field(c,f"journal_mid_{name}",18*mm,(y-24)*mm,W-36*mm,13*mm)
    c.showPage()

    # 10 Weekly review matrix
    bg(c); footer(c, "10 · Wochenreview")
    p(c, "Review: aus Nutzung wird System", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Der Review fragt nicht: War ich gut? Er fragt: Was hat diese Woche als Design funktioniert — und was wird nächste Woche anders gebaut?", styles["Body"], 18*mm, 244*mm, W-36*mm)
    for x,y,title,hint,name in [
        (18,176,"Behalten","Was hat messbar getragen?","keep"),
        (109,176,"Verändern","Was war richtig, aber falsch platziert?","change"),
        (18,105,"Loslassen","Was hat mehr Energie genommen als Wert gebracht?","release"),
        (109,105,"Verstärken","Welches kleine Ritual darf größer werden?","amplify"),
    ]:
        panel(c,x*mm,y*mm,82*mm,54*mm,colors.white,12); label(c,title,(x+7)*mm,(y+41)*mm); p(c,hint,styles["Small"],(x+7)*mm,(y+33)*mm,68*mm); field(c,f"journal_review_{name}",(x+7)*mm,(y+8)*mm,68*mm,18*mm)
    panel(c,18*mm,43*mm,W-36*mm,36*mm,COL["cream"],12)
    p(c,"Entscheidung für die nächste Woche",styles["H2"],28*mm,69*mm,W-56*mm); field(c,"journal_review_next_decision",28*mm,50*mm,W-56*mm,11*mm)
    c.showPage()

    # 11 Product / app bridge
    bg(c); footer(c, "11 · Von PDF zu App")
    p(c, "Was dieses Journal für SPHAERA testet", styles["H1"], 18*mm, 268*mm, W-36*mm)
    p(c, "Der Prototyp testet nicht nur schöne Seiten. Er testet, welche Planungslogik in die App gehört: Wochenarchitektur, Energie‑Budget, Grenzen, Rituale, Review und Wiederkehr.", styles["Body"], 18*mm, 244*mm, W-36*mm)
    for i,(title,body) in enumerate([
        ("Wenn diese Seite hilft", "wird sie später als App‑Modul gedacht."),
        ("Wenn diese Seite nervt", "wird sie gestrichen oder radikal vereinfacht."),
        ("Wenn du wiederkommst", "ist SPHAERA auf dem richtigen Weg."),
    ]):
        y=(176-i*48)*mm; panel(c,24*mm,y,W-48*mm,33*mm,colors.white if i!=1 else COL["cream"],12); p(c,title,styles["H2"],34*mm,y+25*mm,W-68*mm); p(c,body,styles["Small"],34*mm,y+13*mm,W-68*mm)
    p(c,"Feedback‑Frage: Welche Seite würdest du jede Woche wirklich nutzen?",styles["Quote"],31*mm,45*mm,W-62*mm)
    c.showPage()

    cover(c, "Eine Woche ist ein System.", "Der Kompass zeigt Muster. Das Wochenkreis Journal baut daraus eine wiederholbare Praxis: entscheiden, platzieren, schützen, wiederkehren.", "SPHAERA · WOCHENKREIS JOURNAL", "Prototyp 0.2 · sphaera.app")
    c.save()

def main():
    kompass_pdf()
    journal_pdf()
    print(KOMPASS_OUT)
    print(JOURNAL_OUT)

if __name__ == "__main__":
    main()
