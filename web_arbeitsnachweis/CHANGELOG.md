# Changelog

## v1.4.0 - 2026-02-21
- Reset-Button `Woche zuruecksetzen` in der Pruefsektion hinzugefuegt.
- Reset loescht die Eingaben der aktuell sichtbaren Woche aus Formular und lokalem Speicher.
- Hinweistext ergaenzt: neue Woche startet mit neuen Datumswerten leer.
- Service-Worker-Cache auf `arbeitsnachweis-v1-4-0` angehoben.

## v1.3.1 - 2026-02-21
- Branding-Finetuning im Header (klarere Markenzeile, Version-Badge, bessere Meta-Infos).
- App-Metadaten verbessert (Description + Favicon-Eintraege im HTML).
- Manifest auf `1.3.1` aktualisiert und `short_name` praezisiert.
- Service-Worker-Cache auf `arbeitsnachweis-v1-3-1` angehoben.

## v1.3.0 - 2026-02-21
- Produktname auf `Weekly Work Report` aktualisiert.
- Web-Versionen in UI und Manifest auf `1.3.0` angehoben.
- Service-Worker-Cache auf `arbeitsnachweis-v1-3-0` gesetzt.

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
