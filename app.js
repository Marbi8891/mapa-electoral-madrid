(() => {
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const PALETTE = ['#f4b6c2','#b5dbf0','#c9e4b0','#f9d99a','#d7c4ee','#a8e0d2','#f7c2a3','#c6d3f2','#e6e0a0','#efb9e0','#b9e3c1','#f3c9c9','#a9cfe8','#e0cfa6','#cfd8a8','#e5b8d4','#b3d9d9','#f1d0a0','#c8bfe8','#d6ecb0','#f0b8b8'];
const toast = (m, ms = 5000) => { const t = $('toast'); t.textContent = m; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => t.hidden = true, ms); };

// ---- Mapa y capas base ----
const map = L.map('map', { zoomControl: true, preferCanvas: false }).setView([40.4168, -3.7038], 11);
map.createPane('distritos').style.zIndex = 350;   // por debajo de los marcadores (600)
const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(map);
const carto = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', { maxZoom: 19, subdomains: 'abcd', attribution: '© OpenStreetMap · © CARTO' });
let tileErr = 0, usingFallback = false;
osm.on('tileerror', e => {
  if (e.tile && !e.tile.dataset.retry) { e.tile.dataset.retry = 1; setTimeout(() => { e.tile.src = e.tile.src.split('?')[0] + '?r=1'; }, 1500); return; }
  if (++tileErr === 8 && !usingFallback) { usingFallback = true; map.removeLayer(osm); carto.addTo(map); toast('OpenStreetMap no responde; usando mapa alternativo (CARTO).'); }
});
setTimeout(() => map.invalidateSize(), 200);
addEventListener('resize', () => map.invalidateSize());

// ---- Estado ----
let DATA = [], distLayer = null, distByName = {}, cluster = null;
const markers = new Map();
const state = { distrito: '', aprox: true, marcadores: true };
let initialBounds = null;

function pinIcon(est, sel) { return L.divIcon({ className: '', html: `<div class="pin ${est === 'verificada' ? 'ok' : 'ap'}${sel ? ' sel' : ''}"></div>`, iconSize: [20, 20], iconAnchor: [10, 10], popupAnchor: [0, -12] }); }

function gmapsUrl(o) {
  if (o.estado_geocodificacion === 'verificada') return `https://www.google.com/maps/search/?api=1&query=${o.latitud},${o.longitud}`;
  if (o.enlace_google_documento) return o.enlace_google_documento;
  return 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent((o.direccion_original || o.nombre) + ', Madrid');
}
const addrText = o => o.direccion_original || `${o.nombre}, Madrid`;

function popupHtml(o) {
  const ap = o.estado_geocodificacion !== 'verificada';
  const estado = { verificada: 'Coordenadas verificadas', aproximada: 'Ubicación aproximada', pendiente: 'Pendiente de verificar' }[o.estado_geocodificacion];
  const foto = o.imagen_verificada
    ? `<figure class="foto"><a href="${esc(o.imagen_fuente)}" target="_blank" rel="noopener" title="Ver imagen original"><img src="${esc(o.imagen_url)}" alt="${esc(o.imagen_leyenda)}" loading="lazy" width="320" height="200"></a>
       <figcaption>${esc(o.imagen_leyenda)} · ${esc(o.imagen_autor)} · ${esc(o.imagen_licencia)} · Wikimedia Commons</figcaption></figure>`
    : `<div class="foto nofoto">Fotografía no disponible</div>`;
  const dir = o.latitud != null ? `https://www.google.com/maps/dir/?api=1&destination=${o.latitud},${o.longitud}` : null;
  return `<div class="pop"><h3>${esc(o.nombre)}</h3>
  ${foto}
  <p><b>Dirección:</b> ${o.direccion_original ? esc(o.direccion_original) : '<i>no indicada en el documento</i>'}</p>
  <p><b>Distrito:</b> ${esc(o.distrito || '—')} <span class="mut">· zona del documento: ${esc(o.zona_documento)}</span></p>
  <p><b>ID:</b> ${o.id} <span class="mut">(asignado al inventariar; el documento no numera las mesas)</span></p>
  <p><span class="tag ${ap ? 'ap' : ''}">${estado}</span></p>
  ${o.observaciones ? `<p>${esc(o.observaciones)}</p>` : ''}
  ${o.fuente_geocodificacion ? `<p class="mut" style="font-size:12px">Fuente: ${esc(o.fuente_geocodificacion)}</p>` : ''}
  <div class="acts"><a href="${esc(gmapsUrl(o))}" target="_blank" rel="noopener">Abrir en Google Maps</a>${dir ? `<a href="${esc(dir)}" target="_blank" rel="noopener">Cómo llegar</a>` : ''}</div>
  <div class="acts">${o.street_view_url && !o.imagen_verificada ? `<a href="${esc(o.street_view_url)}" target="_blank" rel="noopener">Ver en Street View</a>` : ''}${o.imagen_verificada ? `<a href="${esc(o.imagen_fuente)}" target="_blank" rel="noopener">Ver imagen original</a>` : ''}<button type="button" data-copy="${o.id}">Copiar dirección</button></div></div>`;
}

document.addEventListener('click', async e => {
  const b = e.target.closest('[data-copy]'); if (!b) return;
  const o = DATA.find(x => x.id == b.dataset.copy), txt = addrText(o);
  try { await navigator.clipboard.writeText(txt); } catch { const t = document.createElement('textarea'); t.value = txt; document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove(); }
  b.textContent = '¡Copiada!'; setTimeout(() => b.textContent = 'Copiar dirección', 1500);
});

// ---- Marcadores ----
function buildMarkers() {
  cluster = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 38, spiderfyOnMaxZoom: true, disableClusteringAtZoom: 16 });
  DATA.filter(o => o.latitud != null).forEach(o => {
    const m = L.marker([o.latitud, o.longitud], { icon: pinIcon(o.estado_geocodificacion), title: o.nombre, riseOnHover: true });
    m.bindPopup(() => popupHtml(o), { maxWidth: 340, minWidth: 250, autoPan: true });
    m.on('popupopen', () => m.setIcon(pinIcon(o.estado_geocodificacion, true)));
    m.on('popupclose', () => m.setIcon(pinIcon(o.estado_geocodificacion, false)));
    markers.set(o.id, m);
  });
  map.addLayer(cluster);
}
const visible = o => o.latitud != null && (!state.distrito || o.distrito === state.distrito) && (state.aprox || o.estado_geocodificacion === 'verificada');
function refresh() {
  cluster.clearLayers();
  if (state.marcadores) cluster.addLayers(DATA.filter(visible).map(o => markers.get(o.id)));
  const n = DATA.filter(visible).length, p = DATA.filter(o => o.latitud == null).length;
  $('count').textContent = `${n} en mapa · ${p} pendientes`;
}
function fitVisible(maxZoom = 15) {
  const pts = DATA.filter(visible).map(o => [o.latitud, o.longitud]);
  if (pts.length) map.fitBounds(L.latLngBounds(pts).pad(0.12), { maxZoom });
}

// ---- Distritos ----
function buildDistritos(gj) {
  distLayer = L.geoJSON(gj, {
    pane: 'distritos',
    style: f => ({ color: '#5b6675', weight: 1.4, fillColor: PALETTE[(+f.properties.codigo - 1) % PALETTE.length], fillOpacity: 0.45 }),
    onEachFeature: (f, l) => {
      distByName[f.properties.nombre] = l;
      l.bindTooltip(f.properties.nombre, { sticky: true, className: 'dtip' });
      l.on('mouseover', () => l.setStyle({ weight: 2.5, fillOpacity: 0.6 }));
      l.on('mouseout', () => { distLayer.resetStyle(l); if (state.distrito === f.properties.nombre) hiliDistrito(); });
      l.on('click', e => { if (!e.originalEvent._pin) l.bindPopup(`<b>${esc(f.properties.nombre)}</b><br>Distrito ${f.properties.codigo}`).openPopup(e.latlng); });
    }
  }).addTo(map);
  Object.keys(distByName).sort((a, b) => distByName[a].feature.properties.codigo - distByName[b].feature.properties.codigo)
    .forEach(n => $('selDistrito').add(new Option(`${distByName[n].feature.properties.codigo} · ${n}`, n)));
}

// ---- Buscador ----
const norm = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
$('q').addEventListener('input', () => {
  const t = norm($('q').value.trim()), ul = $('results'); ul.innerHTML = '';
  if (t.length < 2) { ul.hidden = true; return; }
  const hits = DATA.filter(o => norm([o.nombre, o.direccion_original, o.direccion_normalizada, o.codigo_postal, o.distrito, o.zona_documento, o.identificador_mesa].join(' ')).includes(t)).slice(0, 12);
  hits.forEach(o => { const li = document.createElement('li'); li.tabIndex = 0;
    li.innerHTML = `${esc(o.nombre)}<small>${esc(o.distrito || 'Pendiente de verificar')} · ${esc(o.zona_documento)}</small>`;
    const go = () => { ul.hidden = true; $('q').value = o.nombre; goTo(o); };
    li.onclick = go; li.onkeydown = e => e.key === 'Enter' && go(); ul.appendChild(li); });
  if (!hits.length) ul.innerHTML = '<li><small>Sin resultados</small></li>';
  ul.hidden = false;
});
document.addEventListener('click', e => { if (!e.target.closest('.search')) $('results').hidden = true; });
function goTo(o) {
  if (o.latitud == null) { openPanel(true); $('pend').open = true; toast('Esta ubicación está pendiente de verificar; consulta la lista de pendientes.'); return; }
  state.distrito = ''; $('selDistrito').value = ''; state.marcadores = true; $('chkMarcadores').checked = true;
  if (o.estado_geocodificacion !== 'verificada') { state.aprox = true; $('chkAprox').checked = true; }
  refresh(); const m = markers.get(o.id);
  cluster.zoomToShowLayer(m, () => { map.setView(m.getLatLng(), Math.max(map.getZoom(), 17)); m.openPopup(); });
}

// ---- Controles ----
function openPanel(on) { $('panel').hidden = !on; $('btnPanel').setAttribute('aria-expanded', on); document.body.classList.toggle('panel-open', on); }
$('btnPanel').onclick = () => openPanel($('panel').hidden);
$('btnReset').onclick = () => { state.distrito = ''; $('selDistrito').value = ''; refresh(); hiliDistrito(); map.closePopup(); initialBounds ? map.fitBounds(initialBounds, { maxZoom: 15 }) : fitVisible(); };
$('btnAll').onclick = () => { state.distrito = ''; $('selDistrito').value = ''; refresh(); fitVisible(); };
function hiliDistrito() { if (!distLayer) return; distLayer.eachLayer(l => distLayer.resetStyle(l)); const l = distByName[state.distrito]; if (l) { l.setStyle({ color: '#1c2430', weight: 3.5, fillOpacity: 0.2 }); l.bringToFront(); } }
$('selDistrito').onchange = e => { state.distrito = e.target.value; refresh(); hiliDistrito(); if (state.distrito) { const l = distByName[state.distrito]; if (l) map.fitBounds(l.getBounds().pad(0.05)); } else fitVisible(); };
$('chkDistritos').onchange = e => { if (!distLayer) return; e.target.checked ? distLayer.addTo(map) : map.removeLayer(distLayer); };
$('chkMarcadores').onchange = e => { state.marcadores = e.target.checked; refresh(); };
$('chkAprox').onchange = e => { state.aprox = e.target.checked; refresh(); };

// ---- Carga de datos ----
const getJSON = u => fetch(u).then(r => { if (!r.ok) throw new Error(u + ' → ' + r.status); return r.json(); });
(async () => {
  try {
    const d = await getJSON('data/mesas-electorales.json'); DATA = d.ubicaciones;
  } catch (e) { console.error(e); toast('No se pudieron cargar las ubicaciones (data/mesas-electorales.json). Abre la web desde un servidor, no con file://.', 12000); return; }
  buildMarkers(); refresh();
  const pend = DATA.filter(o => o.latitud == null); $('nPend').textContent = pend.length;
  $('pendList').innerHTML = pend.map(o => `<li><b>${esc(o.nombre)}</b><small>${esc(o.zona_documento)} — ${esc(o.observaciones)}</small><small><a href="${esc(gmapsUrl(o))}" target="_blank" rel="noopener">Buscar en Google Maps</a></small></li>`).join('');
  fitVisible(); initialBounds = map.getBounds();
  try { buildDistritos(await getJSON('data/distritos.geojson')); }
  catch (e) { console.error(e); toast('No se pudieron cargar los límites de los distritos; se muestran el mapa y los puntos.', 8000); $('chkDistritos').disabled = true; $('selDistrito').disabled = true; }
})();
})();
