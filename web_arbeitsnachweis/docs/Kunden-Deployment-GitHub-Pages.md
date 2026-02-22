# Kunden-Deployment mit GitHub Pages

## Ziel

Die App wird als feste HTTPS-URL bereitgestellt:
- `https://<github-name>.github.io/<repo-name>/`

So laeuft sie auf Kundenrechnern ohne Python, ohne localhost und ohne lokale Installation.

## Einmalige Einrichtung

1. Repository nach GitHub pushen.
2. In GitHub: `Settings -> Pages -> Build and deployment`.
3. Bei `Source` auf `GitHub Actions` stellen.
4. Sicherstellen, dass der Workflow `Deploy GitHub Pages` vorhanden ist:
   - Datei: `.github/workflows/deploy-pages.yml`

## Release-Prozess

1. Aenderungen in `web_arbeitsnachweis/` durchfuehren.
2. Commit und Push auf `main`.
3. In `Actions` den Lauf `Deploy GitHub Pages` abwarten.
4. Deployment-URL oeffnen und kurz pruefen:
   - Eingaben moeglich
   - Berechnung/Validierung funktioniert
   - Reset-Button funktioniert

## Kunden-Onboarding

1. Kunde oeffnet die URL im Browser.
2. Optional als App installieren:
   - iPhone: Safari -> Teilen -> Zum Home-Bildschirm
   - Edge/Chrome: Installieren-Symbol in der Adressleiste
3. Nutzung ohne weitere lokale Voraussetzungen.

## Betriebsregeln

- Keine Kunden-Distribution mehr per BAT/localhost als Primaerweg.
- Bei sichtbaren Altstaenden Cache-Version in `service-worker.js` erhoehen.
- Versionen synchron halten in:
  - `web_arbeitsnachweis/index.html`
  - `web_arbeitsnachweis/manifest.webmanifest`
  - `web_arbeitsnachweis/CHANGELOG.md`
