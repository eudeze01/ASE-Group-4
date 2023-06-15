import * as db from "./dbstub.js";

// Import Google Maps
((g) => {
  var h,
    a,
    k,
    p = "The Google Maps JavaScript API",
    c = "google",
    l = "importLibrary",
    q = "__ib__",
    m = document,
    b = window;
  b = b[c] || (b[c] = {});
  var d = b.maps || (b.maps = {}),
    r = new Set(),
    e = new URLSearchParams(),
    u = () =>
      h ||
      (h = new Promise(async (f, n) => {
        await (a = m.createElement("script"));
        e.set("libraries", [...r] + "");
        for (k in g)
          e.set(
            k.replace(/[A-Z]/g, (t) => "_" + t[0].toLowerCase()),
            g[k]
          );
        e.set("callback", c + ".maps." + q);
        a.src = `https://maps.${c}apis.com/maps/api/js?` + e;
        d[q] = f;
        a.onerror = () => (h = n(Error(p + " could not load.")));
        a.nonce = m.querySelector("script[nonce]")?.nonce || "";
        m.head.append(a);
      }));
  d[l]
    ? console.warn(p + " only loads once. Ignoring:", g)
    : (d[l] = (f, ...n) => r.add(f) && u().then(() => d[l](f, ...n)));
})({ key: "API-KEY", v: "beta" });

const { Map } = await google.maps.importLibrary("maps");
const { Marker } = await google.maps.importLibrary("marker");

// Initialize variables
let map;
let vehicleMarkers = [];
const centerPos = { lat: 51.5195786, lng: -0.0606907 };

// Initialize Map
async function initMap() {
  map = new Map(document.getElementById("GMap"), {
    zoom: 13,
    center: centerPos,
    mapId: "DEMO_MAP_ID",
  });
}

initMap();
retrieveVehicles();

function removeVehicleMarkers() {
  vehicleMarkers.forEach((e) => {
    e.setMap(null);
  });
}

function retrieveVehicles() {
  removeVehicleMarkers();
  vehicleMarkers = [];
  db.getVehicles().forEach((e) => {
    let pos = { lat: e.lat, lng: e.lng };
    vehicleMarkers.push(
      new Marker({
        position: pos,
        map,
      })
    );
  });
}
