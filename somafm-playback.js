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
    icon.src = new URL("somafm.png", document.currentScript.src).href;
    icon.alt = "";
    icon.width = 24;
    icon.height = 24;
    icon.className = "me-2";
    button.append(icon, "SomaFM");
    button.addEventListener("click", () => execScriptFromOptions("SomaFM", [""]));
    anchor.after(button);
})();
