function drawTable(data, selectedDataType) {
    //create table
    if ($('#toggle-table').is(":empty")) {
        $('#toggle-table').append('<button id="toggle-attributes-table" onclick="toggleAttributeTable(this.id)">Show Attribute Table</button>');
    }

    all_attribute_info = d3.group(data, (d) => d.Component)

    //when the filter changes, apply filter effect from dropdown
    $("#filterBy").change(function (e) {
        var dropdownSelection = document.getElementById("filterBy")
        var dropdownVal = dropdownSelection.value;

        //remove previous table 
        d3.select('#table').select('#jsonTable').remove();
        //load new table
        var attribute_to_load = getAttributes(all_attribute_info, selectedDataType, dropdownVal)
        createTable(attribute_to_load)
    })


    //create new graph by default 
    //this part gets triggered when users collapse/expand a node
    var dropdownSelection = document.getElementById("filterBy")
    var dropdownVal = dropdownSelection.value;
    d3.select('#table').select('#jsonTable').remove();
    var attribute_to_load = getAttributes(all_attribute_info, selectedDataType, dropdownVal);
    createTable(attribute_to_load)

}

//filter attribute table 
function getAttributes(all_attribute_info, datatype, opt) {
    if (opt == "Required Attributes") {
        var attributes_to_load = all_attribute_info
            .get(datatype)
            .filter((d) => d.Required == "True");
        return attributes_to_load;
    } else if (opt == "Conditionally Required Attributes") {
        var attributes_to_load = all_attribute_info
            .get(datatype)
            .filter((d) => d.Cond_Req == "True");
        return attributes_to_load;
    } else if (opt == "Required and Conditionally Required Attributes") {
        var attributes_to_load = all_attribute_info
            .get(datatype)
            .filter((d) => d.Required === "True" || d.Cond_Req === "True");
        return attributes_to_load;
    } else if (opt == "All Attributes") {
        var attributes_to_load = all_attribute_info.get(datatype);
        return attributes_to_load;
    }
}

//format truncated rows 
function formatTruncatedRows() {
    const isEllipsisActive = e => {
        return (e.offsetWidth < e.scrollWidth);
    }

    $("td").each(function (index, object) {
        if (isEllipsisActive(object)) {
            $(object).addClass('truncated')
        } else {
            $(object).removeClass('truncated')
        }

    })

}


//toggle attribute table by toggling class attached to "Show attribute table" button
function toggleAttributeTable() {
    if ($('#chart-placeholder').hasClass('show-attributes-table')) {
        $('#chart-placeholder').removeClass('show-attributes-table')
        $('#toggle-attributes-table').text('Show Attribute Table')
    } else {
        $('#chart-placeholder').addClass('show-attributes-table');
        $('#toggle-attributes-table').text('Hide Attribute Table')
        formatTruncatedRows();
    }

}

//toggle text in attribute table
function toggleText(object) {
    //configure toggle button (+ / -)
    $(".toggle-row").click(function () {
        $(this).parent('td').toggleClass('expanded');

        if ($(this).parent('.expanded').length) {
            $(object).addClass('truncated')
            $(this).html("-")
        } else {
            $(this).html("+")
        }
    })
}

//remove "No row to show" sign 
function RemoveNoRowToShow() {
    var placeholderText = $("#placeholder p");
    if (placeholderText.length > 0) {
        $("#placeholder p").remove()
    }
}

//add "No row to show" sign 
function AddNowRowToShow() {
    var placeholder = $("#placeholder");

    // if "no row to show" sign does not already exist
    if (($('#placeholder p').length == 0)) {
        placeholder.append('<p id="no-row-sign">No Row to show</p>');
    }
}

//Actually creating the attribute table
function createTable(object) {
    //show the top part of the table 
    $('#table').append('<table id="jsonTable"><thead><tr></tr></thead><tbody></tbody></table>');

    if (object[0] != null) {
        $.each(Object.keys(object[0]), function (index, key) {
            //ignore emtpy key like ""
            if (key.length > 0) {
                $('#jsonTable thead tr').append('<th>' + key + '</th>');
            }
        });
        $.each(object, function (index, jsonObject) {
            if (Object.keys(jsonObject).length > 0) {
                var tableRow = '<tr>';

                $.each(Object.keys(jsonObject), function (i, key) {
                    //ignore emtpy key like ""
                    if (key.length > 0) {
                        var td_class = "col-" + i;
                        tableRow += `<td class=${td_class}>` + jsonObject[key]
                        tableRow += `<button class="toggle-row">&plus;</button></td>`
                    }

                });
                tableRow += "</tr>";
                $('#jsonTable tbody').append(tableRow);
            }
        });

        console.log('this is working, if statement')

        RemoveNoRowToShow();

    }//if there's no attributes to show, we could show a line that says "no row to show"
    else {
        console.log('this is working, else statement');

        AddNowRowToShow();
    }

    //add additional formats
    formatTruncatedRows();

    //toggle text
    toggleText(object);


}