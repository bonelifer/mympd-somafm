#!/usr/bin/env python3
"""Provide the current SomaFM lineup to the myMPD picker."""

import argparse
import json
import os
import re
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen


def cache_cover(uri: str, source: str, *, refresh: bool = False) -> bool:
    """Store a provider image using myMPD's native stream cover filename."""
    directory = os.environ.get("MYMPD_THUMBS_DIR")
    if not directory:
        return False
    base = Path(directory) / re.sub(r"[^A-Za-z0-9_-]", "_", uri)
    extensions = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    if not refresh and any(base.with_suffix("." + ext).is_file()
                           for ext in extensions.values()):
        return True
    temporary = None
    try:
        with urlopen(source, timeout=4) as response:
            extension = extensions.get(response.headers.get_content_type())
            data = response.read(2_000_001)
        if not extension or not 0 < len(data) <= 2_000_000:
            return False
        with tempfile.NamedTemporaryFile(dir=directory, delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
        temporary.chmod(0o644)
        temporary.replace(base.with_suffix("." + extension))
        return True
    except OSError:
        return False
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def stations() -> list[dict]:
    """Read current stations and list their published MP3 playlists."""
    with urlopen("https://somafm.com/channels.json", timeout=10) as response:
        lineup = json.load(response)
    result = []
    for channel in lineup["channels"]:
        for playlist in channel.get("playlists", []):
            if playlist.get("format") != "mp3":
                continue
            name = playlist["url"].rsplit("/", 1)[-1].removesuffix(".pls")
            if name and name.isascii() and name.replace("-", "").isalnum():
                result.append({
                    "name": channel["title"],
                    "id": name,
                    "image": channel.get("xlimage") or channel.get("largeimage"),
                })
                break
    return sorted(result, key=lambda station: station["name"].casefold())


def resolve(station: str) -> dict:
    """Resolve the provider's playlist to an HTTPS audio endpoint."""
    with urlopen(f"https://api.somafm.com/{station}.pls", timeout=10) as response:
        playlist = response.read(32768).decode("utf-8")
    for url in re.findall(r"^File[0-9]+=(.+)", playlist, re.M):
        parts = urlsplit(url.strip())
        if (parts.scheme in {"http", "https"} and parts.hostname
                and parts.hostname.endswith(".somafm.com")
                and not parts.username and not parts.password):
            return {"url": parts._replace(scheme="https").geturl()}
    raise ValueError("No SomaFM stream in playlist")


def recent_tracks(station: str) -> list[dict]:
    """Return the artist, title, and album from a station's recent feed."""
    with urlopen(f"https://api.somafm.com/songs/{station}.json",
                 timeout=8) as response:
        feed = json.load(response)
    return [{key: song.get(key) or "" for key in ("artist", "title", "album")}
            for song in feed["songs"]]


class Handler(BaseHTTPRequestHandler):
    """Serve the station list on the bridge's private listener."""

    def do_GET(self) -> None:
        """Return the current lineup or an upstream error."""
        station = re.fullmatch(r"/stations/([a-zA-Z0-9-]+)", self.path)
        recent = re.fullmatch(r"/recent/([a-zA-Z0-9-]{1,64})", self.path)
        if self.path != "/stations" and not station and not recent:
            self.send_error(404)
            return
        try:
            if recent:
                data = recent_tracks(recent[1])
            else:
                data = stations() if not station else resolve(station[1])
            if station and os.environ.get("MYMPD_THUMBS_DIR"):
                try:
                    image = next((item["image"] for item in stations()
                                  if item["id"] == station[1]), None)
                    if image and urlsplit(image).netloc == "api.somafm.com" and image.startswith("https://"):
                        cache_cover(data["url"], image, refresh=True)
                except (OSError, ValueError, KeyError, TypeError):
                    pass  # Station playback still works if artwork is unavailable.
            body = json.dumps(data).encode()
        except (OSError, ValueError, KeyError, TypeError):
            self.send_error(502, "Could not load SomaFM channels")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18768)
    options = parser.parse_args()
    ThreadingHTTPServer((options.listen, options.port), Handler).serve_forever()
