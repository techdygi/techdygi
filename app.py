from __future__ import annotations

import pathlib
import uuid
from typing import Any

from flask import Flask, abort, render_template, request, send_from_directory, url_for
import yt_dlp

BASE_DIR = pathlib.Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


def _is_supported_url(url: str) -> bool:
    lowered = url.lower()
    return "instagram.com" in lowered or "facebook.com" in lowered or "fb.watch" in lowered


def _download_media(url: str) -> dict[str, Any]:
    request_id = str(uuid.uuid4())[:8]
    output_template = str(DOWNLOAD_DIR / f"{request_id}.%(ext)s")

    ydl_opts: dict[str, Any] = {
        "outtmpl": output_template,
        "noplaylist": True,
        "format": "bv*+ba/b",
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    entries = info.get("entries") if isinstance(info, dict) else None
    main_info = entries[0] if entries else info

    if not isinstance(main_info, dict):
        raise RuntimeError("Unable to parse media metadata.")

    requested_downloads = main_info.get("requested_downloads") or []
    filepath = None

    if requested_downloads and isinstance(requested_downloads[0], dict):
        filepath = requested_downloads[0].get("filepath")

    if not filepath:
        ext = main_info.get("ext", "mp4")
        fallback = DOWNLOAD_DIR / f"{request_id}.{ext}"
        if fallback.exists():
            filepath = str(fallback)

    if not filepath:
        candidates = sorted(DOWNLOAD_DIR.glob(f"{request_id}.*"))
        if candidates:
            filepath = str(candidates[0])

    if not filepath:
        raise RuntimeError("Download completed but file could not be located.")

    file_path = pathlib.Path(filepath)
    return {
        "id": request_id,
        "title": main_info.get("title") or "Untitled",
        "uploader": main_info.get("uploader") or main_info.get("channel") or "Unknown",
        "duration": main_info.get("duration"),
        "source_url": url,
        "filename": file_path.name,
        "download_url": url_for("download_file", filename=file_path.name),
    }


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    result = None
    error = None

    if request.method == "POST":
        url = (request.form.get("url") or "").strip()

        if not url:
            error = "Please enter a URL."
        elif not _is_supported_url(url):
            error = "Only Instagram/Facebook URLs are supported."
        else:
            try:
                result = _download_media(url)
            except Exception as exc:  # noqa: BLE001
                error = f"Download failed: {exc}"

    return render_template("index.html", result=result, error=error)


@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename: str):
    safe_target = DOWNLOAD_DIR / filename
    if not safe_target.exists() or not safe_target.is_file():
        abort(404)
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
