# Weekly Work Report (Arbeitsnachweis Web)

Version: `1.5.0`

Diese PWA ist die Web-Ausfuehrung des Arbeitsnachweises und enthaelt:
- Wochenuebersicht (ohne Spalte "Warte")
- automatische Zeitberechnung (Arbeitsstunden/Gesamt)
- Eingabevalidierung fuer die Wochenuebersicht
- taegliche Autospeicherung pro Kalendertag (browserlokal)
- Dark/Light Modus (umschaltbar)
- Transnova Logo oben rechts
- installierbar als App (PWA)

Nicht enthalten:
- Stammdatenbereich
- auszufuehrende Arbeiten
- Reisetabelle
- PDF-Erzeugung
- Signatur
- Export-/Mailfunktion

## Kundenbetrieb (empfohlen)

Fuer Vermarktung und echten Betrieb wird die App per HTTPS gehostet.
Empfohlene Standardroute in diesem Repository:

1. GitHub `Settings -> Pages -> Build and deployment`
2. `Source: GitHub Actions` aktivieren
3. Push auf `main` ausfuehren
4. Deployment laeuft automatisch ueber `.github/workflows/deploy-pages.yml`

Kunden-URL:
- `https://<github-name>.github.io/<repo-name>/`

Vorteil:
- kein Python
- kein localhost
- keine lokalen IT-Policy-Probleme auf Kundengeraeten

## Benennung

- GitHub-/Produktname: `Weekly Work Report`
- fachlicher Begriff in der App: `Arbeitsnachweis`

## Lokaler Testmodus (intern)

1. `start_web_app.bat` starten.
2. Wenn ein lokaler Server verfuegbar ist, oeffnet die App auf `http://127.0.0.1:8080/`.
3. Ohne Server faellt die BAT auf Direktstart (`index.html`) zurueck.

Einschraenkung im Direktstart (`file://`):
- keine PWA-Installation
- kein Service-Worker-Offline-Cache
- bei restriktiven Firmenbrowsern evtl. kein persistenter lokaler Speicher

## Release-Paket erstellen

Aus dem Repository-Root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/create_release_zip.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_release_zip.ps1
```

## Ordnerstruktur
- assets/css/styles.css
- assets/js/app.js
- assets/icons/icon-192.png + icon-512.png
- assets/logos/transnova_logo.png
- docs/Kollegen-Anleitung.txt + .pdf
- docs/Kunden-Deployment-GitHub-Pages.md

## Release-Historie
- Siehe `CHANGELOG.md`
