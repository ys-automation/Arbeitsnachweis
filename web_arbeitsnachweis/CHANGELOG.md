# Changelog

## v1.2.0 - 2026-02-21
- Produktbenennung vereinheitlicht: `Worktime Report Generator (Arbeitsnachweis)`.
- Versionsangaben in Web-App und Manifest auf `1.2.0` aktualisiert.
- Reproduzierbare Release-Erstellung ueber `scripts/create_release_zip.ps1` eingefuehrt.
- Integritaetspruefung des ZIP-Pakets ueber `scripts/verify_release_zip.ps1` ergaenzt.
- CI-Workflow fuer Syntaxcheck und automatischen ZIP-Build eingefuehrt.
- Repository-Standards mit `.editorconfig` und `.gitattributes` ergaenzt.

## v1.1.0 - 2026-02-21
- Taegliche Autospeicherung eingefuehrt: Eingaben werden pro Kalendertag lokal gespeichert.
- Wochenzeilen werden an konkrete Datumswerte gebunden (z. B. Mo 23.02.).
- Hinweis- und Statusmeldungen zur Autospeicherung ergaenzt.
- Cache-Version aktualisiert, damit die neue App-Version sicher ausgeliefert wird.

## v1.0.0 - 2026-02-21
- Browserbasierte Arbeitsnachweis-App finalisiert (Wochenuebersicht + Berechnung + Validierung).
- Spalte "Warte" entfernt.
- Dark/Light Modus mit Umschalter eingebaut.
- PWA-Installationsfunktion inkl. Manifest und Service Worker integriert.
- Transnova Logo eingebunden.
- Projektstruktur professionell reorganisiert (`assets/`, `docs/`).
- Kollegen-Anleitung als TXT und PDF hinzugefuegt.
- Release-ZIP fuer Weitergabe erstellt.
