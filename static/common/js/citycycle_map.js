/*
 * CityCycle - shared Leaflet helper.
 *
 * Loaded once from userapp/master.html and adminapp/master.html, after leaflet.js.
 * Pages only call:   var map = CityCycleMap.createMap('container-id', {center: [lat, lng], zoom: 12});
 *
 * Tile URL / attribution / API key come from Django settings (.env) through the
 * <script id="citycycle-map-config"> JSON block rendered by the master templates.
 */
(function (window, document) {
  'use strict';

  var config = {};
  try {
    var cfgEl = document.getElementById('citycycle-map-config');
    if (cfgEl) { config = JSON.parse(cfgEl.textContent) || {}; }
  } catch (e) {
    console.warn('CityCycleMap: could not read map config', e);
  }

  // ── Coordinate validation ────────────────────────────────────────────────
  function toNumber(v) {
    if (v === null || v === undefined || v === '') { return null; }
    var n = Number(v);
    return isFinite(n) ? n : null;
  }
  function validLat(v) { var n = toNumber(v); return n !== null && n >= -90 && n <= 90; }
  function validLng(v) { var n = toNumber(v); return n !== null && n >= -180 && n <= 180; }
  function validCoords(lat, lng) { return validLat(lat) && validLng(lng); }

  // ── Small on-map message (missing key / tiles failing) ───────────────────
  function showNotice(map, message) {
    var box = map.getContainer();
    if (box.querySelector('.citycycle-map-notice')) { return; }
    var div = document.createElement('div');
    div.className = 'citycycle-map-notice';
    div.style.cssText = 'position:absolute;left:50%;top:10px;transform:translateX(-50%);' +
      'z-index:1000;max-width:90%;padding:8px 14px;border-radius:8px;background:#fff3cd;' +
      'color:#664d03;border:1px solid #ffecb5;font:13px/1.4 sans-serif;text-align:center;' +
      'box-shadow:0 2px 8px rgba(0,0,0,.15);pointer-events:none;';
    div.textContent = message;
    box.appendChild(div);
  }

  function addTileLayer(map) {
    if (!config.tileUrl) {
      showNotice(map, 'Map tiles are not configured. Set MAPTILER_API_KEY in the .env file and restart the server.');
      console.warn('CityCycleMap: MAPTILER_API_KEY is not set - no tile layer added.');
      return null;
    }
    var loaded = 0, failed = 0;
    var layer = L.tileLayer(config.tileUrl, {
      attribution: config.attribution || '',
      maxZoom: config.maxZoom || 20
    });
    layer.on('tileload', function () { loaded++; });
    layer.on('tileerror', function () {
      failed++;
      if (loaded === 0 && failed === 3) {
        showNotice(map, 'Map tiles failed to load. Check MAPTILER_API_KEY and its allowed origins in the MapTiler dashboard.');
        console.error('CityCycleMap: tile requests are failing (invalid key, blocked origin or no network).');
      }
    });
    layer.addTo(map);
    return layer;
  }

  /**
   * Create a map inside #containerId.
   * Returns the L.Map, or null when Leaflet is missing / the container does not exist.
   * Calling it twice for the same container returns the existing map
   * (no "Map container is already initialized" error).
   */
  function createMap(containerId, options) {
    options = options || {};
    if (typeof window.L === 'undefined') {
      console.error('CityCycleMap: Leaflet (L) is not loaded.');
      return null;
    }
    var el = document.getElementById(containerId);
    if (!el) { return null; }
    if (el._citycycleMap) { return el._citycycleMap; }
    if (el._leaflet_id) { return null; }  // initialised by something else

    var center = options.center || [23.022505, 72.571362];   // Ahmedabad
    if (!validCoords(center[0], center[1])) { center = [23.022505, 72.571362]; }

    var map = L.map(el).setView(center, options.zoom || 12);
    el._citycycleMap = map;
    addTileLayer(map);

    // Layout may still be settling (admin theme, tabs) - make sure tiles fill the box.
    setTimeout(function () { map.invalidateSize(); }, 250);
    window.addEventListener('load', function () { map.invalidateSize(); });
    return map;
  }

  window.CityCycleMap = {
    config: config,
    createMap: createMap,
    validLat: validLat,
    validLng: validLng,
    validCoords: validCoords
  };
})(window, document);
