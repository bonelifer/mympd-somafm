(() => {
    const anchor = document.getElementById("PlaybackTitle");
    if (!anchor || document.getElementById("somafm-picker")) {
        return;
    }
    const button = document.createElement("button");
    button.id = "somafm-picker";
    button.type = "button";
    button.className = "btn btn-secondary me-2 mb-2";
    const icon = document.createElement("img");
    icon.src = new URL("thumbs/somafm-papirus.png", document.currentScript.src).href;
    icon.alt = "";
    icon.width = 24;
    icon.height = 24;
    icon.className = "me-2";
    button.append(icon, "SomaFM");
    button.addEventListener("click", () => execScriptFromOptions("SomaFM", [""]));
    anchor.after(button);

    let lastKey = "";
    let lastAlbum = "";
    let pending;
    const normalized = value => value.normalize("NFKC").trim()
        .replace(/\s+[-–—]\s+/gu, " - ").replace(/\s+/gu, " ").toLowerCase();

    function currentTrack() {
        const song = typeof currentSongObj === "undefined" ? null : currentSongObj;
        if (!song?.uri || !song.Title || song.Album?.length) return null;
        const uri = new URL(song.uri, document.baseURI);
        if (!uri.hostname.endsWith(".somafm.com")) return null;
        const station = uri.pathname.match(/^\/([a-z0-9-]+?)(?:-\d+(?:-(?:mp3|aacp?|flac))?)?$/i)?.[1];
        return station ? {station, title: normalized(song.Title), key: uri.href + "\n" + song.Title}
            : null;
    }

    function displayAlbum(album) {
        const field = document.querySelector("#currentAlbum p");
        if (field && field.textContent !== album) field.textContent = album;
    }

    async function updateAlbum() {
        const track = currentTrack();
        if (!track) {
            lastKey = "";
            lastAlbum = "";
            return;
        }
        if (track.key === lastKey) {
            if (lastAlbum) displayAlbum(lastAlbum);
            return;
        }
        lastKey = track.key;
        lastAlbum = "";
        const partition = encodeURIComponent(localSettings.partition);
        try {
            const response = await fetch(subdir + "/script/" + partition +
                "/SomaFM?station=" + encodeURIComponent(track.station),
            {cache: "no-store", signal: AbortSignal.timeout(12000)});
            if (!response.ok) return;
            const songs = await response.json();
            const match = songs.find(song => song.artist && song.title &&
                normalized(song.artist + " - " + song.title) === track.title);
            if (match?.album && currentTrack()?.key === track.key) {
                lastAlbum = match.album;
                displayAlbum(lastAlbum);
            }
        } catch {
            // An unavailable history feed does not interrupt playback.
        }
    }

    const observer = new MutationObserver(() => {
        if (pending === undefined) {
            pending = setTimeout(() => {
                pending = undefined;
                updateAlbum();
            }, 0);
        }
    });
    for (const id of ["PlaybackTitle", "footerTitle", "PlaybackListTags"]) {
        const element = document.getElementById(id);
        if (element) observer.observe(element, {childList: true, subtree: true});
    }
    updateAlbum();
})();
