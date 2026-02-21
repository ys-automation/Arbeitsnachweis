# Worktime Report Generator (Arbeitsnachweis)

Dieses Repository enthaelt eine professionelle Arbeitsnachweis-Loesung mit zwei Komponenten:

- `src/`: Desktop-Anwendung (Python + CustomTkinter)
- `web_arbeitsnachweis/`: installierbare Web-App (PWA) fuer Kollegen

Der Name auf GitHub und nach aussen ist bewusst `Worktime Report Generator`. Der Fachbegriff `Arbeitsnachweis` bleibt in der App erhalten, damit die Nutzung im Alltag klar ist.

## Projektstruktur

- `src/ruf_arbeitsnachweis.py`: Desktop-Hauptanwendung
- `web_arbeitsnachweis/index.html`: Web-Oberflaeche
- `web_arbeitsnachweis/assets/js/app.js`: Berechnung, Validierung, Autospeicherung
- `scripts/create_release_zip.ps1`: reproduzierbare Erstellung des Weitergabe-ZIP
- `scripts/verify_release_zip.ps1`: Integritaetspruefung ZIP gegen Quellordner
- `build_release_zip.bat`: 1-Klick-Release-Paket fuer Windows

## Schnellstart

### Web-App

1. In den Ordner `web_arbeitsnachweis` wechseln.
2. `start_web_app.bat` starten.
3. `http://localhost:8080/` im Browser oeffnen.

### Desktop-App

1. Python-Umgebung mit benoetigten Paketen bereitstellen.
2. `python src/ruf_arbeitsnachweis.py` ausfuehren.

## Release-Prozess (professionell/reproduzierbar)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/create_release_zip.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_release_zip.ps1
```

Oder per Doppelklick:

- `build_release_zip.bat`

## Qualitaet

- `.editorconfig` und `.gitattributes` fuer saubere, konsistente Dateien
- GitHub Actions CI fuer Syntaxcheck + ZIP-Build + ZIP-Verifikation
- Versionierung und Historie in `web_arbeitsnachweis/CHANGELOG.md`
