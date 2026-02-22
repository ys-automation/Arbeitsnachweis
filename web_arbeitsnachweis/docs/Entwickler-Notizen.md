# Entwickler-Notizen

## Aenderungen sind nicht sichtbar (Service Worker / Cache)

Symptom:
- Rechtschreibung/Text wurde geaendert und gespeichert, aber die Seite zeigt weiter den alten Stand.

Schnellcheck:
1. Seite mit Ctrl+Shift+R hart neu laden.
2. Wenn immer noch alt: DevTools -> Application -> Service Workers -> Unregister.
3. Bei Asset-Aenderungen (index.html, app.js, styles.css) die Cache-Version in service-worker.js erhoehen.

Merksatz:
- Wenn eine PWA alte Inhalte zeigt, ist fast immer zuerst der Service-Worker-Cache zu pruefen.

## Deployment auf iPhone (GitHub Pages)

Ziel:
- Die Web-App per HTTPS bereitstellen und auf iOS als PWA installieren.

Einmalige Einrichtung:
1. In GitHub: `Settings -> Pages -> Build and deployment`.
2. `Source: GitHub Actions` waehlen.
3. Sicherstellen, dass `.github/workflows/deploy-pages.yml` im Repository liegt.

URL:
- `https://<github-name>.github.io/<repo-name>/`

Installation auf iPhone:
1. URL in Safari oeffnen.
2. Teilen-Symbol tippen.
3. `Zum Home-Bildschirm` waehlen.

Updates deployen:
```powershell
git add .
git commit -m "Update"
git push origin main
```

Hinweis:
- Nach Push auf `main` deployt GitHub Actions automatisch den Ordner `web_arbeitsnachweis`.

Wichtig bei sichtbaren Altstaenden:
- Cache-Version in `service-worker.js` anheben (`CACHE_NAME`), dann neu deployen.

## Firmenlaptop: Keine Verbindung zu localhost

Symptom:
- Browser meldet `localhost` nicht erreichbar, obwohl `start_web_app.bat` gestartet wurde.

Schnellcheck:
1. Statt `http://localhost:8080/` direkt `http://127.0.0.1:8080/` aufrufen.
2. Pruefen, ob Python verfuegbar ist:
   ```powershell
   python --version
   py --version
   ```
3. Startskript neu starten (`start_web_app.bat`), es nutzt jetzt `127.0.0.1`.
4. Wenn kein Python installiert ist: `start_web_app.bat` startet automatisch `index.html` direkt.

Fallback:
- Wenn lokal nichts erlaubt ist: Deployment ueber GitHub Pages (HTTPS) und dann darueber arbeiten.
- Beim Direktstart ohne Python (`file://`) laufen die Kernfunktionen, aber keine PWA-Installation und kein Service-Worker-Offline-Cache.
- In restriktiven Firmenbrowsern kann auch `localStorage` bei `file://` blockiert sein; dann bleiben Eingaben nur temporaer.
