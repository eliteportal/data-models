---
datatable: true
layout: page
parent: ' template'
title: analysis results metadata template
---

{% assign mydata=site.data.analysis_results_metadata_template %} 
{: .note-title } 
>analysis results metadata template
>
>Template for analysis and results [[Download]](https://github.com/eliteportal/data-models/raw/refs/heads/main/elite-data/manifest-templates/EL_template_AnalysisResultsMetadataTemplate.xlsx)
<table id="myTable" class="display" style="width:100%">
    <thead>
    {% for column in mydata[0] %}
        <th>{{ column[0] }}</th>
    {% endfor %}
    </thead>
    <tbody>
    {% for row in mydata %}
        <tr>
        {% for cell in row %}
            <td>{{ cell[1] }}</td>
        {% endfor %}
        </tr>
    {% endfor %}
    </tbody>
</table>

<script type="text/javascript">
  var pages = [];
  $('#myTable').DataTable({
    responsive: {
        details: {
            display: $.fn.dataTable.Responsive.display.modal( {
                header: function ( row ) {
                    var data = row.data();
                    return 'Details for '+data[0]+' ';
                }
            } ),
            renderer: $.fn.dataTable.Responsive.renderer.tableAll({
                tableClass: "table"
            })
        }
    },
   "deferRender": true,
   "columnDefs": [
      {
         targets: 0,
         render : function(data, type, row, meta){
            if(type === 'display' & $.inArray( data, pages) != -1){
               return $('<a>')
                  .attr('href',row[7]+'/'+data)
                  .text(data)
                  .wrap('<div></div>')
                  .parent()
                  .html();}
             else {
               return data;
            }
         }
      },
      {
        targets: [6,7],
          render : function(data, type, row, meta){
         if(type === 'display' & data != 'Sage Bionetworks'){
            return $('<a>')
               .attr('href', data)
               .text(data)
               .wrap('<div></div>')
               .parent()
               .html();}
         if(type === 'display' & data == 'Sage Bionetworks'){
             return $('<a>')
                .attr('href', 'https://sagebionetworks.org/')
                .text(data)
                .wrap('<div></div>')
                .parent()
                .html();

         } else {
            return data;
         }
      }
   }
   ]
});
</script>