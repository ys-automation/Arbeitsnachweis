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
