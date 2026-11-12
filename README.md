# SomaFM for myMPD

Open SomaFM from Home, Playback, or the Scripts menu. The picker loads the
current SomaFM lineup each time it opens. When you choose a channel, it resolves
SomaFM's published MP3 playlist and plays the resulting stream in MPD.

## Setup

Start the bridge with `docker compose up -d --build` or run
`python3 bridge.py`. The default listener is `127.0.0.1:18768`, for myMPD
using host networking. Enable Lua scripting in myMPD and install the picker:

```bash
python3 install-picker.py --mympd http://127.0.0.1:8081 --workdir /path/to/mympd/workdir
```

The installer copies the bundled Home icon to `pics/thumbs/` and creates
or updates the matching tile. Omit `--workdir` to install only the Lua script.
If API protection is on, pass your session as `MYMPD_SESSION`.

For the Playback page button, copy `assets/somafm.png` and
`somafm-playback.js` to myMPD's `pics/` directory. Append the contents of
`somafm-loader.js` to `config/custom_js` once. Restart myMPD and reload
the browser.

## Playback artwork

Set `MYMPD_THUMBS_DIR` in Compose's `.env` to the absolute path of myMPD's
`pics/thumbs/` directory. The bridge writes covers there for myMPD's native
Playback and footer artwork. Restart the bridge after changing the path.

## Contributing

Contributions are welcome!

- **Bug reports**: [Open an issue](https://github.com/bonelifer/mympd-somafm/issues).
- **Everything else** (questions, feature requests, ideas, general discussion): [Use Discussions](https://github.com/bonelifer/mympd-somafm/discussions).
- Pull requests are welcome for bug fixes or discussed features.

## Acknowledgments

- Code, testing, and documentation assisted by [Codex](https://openai.com/codex/).

## License

Code is licensed under GPL-3.0. The original icon is [CC0](assets/LICENSE.md).
