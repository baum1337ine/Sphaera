#!/usr/bin/env python3
"""Build SPHAERA Wochenkreis Journal prototype PDF v0.4.

Design rule for v0.4:
- no Freebie reference
- no App reference
- quiet premium workbook
- consistent page grid, margins, panel sizes, and typography
"""
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

M = 18 * mm
CONTENT_W = W - 2 * M

COL = {
    "night": colors.HexColor("#070912"),
    "deep": colors.HexColor("#17101D"),
    "violet": colors.HexColor("#7560B8"),
    "ivory": colors.HexColor("#FBF6EA"),
    "cream": colors.HexColor("#F3E7D6"),
    "paper": colors.HexColor("#FFFDF8"),
    "gold": colors.HexColor("#B89A5E"),
    "gold2": colors.HexColor("#D8C38A"),
    "ink": colors.HexColor("#211817"),
    "muted": colors.HexColor("#62575E"),
    "line": colors.HexColor("#D8C89D"),
}

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("Serif", str(FONT_DIR / "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("SerifBold", str(FONT_DIR / "DejaVuSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sans", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("SansBold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Cover", fontName="SerifBold", fontSize=34, leading=38, alignment=TA_CENTER, textColor=COL["ivory"]))
styles.add(ParagraphStyle("CoverSub", fontName="Sans", fontSize=10.2, leading=15.3, alignment=TA_CENTER, textColor=COL["cream"]))
styles.add(ParagraphStyle("H1", fontName="SerifBold", fontSize=21, leading=25, textColor=COL["ink"]))
styles.add(ParagraphStyle("H2", fontName="SerifBold", fontSize=12.8, leading=15.5, textColor=COL["ink"]))
styles.add(ParagraphStyle("Body", fontName="Sans", fontSize=8.6, leading=12.2, textColor=COL["ink"]))
styles.add(ParagraphStyle("Small", fontName="Sans", fontSize=7.1, leading=9.4, textColor=COL["muted"]))
styles.add(ParagraphStyle("Quote", fontName="Serif", fontSize=12.2, leading=16.7, alignment=TA_CENTER, textColor=COL["ink"]))


def rgba(hex_color: str, alpha: float):
    base = colors.HexColor(hex_color)
    return colors.Color(base.red, base.green, base.blue, alpha=alpha)


def para(c, text, style, x, y, w, h=900):
    p = Paragraph(text, style)
    _, th = p.wrap(w, h)
    p.drawOn(c, x, y - th)
    return y - th


def bg(c, dark=False):
    c.setFillColor(COL["night"] if dark else COL["ivory"])
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.saveState()
    c.setStrokeColor(rgba("#D8C38A", .11 if dark else .13))
    c.setLineWidth(.25)
    cx, cy = W/2, H/2 + 5*mm
    for r in (26, 51, 77, 103):
        c.circle(cx, cy, r*mm, stroke=1, fill=0)
    for a in range(0, 180, 30):
        rad = math.radians(a)
        c.line(cx - math.cos(rad)*123*mm, cy - math.sin(rad)*123*mm, cx + math.cos(rad)*123*mm, cy + math.sin(rad)*123*mm)
    c.restoreState()


def mark(c, x, y, r, dark=False):
    c.saveState(); c.translate(x, y)
    c.setStrokeColor(COL["gold2"] if dark else COL["gold"])
    c.setLineWidth(.9)
    for rr in (r, r*.62, r*.29):
        c.circle(0, 0, rr, stroke=1, fill=0)
    for a in range(0, 180, 30):
        rad = math.radians(a)
        c.line(math.cos(rad)*-r, math.sin(rad)*-r, math.cos(rad)*r, math.sin(rad)*r)
    c.restoreState()


def panel(c, x, y, w, h, fill=None, radius=9, stroke=True):
    c.setFillColor(fill or COL["paper"])
    c.setStrokeColor(rgba("#B89A5E", .36))
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke else 0, fill=1)


def label(c, text, x, y, color=None):
    c.setFillColor(color or COL["gold"])
    c.setFont("SansBold", 6.85)
    c.drawString(x, y, text.upper())


def rule(c, x, y, w):
    c.setStrokeColor(rgba("#B89A5E", .40))
    c.setLineWidth(.45)
    c.line(x, y, x+w, y)


def field(c, name, x, y, w, h=9*mm):
    c.setFillColor(COL["paper"])
    c.setStrokeColor(rgba("#B89A5E", .48))
    c.roundRect(x, y, w, h, 3, fill=1, stroke=1)
    try:
        c.acroForm.textfieldRelative(
            name=name,
            x=x+1.6*mm,
            y=y+1.2*mm,
            width=w-3.2*mm,
            height=h-2.4*mm,
            borderWidth=0,
            fillColor=colors.transparent,
            textColor=COL["ink"],
            fontName="Sans",
            fontSize=7.2,
            forceBorder=False,
        )
    except Exception:
        pass


def footer(c, page, title):
    rule(c, M, 15*mm, CONTENT_W)
    c.setFont("Sans", 6.5)
    c.setFillColor(COL["muted"])
    c.drawString(M, 9.2*mm, "SPHAERA · WOCHENKREIS JOURNAL")
    c.drawRightString(W-M, 9.2*mm, f"{page:02d} · {title}")


def page_head(c, page, kicker, title, lead):
    bg(c)
    footer(c, page, kicker)
    label(c, kicker, M, 273*mm)
    para(c, title, styles["H1"], M, 260*mm, CONTENT_W)
    y = para(c, lead, styles["Body"], M, 238*mm, CONTENT_W)
    rule(c, M, y-8*mm, CONTENT_W)


def cover(c):
    bg(c, dark=True)
    c.setFillColor(rgba("#7560B8", .20)); c.circle(70*mm, 235*mm, 58*mm, fill=1, stroke=0)
    c.setFillColor(rgba("#D8C38A", .12)); c.circle(170*mm, 72*mm, 68*mm, fill=1, stroke=0)
    c.setFillColor(COL["gold2"]); c.setFont("SansBold", 8.5); c.drawCentredString(W/2, 263*mm, "SPHAERA · WOCHENKREIS JOURNAL · PROTOTYP 0.4")
    mark(c, W/2, 207*mm, 48*mm, True)
    para(c, "Wochenkreis<br/>Journal", styles["Cover"], 28*mm, 154*mm, W-56*mm)
    para(c, "Ein edles Wochenritual für Fokus, Energie, Grenzen und wiederkehrende Klarheit.", styles["CoverSub"], 39*mm, 101*mm, W-78*mm)
    c.setFont("Sans", 7.3); c.setFillColor(COL["gold2"]); c.drawCentredString(W/2, 22*mm, "Edition zur Review · SPHAERA")
    c.showPage()


def closing(c):
    bg(c, dark=True)
    mark(c, W/2, 204*mm, 47*mm, True)
    para(c, "Klarheit entsteht durch Wiederkehr.", styles["Cover"], 26*mm, 153*mm, W-52*mm)
    para(c, "Eine gute Woche ist nicht voller. Sie ist besser geordnet: mit geschützter Energie, klaren Grenzen und einer Mitte, zu der du zurückkehren kannst.", styles["CoverSub"], 37*mm, 95*mm, W-74*mm)
    c.setFillColor(COL["gold2"]); c.setFont("Sans", 7.2); c.drawCentredString(W/2, 22*mm, "SPHAERA · Wochenkreis Journal · Prototyp 0.4")
    c.showPage()


def box_grid(c, items, top=176, box_h=52, gap=12):
    for i, (title, hint, name) in enumerate(items):
        col = i % 2
        row = i // 2
        x = (18 + col*91)*mm
        y = (top - row*(box_h+gap))*mm
        panel(c, x, y, 82*mm, box_h*mm, colors.white, 11)
        label(c, title, x+7*mm, y+(box_h-13)*mm)
        para(c, hint, styles["Small"], x+7*mm, y+(box_h-21)*mm, 68*mm)
        field(c, name, x+7*mm, y+8*mm, 68*mm, 14*mm)


def full_prompt(c, title, hint, name, y, h=28):
    panel(c, M, y*mm, CONTENT_W, h*mm, colors.white, 10)
    label(c, title, M+8*mm, (y+h-11)*mm)
    para(c, hint, styles["Small"], M+8*mm, (y+h-19)*mm, CONTENT_W-16*mm)
    field(c, name, M+8*mm, (y+6)*mm, CONTENT_W-16*mm, 9*mm)


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
    c.setTitle("SPHAERA Wochenkreis Journal — Prototyp 0.4")
    c.setAuthor("SPHAERA")
    c.setSubject("Edles Wochenjournal für Fokus, Energie, Grenzen und wiederkehrende Klarheit")
    c.setKeywords("SPHAERA, Wochenkreis Journal, Wochenplanung, Energieplanung, Ritual, PDF")

    cover(c)

    page_head(c, 1, "Orientierung", "Die Woche als Kreis", "Dieses Journal behandelt die Woche nicht als lineare Liste, sondern als geordneten Kreis: Ausrichtung, Platzierung, Schutz, Ritual und Review. Jede Seite dient einer konkreten Entscheidung.")
    box_grid(c, [
        ("Ausrichtung", "Was ist die Mitte dieser Woche?", "v04_meth_align"),
        ("Kapazität", "Welche Energie steht realistisch zur Verfügung?", "v04_meth_capacity"),
        ("Schutz", "Welche Grenze hält die Woche in Form?", "v04_meth_protect"),
        ("Wiederkehr", "Welches Ritual bringt dich zurück?", "v04_meth_return"),
    ], top=164, box_h=52, gap=13)
    full_prompt(c, "Leitsatz", "Ein Satz, der die Woche zusammenhält.", "v04_meth_sentence", 35, 30)
    c.showPage()

    page_head(c, 2, "Architektur", "Wochenarchitektur", "Bevor Termine und Aufgaben ihren Platz bekommen, braucht die Woche eine innere Ordnung: Thema, Ergebnis, Grenze und eine bewusste Form von genug.")
    box_grid(c, [
        ("Wochenthema", "Der rote Faden für alle Entscheidungen.", "v04_arch_theme"),
        ("Wesentliches Ergebnis", "Was soll am Ende wirklich klarer, leichter oder erledigt sein?", "v04_arch_result"),
        ("Nicht verhandelbar", "Was darf diese Woche nicht verloren gehen?", "v04_arch_nonneg"),
        ("Nicht‑Tun", "Was wird bewusst nicht begonnen oder perfektioniert?", "v04_arch_not"),
    ], top=164, box_h=52, gap=13)
    full_prompt(c, "Genug ist erreicht, wenn …", "Definiere ein ruhiges Ende, bevor die Woche beginnt.", "v04_arch_enough", 35, 30)
    c.showPage()

    page_head(c, 3, "Lebensbereiche", "Rollen & Räume", "Eine edle Woche ist nicht nur effizient, sondern geordnet. Diese Seite schützt davor, dass ein einzelner Bereich die ganze Woche übernimmt.")
    label(c, "Bereich", 24*mm, 211*mm); label(c, "Raum", 75*mm, 211*mm); label(c, "Minimum", 118*mm, 211*mm); label(c, "Grenze", 157*mm, 211*mm)
    y = 193*mm
    for i, area in enumerate(["Körper / Energie", "Beziehung / Familie", "Arbeit / Projekt", "Haushalt / Ordnung", "Kreativität / Lernen", "Stille / Ritual"]):
        panel(c, M, y-7*mm, CONTENT_W, 14*mm, colors.white, 7)
        c.setFont("SansBold", 7.4); c.setFillColor(COL["ink"]); c.drawString(25*mm, y*mm, area)
        field(c, f"v04_area_room_{i}", 72*mm, y-5*mm, 36*mm, 8.2*mm)
        field(c, f"v04_area_min_{i}", 114*mm, y-5*mm, 36*mm, 8.2*mm)
        field(c, f"v04_area_bound_{i}", 156*mm, y-5*mm, 33*mm, 8.2*mm)
        y -= 24*mm
    full_prompt(c, "Schutzpriorität", "Welcher Bereich braucht diese Woche bewusst mehr Raum oder Grenze?", "v04_area_priority", 34, 30)
    c.showPage()

    page_head(c, 4, "Energie", "Energiehaushalt", "Energie wird nicht vorausgesetzt, sondern verteilt. Diese Seite verhindert, dass Tiefenarbeit, Pflegeaufgaben und Regeneration denselben inneren Preis bekommen.")
    box_grid(c, [
        ("Tiefenenergie", "Denken, Schreiben, Bauen, Entscheiden.", "v04_energy_deep"),
        ("Pflegeenergie", "Antworten, Sortieren, Admin, Nachziehen.", "v04_energy_care"),
        ("Körperenergie", "Bewegen, Vorbereiten, Aufräumen, Wege.", "v04_energy_body"),
        ("Integrationsenergie", "Schlaf, Stille, Verarbeitung, Leerlauf.", "v04_energy_rest"),
    ], top=164, box_h=53, gap=13)
    full_prompt(c, "Überlastungsregel", "Wenn es zu viel wird, wird zuerst verkleinert …", "v04_energy_rule", 34, 30)
    c.showPage()

    page_head(c, 5, "Entscheidung", "Prioritäten‑Matrix", "Diese Seite trennt wesentlich von möglich. Nicht alles, was sinnvoll ist, gehört in diese Woche.")
    box_grid(c, [
        ("Muss geschehen", "Tragend für Ruhe, Fortschritt oder Verlässlichkeit.", "v04_prio_must"),
        ("Darf geschehen", "Schön, wertvoll, aber nicht tragend.", "v04_prio_may"),
        ("Bitten / Delegieren", "Was muss nicht allein gehalten werden?", "v04_prio_ask"),
        ("Verschieben / Streichen", "Was verlässt diese Woche bewusst?", "v04_prio_drop"),
    ], top=164, box_h=53, gap=13)
    full_prompt(c, "Eine klärende Entscheidung", "Welche Entscheidung macht die ganze Woche leichter?", "v04_prio_one", 34, 30)
    c.showPage()

    page_head(c, 6, "Wochenkreis", "Mitte & Tagesqualitäten", "Der Kreis macht sichtbar, was eine Liste oft verbirgt: Übergänge, leichte Tage, geschützte Slots und die Mitte, zu der du zurückkehrst.")
    cx, cy, r = W/2, 154*mm, 50*mm
    c.setStrokeColor(COL["gold"]); c.setLineWidth(1.1); c.circle(cx, cy, r, stroke=1, fill=0)
    for i, d in enumerate(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]):
        a = math.radians(90 - i*360/7)
        c.setStrokeColor(rgba("#B89A5E", .52)); c.line(cx, cy, cx+math.cos(a)*r, cy+math.sin(a)*r)
        c.setFillColor(COL["ink"]); c.setFont("SansBold", 7.2); c.drawCentredString(cx+math.cos(a-.43)*r*.78, cy+math.sin(a-.43)*r*.78, d)
    field(c, "v04_circle_center", cx-27*mm, cy-7*mm, 54*mm, 14*mm)
    label(c, "Mitte", cx-8*mm, cy+14*mm)
    full_prompt(c, "Zwei leichte Tage", "Welche Tage werden bewusst nicht überladen?", "v04_circle_light", 48, 25)
    c.showPage()

    page_head(c, 7, "Platzierung", "Wochenplan", "Jeder Tag bekommt nur vier Angaben: Qualität, Hauptslot, Grenze und Ritual. So bleibt die Woche geordnet, ohne sich zu überplanen.")
    label(c, "Tag", 23*mm, 211*mm); label(c, "Qualität", 43*mm, 211*mm); label(c, "Hauptslot", 82*mm, 211*mm); label(c, "Grenze", 128*mm, 211*mm); label(c, "Ritual", 162*mm, 211*mm)
    y = 193*mm
    for d in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
        panel(c, M, y-7*mm, CONTENT_W, 14*mm, colors.white, 7)
        c.setFont("SansBold", 7.4); c.setFillColor(COL["gold"]); c.drawString(25*mm, y*mm, d)
        field(c, f"v04_plan_{d}_quality", 41*mm, y-5*mm, 34*mm, 8.2*mm)
        field(c, f"v04_plan_{d}_slot", 80*mm, y-5*mm, 42*mm, 8.2*mm)
        field(c, f"v04_plan_{d}_bound", 127*mm, y-5*mm, 29*mm, 8.2*mm)
        field(c, f"v04_plan_{d}_ritual", 161*mm, y-5*mm, 28*mm, 8.2*mm)
        y -= 22*mm
    full_prompt(c, "Puffer / Leerstelle", "Wo bleibt bewusst Raum für das Unerwartete?", "v04_plan_buffer", 34, 29)
    c.showPage()

    page_head(c, 8, "Ritual", "Ritual‑Engine", "Rituale sind keine Dekoration. Sie sind kleine wiederkehrende Handlungen, die Ordnung wiederherstellen, wenn die Woche ihre Form verliert.")
    box_grid(c, [
        ("Wochenstart", "Wie betrittst du die Woche bewusst?", "v04_rit_start"),
        ("Übergang", "Wie wechselst du zwischen Rollen oder Räumen?", "v04_rit_transition"),
        ("Schutz", "Welche Handlung beendet Arbeit wirklich?", "v04_rit_close"),
        ("Review", "Wann und wie liest du die Woche?", "v04_rit_review"),
    ], top=164, box_h=53, gap=13)
    full_prompt(c, "Kleinste Wiederholung", "Welche Handlung ist so klein, dass sie fast immer möglich bleibt?", "v04_rit_small", 34, 30)
    c.showPage()

    page_head(c, 9, "Grenzen", "Kommunikation & Schutz", "Grenzen wirken besser, wenn sie vorformuliert sind. Diese Seite macht Schutz freundlich, präzise und wiederholbar.")
    box_grid(c, [
        ("Nein‑Satz", "Ein ruhiger Satz ohne lange Rechtfertigung.", "v04_comm_no"),
        ("Bitte‑Satz", "Was du aktiv erfragen oder delegieren darfst.", "v04_comm_ask"),
        ("Antwortfenster", "Wann du erreichbar bist — und wann nicht.", "v04_comm_window"),
        ("Abschlusszeichen", "Woran dein Körper merkt: genug für heute.", "v04_comm_end"),
    ], top=164, box_h=53, gap=13)
    full_prompt(c, "Schutzformel", "Ein Satz, der diese Woche deine Energie schützt.", "v04_comm_formula", 34, 30)
    c.showPage()

    page_head(c, 10, "Reibung", "Wenn‑dann‑Design", "Gute Planung kennt Reibung, bevor sie entsteht. Diese Sätze verhindern, dass du im schwierigen Moment neu verhandeln musst.")
    rows = [
        ("Wenn meine Energie niedrig ist …", "dann ist die Mindestversion:"),
        ("Wenn ein Tag kippt …", "dann rette ich nur:"),
        ("Wenn ich aufschiebe …", "dann beginne ich mit:"),
        ("Wenn andere mehr wollen …", "dann antworte ich:"),
        ("Wenn ich perfektioniere …", "dann ist fertig genug bei:"),
    ]
    y = 205*mm
    for i, (a, b) in enumerate(rows):
        label(c, a, M, y); field(c, f"v04_if_{i}", M, y-17*mm, 78*mm, 10*mm)
        label(c, b, 105*mm, y); field(c, f"v04_then_{i}", 105*mm, y-17*mm, 87*mm, 10*mm)
        y -= 34*mm
    c.showPage()

    page_head(c, 11, "Wochenmitte", "Reset & Kalibrierung", "Zur Wochenmitte wird nicht bewertet, sondern neu geordnet. Das Journal bleibt lebendig: kleiner, klarer, geschützter.")
    full_prompt(c, "Was bleibt wesentlich?", "Nur die Mitte, nicht die lauten Ränder.", "v04_mid_essential", 180, 32)
    full_prompt(c, "Was wird kleiner?", "Aufgabe, Anspruch, Gespräch oder Perfektion.", "v04_mid_smaller", 137, 32)
    full_prompt(c, "Welche Grenze wird aktiviert?", "Eine konkrete Handlung, kein Wunsch.", "v04_mid_boundary", 94, 32)
    full_prompt(c, "Was bekommt Raum?", "Weil die Woche etwas Unerwartetes gezeigt hat.", "v04_mid_room", 51, 32)
    c.showPage()

    page_head(c, 12, "Review", "Wochenreview", "Der Review fragt nicht: War ich gut? Er fragt: Was hat als Design funktioniert — und was wird nächste Woche anders gebaut?")
    box_grid(c, [
        ("Behalten", "Was hat getragen und darf wiederkehren?", "v04_rev_keep"),
        ("Verändern", "Was war richtig, aber falsch platziert?", "v04_rev_change"),
        ("Loslassen", "Was kostete mehr Energie als es Wert brachte?", "v04_rev_release"),
        ("Verstärken", "Welches kleine Ritual darf wachsen?", "v04_rev_amplify"),
    ], top=164, box_h=53, gap=13)
    full_prompt(c, "Entscheidung für die nächste Woche", "Eine konkrete Anpassung, nicht nur eine Erkenntnis.", "v04_rev_next", 34, 30)
    c.showPage()

    page_head(c, 13, "Transfer", "Nächste Woche vorbereiten", "Übertrage nur, was wirklich gelernt wurde — nicht alles, was unerledigt blieb. Wiederkehr ist die eigentliche Form von Fortschritt.")
    box_grid(c, [
        ("Wiederholen", "Was soll bewusst zurückkehren?", "v04_trans_repeat"),
        ("Vereinfachen", "Was bekommt eine kleinere, bessere Form?", "v04_trans_simple"),
        ("Früher platzieren", "Was braucht einen besseren Zeitpunkt?", "v04_trans_earlier"),
        ("Nicht mehr tragen", "Was verlässt den Kreis?", "v04_trans_drop"),
    ], top=164, box_h=53, gap=13)
    full_prompt(c, "Nächste Woche beginnt mit …", "Der erste ruhige Schritt.", "v04_trans_start", 34, 30)
    c.showPage()

    page_head(c, 14, "Notizen", "Freier Kreis", "Raum für Skizzen, Sätze, Symbole, Beobachtungen oder eine eigene Wochenkarte.")
    panel(c, M, 39*mm, CONTENT_W, 170*mm, colors.white, 12)
    c.setStrokeColor(rgba("#B89A5E", .22)); c.setLineWidth(.35)
    y = 194*mm
    for _ in range(13):
        c.line(27*mm, y, W-27*mm, y)
        y -= 11*mm
    mark(c, W/2, 124*mm, 28*mm, False)
    c.showPage()

    closing(c)
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
