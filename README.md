# Weekly Work Report

Dieses Repository enthaelt die Web-App `web_arbeitsnachweis/`.

## Produktiver Betrieb (empfohlen)

Fuer den Kundenbetrieb wird die App per HTTPS ueber GitHub Pages ausgeliefert.
Damit entfallen lokale Abhaengigkeiten wie Python/localhost auf Kundengeraeten.

- Deployment: `.github/workflows/deploy-pages.yml`
- Quelle: `web_arbeitsnachweis/`
- Ziel-URL: `https://<github-name>.github.io/<repo-name>/`

Einmalig in GitHub:
1. `Settings -> Pages -> Build and deployment`
2. `Source: GitHub Actions`

Ab dann gilt:
- Aenderung in `web_arbeitsnachweis/`
- Commit + Push nach `main`
- automatische Aktualisierung der Kunden-URL

## Lokaler Testmodus (nur intern)

```powershell
cd web_arbeitsnachweis
start_web_app.bat
```

## Release-ZIP (interne Weitergabe)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/create_release_zip.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_release_zip.ps1
```

Alternativ:
- `build_release_zip.bat`

## Hinweise

- Fachlicher Name: `Arbeitsnachweis`
- Produktname: `Weekly Work Report`
- Projektdetails: `web_arbeitsnachweis/README.md`
