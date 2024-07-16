let table = document.getElementById("csv-data");
let url =
  "https://raw.githubusercontent.com/Sage-Bionetworks/data_curator_config/main/dcc_config.csv";
let dropdown = document.getElementById("selection");

// fetch(url)
//   .then((response) => response.text())
//   .then((data) => {
//     let rows = data.split("\n");
//     for (let i = 0; i < rows.length; i++) {
//       let cells = rows[i].split(",");
//       let row = table.insertRow();
//       for (let j = 0; j < 5; j++) {
//         let cell = row.insertCell();
//         cell.innerText = cells[j];
//       }
//     }
//   })
//   .catch((error) => console.log(error));

var schemaOptions = [];

fetch(url)
  .then((response) => response.text())
  .then((data) => {
    let rows = data.split("\n");
    for (let i = 0; i < rows.length; i++) {
      let cells = rows[i].split(",");
      for (let j = 0; j < cells.length; j++) {
        if (j == 0 && i > 0) {
          var text = cells[j];
          var opt = document.createElement("option");
          opt.textContent = text;
          opt.value = cells[j + 2];
          dropdown.appendChild(opt);
        }
      }
    }
  })
  .catch((error) => console.log(error));

console.log(dropdown);

// $(".dropdown").on("show.bs.dropdown", function (event) {
//   var x = $(event.relatedTarget).text(); // Get the text of the element
// });

// var selectedValue = document.getElementById("dropdown");

// console.log(selectedValue);
