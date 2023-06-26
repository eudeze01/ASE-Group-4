console.log("UI");

let mapObj;
let choosingStart = false,
  choosingDest = false;
let startMarker, destMarker;

// Elements
const input_start = document.getElementById("input_start");
const input_destination = document.getElementById("input_destination");
const btn_book_vehicle = document.getElementById("book_vehicle");
const btn_select_map_start = document.getElementById("btn_select_map_start");
const btn_select_map_destination = document.getElementById(
  "btn_select_map_destination"
);

export const InitializeUI = function init_UI(map) {
  //   console.log(map);
  mapObj = map;
  registerListeners();
  document.getElementById("input_start").disabled = true;
  document.getElementById("input_destination").disabled = true;
};

function setStartInputUI(latLng) {
  if (startMarker) {
    document.getElementById("input_start").value =
      latLng.lat() + ", " + latLng.lng();
  }
}

function setDestInputUI(latLng) {
  if (destMarker) {
    document.getElementById("input_destination").value =
      latLng.lat() + ", " + latLng.lng();
  }
}

function vehicleBooked(data) {
  enableControls(false);
  document.getElementById("vehicle_id").innerText = data.car_id;
  document.getElementById("time_to_arrive").innerText =
    Number(data.total_time.toFixed(2)) + " mins";
  document.getElementById("confirm_info").classList.remove("d-none");
}

function enableControls(enable = true) {
  input_start.disabled = !enable;
  input_destination.disabled = !enable;
  btn_book_vehicle.disabled = !enable;
  btn_select_map_start.disabled = !enable;
  btn_select_map_destination.disabled = !enable;
}

// TODO: Implement Validation
function validate() {
  if (!startMarker) {
    return { error: "" };
  }
}

function registerListeners() {
  // Listner for selecting start and destination on the map
  mapObj.addListener("click", (e) => {
    if (choosingStart) {
      if (startMarker) {
        startMarker.setMap(null);
        startMarker = null;
      }

      startMarker = new google.maps.Marker({
        position: e.latLng,
        map: mapObj,
      });
      mapObj.panTo(e.latLng);

      const infowindow = new google.maps.InfoWindow({
        content: "Start Location",
        ariaLabel: "Start",
      });

      infowindow.open({
        anchor: startMarker,
        mapObj,
      });

      setStartInputUI(e.latLng);
    } else if (choosingDest) {
      if (destMarker) {
        destMarker.setMap(null);
        destMarker = null;
      }

      destMarker = new google.maps.Marker({
        position: e.latLng,
        map: mapObj,
      });
      mapObj.panTo(e.latLng);

      new google.maps.InfoWindow({
        content: "End Location",
        ariaLabel: "Start",
      }).open({
        anchor: destMarker,
        mapObj,
      });
      setDestInputUI(e.latLng);
    }
  });

  const book_btn = document.getElementById("book_vehicle");
  book_btn.addEventListener("click", async () => {
    if (startMarker && destMarker) {
      let route = {
        source: {
          x: startMarker.getPosition().lat(),
          y: startMarker.getPosition().lng(),
        },
        destination: {
          x: 4.65465,
          y: 45.6544,
        },
      };

      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(route),
      };

      //   POST to /api/book to book vehicle
      fetch("/api/book", options).then((res) => {
        res.json().then((data) => {
          console.log(data);
          vehicleBooked(data);
        });
      });
    }
  });

  const set_map_start = document.getElementById("btn_select_map_start");
  set_map_start.addEventListener("click", () => {
    choosingStart = !choosingStart;
    choosingDest = false;

    if (choosingStart) {
      set_map_start.innerHTML = '<i class="bi bi-check-lg"></i>';
      set_map_dest.innerHTML = '<i class="bi bi-pin-map-fill"></i>';
    } else {
      set_map_start.innerHTML = '<i class="bi bi-pin-map-fill"></i>';
    }
  });

  const set_map_dest = document.getElementById("btn_select_map_destination");
  set_map_dest.addEventListener("click", () => {
    choosingDest = !choosingDest;
    choosingStart = false;

    if (choosingDest) {
      set_map_dest.innerHTML = '<i class="bi bi-check-lg"></i>';
      set_map_start.innerHTML = '<i class="bi bi-pin-map-fill"></i>';
    } else {
      set_map_dest.innerHTML = '<i class="bi bi-pin-map-fill"></i>';
    }
  });
}
