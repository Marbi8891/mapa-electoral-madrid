# Mapa de mesas electorales · Madrid

Mapa Leaflet (OpenStreetMap) con los 21 distritos municipales y las ubicaciones del documento `MESAS ELECTORALES.docx`.

## Estructura
- `index.html`, `styles.css`, `app.js`: aplicación (sin frameworks; Leaflet y markercluster desde cdnjs).
- `data/mesas-electorales.json`: 40 ubicaciones inventariadas (estado y fuente de geocodificación por registro).
- `data/distritos.geojson`: límites de los 21 distritos (Geoportal del Ayuntamiento de Madrid, TopoJSON oficial, simplificado a ~13 m; CC BY 4.0).
- `scripts/build_data.py`: regenera el JSON; el distrito se calcula por punto-en-polígono.

## Ejecutar en local
```bash
cd mapa-electoral-madrid
python3 -m http.server 8000   # abrir http://localhost:8000
```
(No funciona abriendo `index.html` con `file://`: el navegador bloquea `fetch` de los JSON.)

## Publicar en GitHub Pages
1. Sube la carpeta a un repositorio (raíz con `index.html`).
2. Settings → Pages → Source: *Deploy from a branch* → `main` / `/ (root)`.
3. La web queda en `https://<usuario>.github.io/<repo>/`.

## Calidad de los datos
- **verificada**: dirección con nº de portal coincidente, o centro/estación identificado por nombre en OSM.
- **aproximada**: solo calle, plaza o glorieta; el punto no es la ubicación exacta de la mesa.
- **pendiente**: sin coincidencia fiable; no se dibuja, aparece en la lista de pendientes.
Para corregir un punto, edita `lat`/`lon`/estado en `scripts/build_data.py` y ejecútalo.
