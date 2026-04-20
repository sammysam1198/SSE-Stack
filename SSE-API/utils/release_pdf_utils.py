import io
import re
from collections import defaultdict

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


def sanitize_name(value: str) -> str:
    value = (value or "release").strip()
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return value[:80] or "release"


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

    return lines + ([current] if current else []) or ["—"]


def draw_label_value(c, label, value, x_label, x_value, y, page_width, font_size=10):
    max_width = page_width - x_value - 0.75 * inch

    c.setFont("Helvetica-Bold", font_size)
    c.drawString(x_label, y, f"{label}:")

    wrapped = wrap_text(value, "Helvetica", font_size, max_width)
    c.setFont("Helvetica", font_size)

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


def build_release_details_pdf_bytes(release: dict) -> tuple[bytes, str]:
    title = release.get("release_title") or "Untitled Release"
    filename = f"{sanitize_name(title)}_details.pdf"

    artists = release.get("artists", [])
    tracks = release.get("tracks", [])
    credits = release.get("track_credits", [])

    credits_by_track = defaultdict(list)
    for credit in credits:
        credits_by_track[credit["release_track_id"]].append(credit)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    page_width, page_height = LETTER

    left = 0.75 * inch
    label_x = left
    value_x = left + 2.2 * inch
    y = page_height - 0.8 * inch

    c.setTitle(f"{title} Release Details")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(left, y, "SpacedOut Studios Release Package")
    y -= 22

    def section(title_text, y_pos):
        c.setFont("Helvetica-Bold", 13)
        c.drawString(left, y_pos, title_text)
        return y_pos - 18

    y = section("Release Details", y)
    for label, key in [
        ("Release Title", "release_title"),
        ("Release Type", "release_type"),
        ("Preferred Release Date", "preferred_release_date"),
        ("Primary Genre", "primary_genre"),
        ("Other Genres", "other_genres"),
        ("Release Pitch", "release_pitch"),
        ("Status", "status"),
    ]:
        y = ensure_page(c, y)
        y = draw_label_value(c, label, release.get(key), label_x, value_x, y, page_width)

    y -= 8
    y = ensure_page(c, y)
    y = section("Artists", y)

    for artist in artists:
        summary = f"{artist.get('display_name') or '—'} ({artist.get('role_type') or '—'})"
        y = ensure_page(c, y)
        y = draw_label_value(c, "Artist", summary, label_x, value_x, y, page_width)
        for label, key in [
            ("Email", "email"),
            ("First Name", "first_name"),
            ("Last Name", "last_name"),
            ("IPI", "ipi"),
            ("PRO", "pro"),
            ("Publisher", "publisher"),
            ("Spotify", "spotify_url"),
            ("Apple Music", "apple_music_url"),
            ("YouTube", "youtube_url"),
            ("SoundCloud", "soundcloud_url"),
            ("Split %", "split_percent"),
        ]:
            y = ensure_page(c, y)
            y = draw_label_value(c, label, artist.get(key), label_x, value_x, y, page_width)
        y -= 6

    y = ensure_page(c, y)
    y = section("Tracks", y)

    for track in tracks:
        heading = f"{track.get('track_number', '—')}. {track.get('track_title', 'Untitled Track')}"
        y = ensure_page(c, y)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left, y, heading)
        y -= 16

        for label, key in [
            ("Artists", "track_artists_text"),
            ("Length", "track_length"),
            ("Language", "language"),
            ("Instrumental", "is_instrumental"),
            ("Lyrics", "lyrics"),
            ("Track Pitch", "track_pitch"),
            ("Audio File", "audio_original_filename"),
        ]:
            y = ensure_page(c, y)
            y = draw_label_value(c, label, track.get(key), label_x, value_x, y, page_width)

        track_credit_rows = credits_by_track.get(track["id"], [])
        if track_credit_rows:
            y = ensure_page(c, y)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left, y, "Credits")
            y -= 14

            for credit in track_credit_rows:
                credit_summary = f"{credit.get('credit_type', 'credit').title()}: {credit.get('artist_name') or ((credit.get('first_name') or '') + ' ' + (credit.get('last_name') or '')).strip() or '—'}"
                y = ensure_page(c, y)
                c.setFont("Helvetica", 10)
                c.drawString(value_x, y, credit_summary)
                y -= 13

        y -= 10

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes, filename