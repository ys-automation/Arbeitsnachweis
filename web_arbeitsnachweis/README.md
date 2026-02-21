# Arbeitsnachweis (Web)

Version: `1.1.0`

Dieses Projekt ist eine Browser-Version deines Arbeitsnachweises und enthaelt:
- Wochenuebersicht (ohne Spalte "Warte")
- automatische Zeitberechnung (Arbeitsstunden/Gesamt)
- Eingabevalidierung fuer die Wochenuebersicht
- taegliche Autospeicherung pro Kalendertag (browserlokal)
- Dark/Light Modus (umschaltbar)
- Transnova Logo oben rechts
- installierbar als App (PWA)

Nicht enthalten:
- Stammdatenbereich
- Auszufuehrende Arbeiten
- Reisetabelle
- PDF-Erzeugung
- Signatur
- Export-/Mailfunktion

## Weitergabe an Kollegen

Du kannst den Ordner `web_arbeitsnachweis` direkt weitergeben (ZIP oder USB).
Alles Notwendige ist in diesem Ordner enthalten, inklusive Logo und Icons.

## Start beim Kollegen

1. Ordner `web_arbeitsnachweis` entpacken.
2. `start_web_app.bat` doppelklicken.
3. Im Browser auf `App installieren` klicken (Edge/Chrome).

Alternative ohne BAT:
1. Im Ordner `web_arbeitsnachweis` ein Terminal oeffnen.
2. `python -m http.server 8080`
3. `http://localhost:8080/` aufrufen.

## Ordnerstruktur
- assets/css/styles.css
- assets/js/app.js
- assets/icons/icon-192.png + icon-512.png
- assets/logos/transnova_logo.png
- docs/Kollegen-Anleitung.txt + .pdf

## Release-Historie
- Siehe `CHANGELOG.md`
