$.get("files/config.yml").done(function (data) {
  //loading content of the config file
  // var config_content = jsyaml.load(data);

  var dropdown = document.getElementById("selection");
  var schema_url = dropdown.value.toString();

  dropdown.addEventListener("change", function () {
    schema_url = dropdown.value.toString();
    //////////////////for using schematic API
    getRequestedJson(schema_url).then((tangled_tree_data) => {
      var chart_dta = chart(tangled_tree_data);
      createCollapsibleTree(chart_dta, schema_url);
    });
  });

  console.log(schema_url);

  //////////////////for using schematic API
  // getRequestedJson(schema_url).then((tangled_tree_data) => {
  //   var chart_dta = chart(tangled_tree_data);
  //   createCollapsibleTree(chart_dta, schema_url);
  // });
});
