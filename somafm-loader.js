(() => {
    const script = document.createElement("script");
    const url = new URL("browse/pics/somafm-playback.js?v=3", document.currentScript.src).href;
    const policy = window.trustedTypes?.createPolicy("somafm-player", {
        createScriptURL(candidate) {
            if (candidate !== url) {
                throw new TypeError("Unexpected SomaFM script URL");
            }
            return url;
        }
    });
    script.src = policy ? policy.createScriptURL(url) : url;
    document.head.append(script);
})();
