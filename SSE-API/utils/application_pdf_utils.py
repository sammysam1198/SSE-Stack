import re
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_OUTPUT_DIR = BASE_DIR / "application_docs"


def sanitize_name(value: str) -> str:
    value = (value or "Unknown").strip()
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return value[:80] or "Unknown"


def wrap_text(text: str, font_name: str, font_size: int, max_width: float):
    text = str(text or "—").strip()
    if not text:
        return ["—"]

    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else f"{current} {word}"
        if stringWidth(test, font_name, font_size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines or ["—"]


def draw_label_value(c, label, value, x_label, x_value, y, page_width, font_size=10):
    label_font = "Helvetica-Bold"
    value_font = "Helvetica"
    max_width = page_width - x_value - 0.75 * inch

    c.setFont(label_font, font_size)
    c.drawString(x_label, y, f"{label}:")

    wrapped = wrap_text(value, value_font, font_size, max_width)
    c.setFont(value_font, font_size)

    line_y = y
    for i, line in enumerate(wrapped):
        c.drawString(x_value, line_y, line)
        if i < len(wrapped) - 1:
            line_y -= 14

    used_height = max(1, len(wrapped)) * 14
    return y - used_height - 6


def ensure_page(c, y, min_y=0.9 * inch):
    if y < min_y:
        c.showPage()
        c.setFont("Helvetica", 10)
        return 10.5 * inch
    return y


def generate_application_pdf(application: dict) -> str:
    PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    first_name = sanitize_name(application.get("first_name"))
    last_name = sanitize_name(application.get("last_name"))
    app_id = application.get("id", "unknown")

    filename = f"application_{app_id}_{first_name}_{last_name}.pdf"
    file_path = PDF_OUTPUT_DIR / filename

    c = canvas.Canvas(str(file_path), pagesize=LETTER)
    page_width, page_height = LETTER

    left = 0.75 * inch
    label_x = left
    value_x = left + 2.2 * inch
    y = page_height - 0.8 * inch

    c.setTitle(f"{application.get('artist_name', 'Artist')} Application")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(left, y, "SpacedOut Studios Artist Application")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(left, y, f"Application ID: {application.get('id', '—')}")
    y -= 14
    c.drawString(left, y, f"Submitted At: {application.get('created_at', '—')}")
    y -= 14
    c.drawString(left, y, f"Status: {application.get('status', 'pending')}")
    y -= 24

    def section(title, y_pos):
        c.setFont("Helvetica-Bold", 13)
        c.drawString(left, y_pos, title)
        return y_pos - 18

    y = section("Identity", y)
    for label, key in [
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        ("Birthday", "birthday"),
        ("Artist Name", "artist_name"),
        ("Country", "country"),
        ("City", "city"),
        ("State / Province", "state_province"),
        ("Email", "email"),
        ("Phone", "phone"),
    ]:
        y = ensure_page(c, y)
        y = draw_label_value(c, label, application.get(key), label_x, value_x, y, page_width)

    y -= 8
    y = ensure_page(c, y)
    y = section("Professional Info", y)
    for label, key in [
        ("Current Label", "current_label"),
        ("Publisher", "publisher"),
        ("Current Distributor", "current_distributor"),
        ("Total Releases", "total_releases"),
        ("Releases Last 12 Months", "releases_last_12_months"),
        ("Spotify Monthly Listeners", "spotify_monthly_listeners"),
    ]:
        y = ensure_page(c, y)
        y = draw_label_value(c, label, application.get(key), label_x, value_x, y, page_width)

    y -= 8
    y = ensure_page(c, y)
    y = section("Links", y)
    for label, key in [
        ("Streaming Link", "streaming_link"),
        ("Instagram Link", "instagram_link"),
        ("YouTube Link", "youtube_link"),
        ("Bandcamp Link", "bandcamp_link"),
        ("Website Link", "website_link"),
    ]:
        y = ensure_page(c, y)
        y = draw_label_value(c, label, application.get(key), label_x, value_x, y, page_width)

    y -= 8
    y = ensure_page(c, y)
    y = section("Application Questions", y)
    for label, key in [
        ("Why do you want to work with SpacedOut Studios?", "fit"),
        ("What makes your music stand out in your genre?", "standout"),
        ("Strongest skill and weakest leverage point", "strongest_skill_and_leverage"),
        ("Release Schedule", "release_schedule"),
        ("Unreleased Music Ready", "unreleased_music_ready"),
        ("Branding", "branding"),
        ("Goals in 12 Months", "goals_12_months"),
        ("Collaboration Openness", "collaboration_openness"),
        ("How They Heard About Us", "heard_about"),
    ]:
        y = ensure_page(c, y)
        y = draw_label_value(c, label, application.get(key), label_x, value_x, y, page_width)

    y -= 8
    y = ensure_page(c, y)
    y = section("Financial / Operational", y)
    for label, key in [
        ("Bank Account Access", "bank_account_access"),
        ("Bank Account Explanation", "bank_account_explanation"),
        ("Agreement", "agreement"),
    ]:
        y = ensure_page(c, y)
        y = draw_label_value(c, label, application.get(key), label_x, value_x, y, page_width)

    c.save()

    return f"application_docs/{filename}"