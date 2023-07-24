let records = [];

function loadPreviousJourneys() {
  fetch("/api/driverJourneyHistory").then((r) => {
    if (r.ok) {
      r.json().then((v) => {
        // records = v;
        records = [];
        const table_element = document.getElementById("pj_t_body");

        document.getElementById("spinner").classList.add("d-none");
        document.getElementById("table_view").classList.remove("d-none");

        if (Array.isArray(v)) {
          table_element.innerHTML = "";
          v.forEach((v) => {
            records.push({
              ...v,
              start_time: Date.parse(v.start_time),
              end_time: Date.parse(v.end_time),
            });

            const t_row = document.createElement("tr");
            const start_date = document.createElement("td");
            start_date.innerText =
              new Date(v.start_time).toLocaleString() + " UTC";
            const end_date = document.createElement("td");
            end_date.innerText = new Date(v.end_time).toLocaleString() + " UTC";
            const rating = document.createElement("td");
            rating.innerText = (v.rating * 5).toFixed(2) + "/ 5";
            const fair = document.createElement("td");
            fair.innerText = v.fair + "  £";

            t_row.appendChild(start_date);
            t_row.appendChild(end_date);
            t_row.appendChild(rating);
            t_row.appendChild(fair);

            table_element.appendChild(t_row);

            document.getElementById("total").innerText =
              "Total Earning : " + getSumOfFairs().toFixed(2) + " £";
            document.getElementById("today_earn").innerText =
              "Today's Earnings : " + getTodayEarnings().toFixed(2) + " £";
          });
        }

        // console.log(getSumOfFairs());

        console.log(records);
      });
    }
  });
}

function getSumOfFairs() {
  return records.reduce((p, c) => p + c.fair, 0);
}

function getTodayEarnings() {
  return records
    .filter((v) => v.end_time > new Date().setUTCHours(0, 0, 0, 0))
    .reduce((p, c) => p + c.fair, 0);
}

document.addEventListener("DOMContentLoaded", (_this, ev) => {
  loadPreviousJourneys();
});
