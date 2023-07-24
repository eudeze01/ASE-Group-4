console.log("Hello Admin");

let driver_transactions = [];

function loadDriverDetails() {
  fetch("/api/getAllDrivers")
    .then((r) => {
      if (r.ok) {
        r.json().then((data) => {
          const driver_t_body = document.getElementById("driver_t_body");
          driver_t_body.innerHTML = "";

          document.getElementById("spinner").classList.add("d-none");
          document.getElementById("driver_table").classList.remove("d-none");

          if (Array.isArray(data)) {
            data.forEach((d) => {
              const t_row = document.createElement("tr");

              const id = document.createElement("td");
              id.innerText = d.id;
              const name = document.createElement("td");
              name.innerText = d.driver_name;
              const email = document.createElement("td");
              email.innerText = d.email ? d.email : "No user account linked";
              const v_plate = document.createElement("td");
              v_plate.innerText = d.plate;
              const v_type = document.createElement("td");
              v_type.innerText = d.type;
              const v_model = document.createElement("td");
              v_model.innerText = d.model;

              t_row.appendChild(id);
              t_row.appendChild(name);
              t_row.appendChild(email);
              t_row.appendChild(v_plate);
              t_row.appendChild(v_type);
              t_row.appendChild(v_model);

              driver_t_body.appendChild(t_row);
            });
          }
        });
      }
    })
    .catch((r) => {
      console.log(r);
    });
}

function loadDriverTransactions() {
  fetch("/api/getDriverJourneys").then((r) => {
    if (r.ok) {
      driver_transactions = [];

      r.json().then((data) => {
        console.log(data);
        const driver_t_body = document.getElementById("trance_t_body");
        driver_t_body.innerHTML = "";

        document.getElementById("spinner_trans").classList.add("d-none");
        document.getElementById("trans_table").classList.remove("d-none");

        if (Array.isArray(data)) {
          data.forEach((d) => {
            driver_transactions.push({
              ...d,
              start_time: Date.parse(d.start_time),
              end_time: Date.parse(d.end_time),
            });
          });

          populateTransactionTable(driver_transactions);
          populateSummary(getSummaryForTransaction(driver_transactions));
        }
      });
    }
  });
}

function populateTransactionTable(data) {
  const driver_t_body = document.getElementById("trance_t_body");
  driver_t_body.innerHTML = "";

  if (Array.isArray(data)) {
    data.forEach((d) => {
      const t_row = document.createElement("tr");

      const v_id = document.createElement("td");
      v_id.innerText = d.v_id;

      const plate = document.createElement("td");
      plate.innerText = d.plate;

      const name = document.createElement("td");
      name.innerText = d.driver_name;

      const start_time = document.createElement("td");
      start_time.innerText = new Date(d.start_time).toUTCString();

      const end_time = document.createElement("td");
      end_time.innerText = new Date(d.end_time).toUTCString();

      const rating = document.createElement("td");
      rating.innerText = d.rating * 5 + " / 5";

      const fair = document.createElement("td");
      fair.innerText = d.fair;

      t_row.appendChild(v_id);
      t_row.appendChild(plate);
      t_row.appendChild(name);
      t_row.appendChild(start_time);
      t_row.appendChild(end_time);
      t_row.appendChild(rating);
      t_row.appendChild(fair);

      driver_t_body.appendChild(t_row);
    });
  }
}

function populateSummary(data) {
  const tot_fair = document.getElementById("tot_fair");
  const avg_fair = document.getElementById("avg_fair");
  const avg_rate = document.getElementById("avg_rating");
  const count = document.getElementById("jrn_count");
  if (data) {
    tot_fair.innerText = data.totalFair.toFixed(2) + " £";
    avg_fair.innerText = data.averageFair.toFixed(2) + " £";
    avg_rate.innerText = data.averageRating.toFixed(2) + " / 5";
    count.innerText = data.count;
  } else {
    tot_fair.innerText = "N/A";
    avg_fair.innerText = "N/A";
    avg_rate.innerText = "N/A";
    count.innerText = "N/A";
  }
}

function getSummaryForTransaction(data) {
  let total = 0;
  let avgRate = 0;
  if (Array.isArray(data) && data.length > 0) {
    total = data.reduce((p, cv) => p + cv.fair, 0);
    avgRate = data.reduce((p, cv) => p + cv.rating * 5, 0) / data.length;

    return {
      totalFair: total,
      averageFair: total / data.length,
      averageRating: avgRate,
      count: data.length,
    };
  }
}

document.addEventListener("DOMContentLoaded", (_this) => {
  loadDriverDetails();
  loadDriverTransactions();

  const btn_search_trans = document.getElementById("btn_search_trans");
  const search_input = document.getElementById("search_input");

  btn_search_trans.addEventListener("click", (e) => {
    const search_str = search_input.value.trim().toLowerCase();
    // console.log(search_str);
    const filtered = driver_transactions.filter((v) => {
      let plate_match = false;
      if (v.plate) {
        plate_match = String(v.plate).includes(search_str);
      }
      let driver_match = false;

      if (v.driver_name) {
        driver_match = String(v.driver_name).toLowerCase().includes(search_str);
      }

      return plate_match || driver_match;
    });

    // console.log(filtered);
    populateTransactionTable(filtered);
    // console.log(getSummaryForTransaction(filtered));
    populateSummary(getSummaryForTransaction(filtered));
  });
});
