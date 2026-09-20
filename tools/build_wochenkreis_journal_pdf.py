#!/usr/bin/env python3
"""Build the differentiated SPHAERA Wochenkreis Journal prototype PDF."""
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
OUT = ROOT / "assets/free/sphaera-wochenkreis-journal-prototyp.pdf"
W, H = A4

COL = {
    "night": colors.HexColor("#070912"),
    "violet_dark": colors.HexColor("#211426"),
    "violet": colors.HexColor("#8067C8"),
    "ivory": colors.HexColor("#FBF6EA"),
    "cream": colors.HexColor("#F4E9DA"),
    "paper": colors.HexColor("#FFFDF7"),
    "gold": colors.HexColor("#B89A5E"),
    "gold2": colors.HexColor("#D8C38A"),
    "ink": colors.HexColor("#221817"),
    "muted": colors.HexColor("#665A62"),
    "line": colors.HexColor("#D9C79A"),
}
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("Serif", str(FONT_DIR / "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("SerifBold", str(FONT_DIR / "DejaVuSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sans", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("SansBold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Cover", fontName="SerifBold", fontSize=34, leading=38, alignment=TA_CENTER, textColor=COL["ivory"]))
styles.add(ParagraphStyle("CoverSub", fontName="Sans", fontSize=10.5, leading=15.5, alignment=TA_CENTER, textColor=COL["cream"]))
styles.add(ParagraphStyle("H1", fontName="SerifBold", fontSize=22, leading=26, textColor=COL["ink"]))
styles.add(ParagraphStyle("H2", fontName="SerifBold", fontSize=13.2, leading=16, textColor=COL["ink"]))
styles.add(ParagraphStyle("Body", fontName="Sans", fontSize=8.9, leading=12.6, textColor=COL["ink"]))
styles.add(ParagraphStyle("Small", fontName="Sans", fontSize=7.25, leading=9.6, textColor=COL["muted"]))
styles.add(ParagraphStyle("Quote", fontName="Serif", fontSize=12.3, leading=17, alignment=TA_CENTER, textColor=COL["ink"]))
styles.add(ParagraphStyle("Tiny", fontName="Sans", fontSize=6.4, leading=8.4, textColor=COL["muted"]))


def rgba(hex_color: str, alpha: float):
    c = colors.HexColor(hex_color)
    return colors.Color(c.red, c.green, c.blue, alpha=alpha)


def para(c, text, style, x, y, w, h=900):
    q = Paragraph(text, style)
    _, th = q.wrap(w, h)
    q.drawOn(c, x, y - th)
    return y - th


def bg(c, dark=False):
    c.setFillColor(COL["night"] if dark else COL["ivory"])
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.saveState()
    c.setStrokeColor(rgba("#D8C38A", .12 if dark else .18))
    c.setLineWidth(.32)
    cx, cy = W/2, H/2 + 8*mm
    for r in (23, 45, 69, 96):
        c.circle(cx, cy, r*mm, stroke=1, fill=0)
    for a in range(0, 180, 30):
        rad = math.radians(a)
        c.line(cx-math.cos(rad)*128*mm, cy-math.sin(rad)*128*mm, cx+math.cos(rad)*128*mm, cy+math.sin(rad)*128*mm)
    c.restoreState()


def mark(c, x, y, r, dark=False):
    c.saveState(); c.translate(x, y)
    c.setStrokeColor(COL["gold2"] if dark else COL["gold"]); c.setLineWidth(.9)
    for rr in (r, r*.62, r*.29): c.circle(0, 0, rr, stroke=1, fill=0)
    for a in range(0, 180, 30):
        rad=math.radians(a); c.line(math.cos(rad)*-r, math.sin(rad)*-r, math.cos(rad)*r, math.sin(rad)*r)
    c.restoreState()


def panel(c, x, y, w, h, fill=None, radius=10, stroke=True):
    c.setFillColor(fill or COL["paper"])
    c.setStrokeColor(rgba("#B89A5E", .34))
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke else 0, fill=1)


def label(c, text, x, y, color=None):
    c.setFillColor(color or COL["gold"]); c.setFont("SansBold", 7.15); c.drawString(x, y, text.upper())


def field(c, name, x, y, w, h=10*mm, fill=True):
    if fill:
        c.setFillColor(COL["paper"]); c.setStrokeColor(rgba("#B89A5E", .48)); c.roundRect(x, y, w, h, 3.5, fill=1, stroke=1)
    try:
        c.acroForm.textfieldRelative(name=name, x=x+1.7*mm, y=y+1.3*mm, width=w-3.4*mm, height=h-2.6*mm, borderWidth=0, fillColor=colors.transparent, textColor=COL["ink"], fontName="Sans", fontSize=7.5, forceBorder=False)
    except Exception:
        pass


def checkbox(c, name, x, y, text):
    c.setFillColor(COL["paper"]); c.setStrokeColor(COL["gold"]); c.roundRect(x, y, 4.1*mm, 4.1*mm, 1, fill=1, stroke=1)
    try:
        c.acroForm.checkboxRelative(name=name, x=x, y=y, size=4.1*mm, buttonStyle="check", borderWidth=.5, borderColor=COL["gold"], fillColor=colors.transparent, textColor=COL["violet_dark"], forceBorder=True)
    except Exception:
        pass
    c.setFillColor(COL["ink"]); c.setFont("Sans", 7.2); c.drawString(x+5.8*mm, y+.6*mm, text)


def footer(c, page, title):
    c.setStrokeColor(rgba("#B89A5E", .38)); c.line(18*mm, 15*mm, W-18*mm, 15*mm)
    c.setFont("Sans", 6.7); c.setFillColor(COL["muted"])
    c.drawString(18*mm, 9.4*mm, "SPHAERA · WOCHENKREIS JOURNAL")
    c.drawRightString(W-18*mm, 9.4*mm, f"{page:02d} · {title}")


def page_head(c, page, kicker, title, lead):
    bg(c); footer(c, page, kicker)
    label(c, kicker, 18*mm, 273*mm)
    para(c, title, styles["H1"], 18*mm, 260*mm, W-36*mm)
    para(c, lead, styles["Body"], 18*mm, 238*mm, W-36*mm)


def cover(c):
    bg(c, dark=True)
    c.setFillColor(rgba("#8067C8", .22)); c.circle(70*mm, 235*mm, 60*mm, fill=1, stroke=0)
    c.setFillColor(rgba("#D8C38A", .14)); c.circle(169*mm, 74*mm, 70*mm, fill=1, stroke=0)
    c.setFillColor(COL["gold2"]); c.setFont("SansBold", 8.7); c.drawCentredString(W/2, 263*mm, "SPHAERA · WOCHENKREIS JOURNAL · PROTOTYP 0.3")
    mark(c, W/2, 207*mm, 48*mm, True)
    para(c, "Wochenkreis<br/>Journal", styles["Cover"], 28*mm, 154*mm, W-56*mm)
    para(c, "Ein wöchentliches Operating‑Room‑System für Fokus, Energie, Grenzen, Rituale und Entscheidungen. Die Praxis nach dem kostenlosen Kompass.", styles["CoverSub"], 35*mm, 100*mm, W-70*mm)
    c.setFont("Sans", 7.5); c.setFillColor(COL["gold2"]); c.drawCentredString(W/2, 22*mm, "sphaera.app · Version 0.3 · Review-Prototyp")
    c.showPage()


def two_column_boxes(c, items, start_y=170, box_h=54, gap=10):
    for i, (title, hint, name) in enumerate(items):
        col = i % 2; row = i // 2
        x = (18 + col*91)*mm
        y = (start_y - row*(box_h+gap))*mm
        panel(c, x, y, 82*mm, box_h*mm, colors.white, 12)
        label(c, title, x+7*mm, y+(box_h-13)*mm)
        para(c, hint, styles["Small"], x+7*mm, y+(box_h-21)*mm, 68*mm)
        field(c, name, x+7*mm, y+8*mm, 68*mm, 15*mm)


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
    c.setTitle("SPHAERA Wochenkreis Journal — Prototyp 0.3")
    c.setAuthor("SPHAERA")
    c.setSubject("Wöchentliches Planungssystem für Fokus, Energie, Grenzen, Rituale und Review")
    c.setKeywords("SPHAERA, Wochenkreis Journal, Wochenplanung, Energieplanung, Ritual, Low Ticket")

    cover(c)

    page_head(c, 1, "Methode", "Nicht beobachten. Entwerfen.", "Der kostenlose Kompass sammelt Signale. Dieses Journal baut daraus eine Woche. Es ist kein zweites Reflexionsheft, sondern ein ruhiges System für Auswahl, Platzierung und Wiederkehr.")
    for x, n, title, body in [(18,"1","Architektur","Die Woche bekommt Thema, Grenze und Priorität."),(76,"2","Kapazität","Energie wird budgetiert, nicht romantisiert."),(134,"3","Transfer","Der Review erzeugt eine Entscheidung für die nächste Woche.")]:
        panel(c, x*mm, 166*mm, 52*mm, 48*mm, COL["cream"], 12)
        c.setFillColor(COL["gold"]); c.setFont("SerifBold", 22); c.drawString((x+6)*mm, 197*mm, n)
        c.setFillColor(COL["ink"]); c.setFont("SansBold", 8.2); c.drawString((x+6)*mm, 187*mm, title)
        para(c, body, styles["Small"], (x+6)*mm, 178*mm, 40*mm)
    panel(c, 18*mm, 70*mm, W-36*mm, 58*mm, colors.white, 14)
    para(c, "Arbeitsversprechen", styles["H2"], 28*mm, 115*mm, W-56*mm)
    para(c, "Ich plane diese Woche nicht, um mehr in sie hineinzudrücken. Ich plane, damit das Wesentliche einen geschützten Ort bekommt.", styles["Quote"], 31*mm, 101*mm, W-62*mm)
    field(c, "v03_versprechen", 28*mm, 80*mm, W-56*mm, 10*mm)
    c.showPage()

    page_head(c, 2, "Kommandoraum", "Wochenarchitektur", "Bevor Aufgaben verteilt werden, wird die Woche entworfen: Thema, Ergebnis, Grenzen, Nicht‑Tun und eine klare Definition von genug.")
    two_column_boxes(c, [
        ("Wochenthema", "Der rote Faden, an dem du Entscheidungen prüfst.", "v03_arch_theme"),
        ("Hauptgewinn", "Was soll am Ende wirklich klarer, leichter oder erledigt sein?", "v03_arch_win"),
        ("Nicht‑Tun", "Was wird bewusst nicht begonnen, diskutiert oder perfektioniert?", "v03_arch_not"),
        ("Schutzgrenze", "Welche Grenze verhindert, dass die Woche ausläuft?", "v03_arch_boundary"),
    ], 164, 55, 12)
    panel(c, 18*mm, 34*mm, W-36*mm, 39*mm, COL["cream"], 12)
    para(c, "Genug ist diese Woche …", styles["H2"], 28*mm, 62*mm, W-56*mm); field(c, "v03_arch_enough", 28*mm, 42*mm, W-56*mm, 11*mm)
    c.showPage()

    page_head(c, 3, "Rollen", "Lebensbereiche bewusst verteilen", "Ein gutes Wochensystem verhindert, dass nur der lauteste Lebensbereich gewinnt. Jeder Bereich bekommt eine bewusste Entscheidung: Raum, Minimum oder Grenze.")
    areas=["Körper / Energie","Beziehung / Familie","Arbeit / Projekt","Haushalt / Ordnung","Kreativität / Lernen","Stille / Ritual"]
    y=208*mm
    for i,a in enumerate(areas):
        panel(c, 18*mm, y-17*mm, W-36*mm, 14*mm, colors.white, 7)
        c.setFont("SansBold", 7.6); c.setFillColor(COL["ink"]); c.drawString(25*mm, y-8*mm, a)
        field(c, f"v03_area_space_{i}", 72*mm, y-15*mm, 42*mm, 8.5*mm)
        field(c, f"v03_area_min_{i}", 120*mm, y-15*mm, 31*mm, 8.5*mm)
        field(c, f"v03_area_bound_{i}", 157*mm, y-15*mm, 32*mm, 8.5*mm)
        y-=23*mm
    label(c, "Raum", 74*mm, 215*mm); label(c, "Minimum", 121*mm, 215*mm); label(c, "Grenze", 158*mm, 215*mm)
    panel(c, 18*mm, 39*mm, W-36*mm, 33*mm, COL["cream"], 12)
    para(c, "Priorität des Schutzes", styles["H2"], 28*mm, 63*mm, W-56*mm); field(c, "v03_area_priority", 28*mm, 45*mm, W-56*mm, 10*mm)
    c.showPage()

    page_head(c, 4, "Kapazität", "Energie‑Budget", "Plane mit realer Kapazität. Nicht alle Aufgaben brauchen dieselbe Energie; nicht jede Energie ist jeden Tag verfügbar.")
    two_column_boxes(c, [
        ("Tiefenenergie", "Denken, Schreiben, Bauen, Entscheiden. Maximal wenige Slots.", "v03_energy_deep"),
        ("Pflegeenergie", "Antworten, Sortieren, Admin, Nachziehen.", "v03_energy_care"),
        ("Körperenergie", "Bewegen, Vorbereiten, Räume ordnen, Wege erledigen.", "v03_energy_body"),
        ("Integrationsenergie", "Schlafen, verarbeiten, nichts erzwingen, still werden.", "v03_energy_rest"),
    ], 164, 56, 12)
    panel(c, 18*mm, 34*mm, W-36*mm, 38*mm, COL["cream"], 12)
    para(c, "Überlastungsregel: Wenn die Woche kippt, wird zuerst verkleinert …", styles["H2"], 28*mm, 62*mm, W-56*mm); field(c, "v03_energy_reduce", 28*mm, 42*mm, W-56*mm, 11*mm)
    c.showPage()

    page_head(c, 5, "Fokus", "Entscheidungsboard", "Diese Seite trennt wesentlich von möglich. Sie macht sichtbar, was wirklich passieren muss — und was losgelassen werden darf, ohne die Woche zu verlieren.")
    two_column_boxes(c, [
        ("Must happen", "Ohne das fühlt sich die Woche unfertig oder unruhig an.", "v03_decide_must"),
        ("Nice if possible", "Wertvoll, aber nicht tragend.", "v03_decide_nice"),
        ("Delegate / Ask", "Was muss nicht allein gehalten werden?", "v03_decide_ask"),
        ("Drop / Defer", "Was darf sichtbar später werden?", "v03_decide_drop"),
    ], 164, 56, 12)
    panel(c, 18*mm, 34*mm, W-36*mm, 38*mm, COL["cream"], 12)
    para(c, "Eine Entscheidung, die diese Woche leichter macht", styles["H2"], 28*mm, 62*mm, W-56*mm); field(c, "v03_decide_one", 28*mm, 42*mm, W-56*mm, 11*mm)
    c.showPage()

    page_head(c, 6, "Kreis", "Wochenkreis & Platzierung", "Jetzt wird die Woche sichtbar. Jeder Tag bekommt eine Qualität, einen Hauptslot, eine Grenze und ein kleines Ritual. Das ist die Brücke von Erkenntnis zu Umsetzung.")
    cx, cy, r = W/2, 155*mm, 50*mm
    c.setStrokeColor(COL["gold"]); c.setLineWidth(1.2); c.circle(cx, cy, r, stroke=1, fill=0)
    for i, d in enumerate(["Mo","Di","Mi","Do","Fr","Sa","So"]):
        a=math.radians(90-i*360/7); c.setStrokeColor(rgba("#B89A5E", .50)); c.line(cx, cy, cx+math.cos(a)*r, cy+math.sin(a)*r)
        c.setFillColor(COL["ink"]); c.setFont("SansBold", 7.2); c.drawCentredString(cx+math.cos(a-.43)*r*.78, cy+math.sin(a-.43)*r*.78, d)
    field(c, "v03_circle_center", cx-27*mm, cy-7*mm, 54*mm, 14*mm)
    label(c, "Mitte der Woche", cx-18*mm, cy+14*mm)
    for x,y,title,name in [(18,47,"Zwei leichte Tage","light"),(109,47,"Ein geschützter Tiefenslot","deep")]:
        panel(c,x*mm,y*mm,82*mm,35*mm,colors.white,10); label(c,title,(x+7)*mm,(y+22)*mm); field(c,f"v03_circle_{name}",(x+7)*mm,(y+7)*mm,68*mm,10*mm)
    c.showPage()

    for page_no, title, days in [(7, "Tage platzieren I", ["Montag","Dienstag","Mittwoch","Donnerstag"]), (8, "Tage platzieren II", ["Freitag","Samstag","Sonntag","Puffer / Leerstelle"] )]:
        page_head(c, page_no, "Platzierung", title, "Nicht jeder Tag muss alles tragen. Trage nur die stärkste Qualität ein: Hauptslot, Grenze, Ritual und Mindestversion.")
        y=203*mm
        for i,d in enumerate(days):
            panel(c,18*mm,y-32*mm,W-36*mm,29*mm,colors.white,10)
            c.setFillColor(COL["gold"]); c.setFont("SansBold",7.8); c.drawString(25*mm,y-11*mm,d)
            label(c,"Hauptslot",55*mm,y-8*mm); field(c,f"v03_day_{page_no}_{i}_slot",55*mm,y-24*mm,36*mm,9*mm)
            label(c,"Grenze",96*mm,y-8*mm); field(c,f"v03_day_{page_no}_{i}_bound",96*mm,y-24*mm,35*mm,9*mm)
            label(c,"Ritual",136*mm,y-8*mm); field(c,f"v03_day_{page_no}_{i}_ritual",136*mm,y-24*mm,53*mm,9*mm)
            y-=41*mm
        panel(c,18*mm,33*mm,W-36*mm,28*mm,COL["cream"],11)
        para(c,"Mindestversion, falls die Woche kippt",styles["H2"],28*mm,53*mm,W-56*mm); field(c,f"v03_day_{page_no}_minimum",28*mm,38*mm,W-56*mm,9*mm)
        c.showPage()

    page_head(c, 9, "Reibung", "Wenn‑dann‑Design", "Gute Planung kennt Hindernisse, bevor sie kommen. Diese Sätze senken Reibung, weil du im schwierigen Moment nicht neu verhandeln musst.")
    rows=[("Wenn ich zu wenig Energie habe …","dann mache ich die Mindestversion:"),("Wenn ein Tag kippt …","dann rette ich nur:"),("Wenn ich prokrastiniere …","dann starte ich mit 5 Minuten:"),("Wenn andere mehr wollen …","dann lautet meine Grenze:"),("Wenn ich perfektioniere …","dann ist fertig genug bei:")]
    y=207*mm
    for i,(a,b) in enumerate(rows):
        label(c,a,18*mm,y); field(c,f"v03_if_{i}",18*mm,y-17*mm,76*mm,10*mm)
        label(c,b,103*mm,y); field(c,f"v03_then_{i}",103*mm,y-17*mm,89*mm,10*mm)
        y-=34*mm
    c.showPage()

    page_head(c, 10, "Grenzen", "Kommunikation & Schutz", "Viele Wochen scheitern nicht am Plan, sondern an ungeklärten Außenkanten. Diese Seite macht Grenzen formulierbar, bevor sie emotional werden.")
    two_column_boxes(c, [
        ("Nein‑Satz", "Ein freundlicher Satz, der keine lange Rechtfertigung braucht.", "v03_comm_no"),
        ("Bitte‑Satz", "Was du aktiv erfragen oder delegieren darfst.", "v03_comm_ask"),
        ("Antwortfenster", "Wann du Nachrichten beantwortest — und wann nicht.", "v03_comm_window"),
        ("Abschlusszeichen", "Woran dein Körper merkt: Arbeit ist für heute zu Ende.", "v03_comm_end"),
    ], 164, 56, 12)
    c.showPage()

    page_head(c, 11, "Ritual", "Ritual‑Engine", "Rituale sind hier keine Deko. Sie sind kleine Anker, die die Woche wieder in Form bringen, wenn sie zerfasert.")
    two_column_boxes(c, [
        ("Wochenstart", "Wie betrittst du die Woche bewusst?", "v03_rit_start"),
        ("Übergang", "Wie wechselst du zwischen Rollen oder Räumen?", "v03_rit_transition"),
        ("Schutz", "Welche Handlung beendet Arbeit wirklich?", "v03_rit_protect"),
        ("Review", "Wann und wie liest du die Woche?", "v03_rit_review"),
    ], 164, 56, 12)
    panel(c,18*mm,34*mm,W-36*mm,37*mm,COL["cream"],12)
    para(c,"Kleinste tägliche Wiederholung",styles["H2"],28*mm,61*mm,W-56*mm); field(c,"v03_rit_small",28*mm,42*mm,W-56*mm,10*mm)
    c.showPage()

    page_head(c, 12, "Mitte", "Wochenmitte Reset", "Zur Wochenmitte wird nicht bewertet, sondern nachjustiert. Das Journal darf lebendig bleiben: kleiner, klarer, geschützter.")
    for title,hint,name,y in [("Was bleibt wesentlich?","Nur die echte Mitte, nicht die lauten Ränder.","essential",205),("Was wird ab jetzt kleiner?","Aufgabe, Anspruch, Gespräch oder Perfektion.","smaller",165),("Welche Grenze wird aktiviert?","Eine konkrete Handlung, kein Wunsch.","boundary",125),("Was bekommt unerwartet Raum?","Weil die Woche etwas Neues gezeigt hat.","new",85)]:
        label(c,title,18*mm,y*mm); para(c,hint,styles["Small"],18*mm,(y-5)*mm,W-36*mm); field(c,f"v03_mid_{name}",18*mm,(y-24)*mm,W-36*mm,12*mm)
    c.showPage()

    page_head(c, 13, "Review", "Wochenreview Matrix", "Der Review fragt nicht: War ich gut? Er fragt: Was hat als Design funktioniert — und was wird nächste Woche anders gebaut?")
    two_column_boxes(c, [
        ("Behalten", "Was hat messbar getragen?", "v03_rev_keep"),
        ("Verändern", "Was war richtig, aber falsch platziert?", "v03_rev_change"),
        ("Loslassen", "Was hat mehr Energie genommen als Wert gebracht?", "v03_rev_release"),
        ("Verstärken", "Welches kleine Ritual darf wachsen?", "v03_rev_amplify"),
    ], 164, 56, 12)
    panel(c,18*mm,34*mm,W-36*mm,38*mm,COL["cream"],12)
    para(c,"Entscheidung für nächste Woche",styles["H2"],28*mm,62*mm,W-56*mm); field(c,"v03_rev_next",28*mm,42*mm,W-56*mm,11*mm)
    c.showPage()

    page_head(c, 14, "Transfer", "Nächste Woche vorbereiten", "Der Wert des Journals entsteht durch Wiederkehr. Übertrage nur, was wirklich gelernt wurde — nicht alles, was unerledigt blieb.")
    two_column_boxes(c, [
        ("Wiederholen", "Was soll bewusst zurückkehren?", "v03_transfer_repeat"),
        ("Vereinfachen", "Was bekommt eine kleinere Version?", "v03_transfer_simple"),
        ("Früher platzieren", "Was braucht einen besseren Zeitpunkt?", "v03_transfer_earlier"),
        ("Nicht mehr tragen", "Was verlässt den Kreis?", "v03_transfer_drop"),
    ], 164, 56, 12)
    panel(c,18*mm,34*mm,W-36*mm,38*mm,COL["cream"],12)
    para(c,"Nächste Woche beginnt mit …",styles["H2"],28*mm,62*mm,W-56*mm); field(c,"v03_transfer_start",28*mm,42*mm,W-56*mm,11*mm)
    c.showPage()

    page_head(c, 15, "App‑Brücke", "Was diese Seiten für SPHAERA testen", "Der Prototyp testet nicht nur ein PDF, sondern App‑Logik: Welche Planungsfragen werden jede Woche wirklich benutzt? Welche Felder sind zu viel? Welche Struktur macht ruhiger?")
    for i,(title,body) in enumerate([("Wenn eine Seite trägt", "wird sie als späteres App‑Modul gedacht."),("Wenn eine Seite nervt", "wird sie gestrichen oder radikal vereinfacht."),("Wenn du zurückkommst", "ist SPHAERA auf dem richtigen Weg."),("Wenn du bezahlst", "dann nicht für mehr Seiten, sondern für bessere Wochenklarheit.")]):
        y=(180-i*36)*mm; panel(c,24*mm,y,W-48*mm,25*mm,colors.white if i!=3 else COL["cream"],10); para(c,title,styles["H2"],34*mm,y+18*mm,W-68*mm); para(c,body,styles["Small"],34*mm,y+8*mm,W-68*mm)
    p_y=40*mm
    para(c,"Reviewfrage: Welche drei Seiten würdest du wirklich jede Woche öffnen?",styles["Quote"],31*mm,p_y+20*mm,W-62*mm)
    field(c,"v03_app_feedback",31*mm,p_y,W-62*mm,11*mm)
    c.showPage()

    bg(c, dark=True)
    mark(c, W/2, 205*mm, 47*mm, True)
    para(c, "Eine Woche ist ein System.", styles["Cover"], 28*mm, 154*mm, W-56*mm)
    para(c, "Der Kompass zeigt Muster. Das Wochenkreis Journal baut daraus eine wiederholbare Praxis: entscheiden, platzieren, schützen, wiederkehren.", styles["CoverSub"], 35*mm, 99*mm, W-70*mm)
    c.setFillColor(COL["gold2"]); c.setFont("Sans", 7.4); c.drawCentredString(W/2, 22*mm, "Prototyp 0.3 · sphaera.app")
    c.showPage()

    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
