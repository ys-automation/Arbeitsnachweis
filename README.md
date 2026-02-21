# Weekly Work Report

Dieses Repository ist ein Monorepo mit **zwei getrennten Projekten**:

1. `src/` -> Python Desktop-App
2. `web_arbeitsnachweis/` -> Web-App (HTML/CSS/JS, PWA)

Sie nutzen denselben fachlichen Zweck (Arbeitsnachweis), sind aber technisch unabhaengig.

## Welche README ist fuer welches Projekt?

- Python-Projekt: `src/README.md`
- Web-Projekt: `web_arbeitsnachweis/README.md`

## Schnellstart je Projekt

### 1) Python Desktop-App

```powershell
python src/ruf_arbeitsnachweis.py
```

### 2) Web-App

```powershell
cd web_arbeitsnachweis
start_web_app.bat
```

## Release-ZIP fuer Web-App

Die folgenden Skripte betreffen nur das Web-Projekt:

- `scripts/create_release_zip.ps1`
- `scripts/verify_release_zip.ps1`
- `build_release_zip.bat`

## Repo-Qualitaet

- `.editorconfig` und `.gitattributes` fuer konsistente Dateien
- GitHub Actions CI mit Python-Syntaxcheck sowie Web-ZIP-Build/Verifikation
