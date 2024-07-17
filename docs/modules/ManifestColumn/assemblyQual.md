---
datatable: true
layout: page
parent: ManifestColumn
title: assemblyQual
---

{% assign mydata=site.data.assemblyQual %} 
{: .note-title } 
>assemblyQual
>
>Assembly quality. The assembly quality category is based on sets of criteria outlined for each assembly quality category.High Quality- Multiple fragments where gaps span repetitive regions. Presence of the 23S, 16S and 5S rRNA genes and at least 18 tRNAs.Medium Quality- Many fragments with little to no review of assembly other than reporting of standard assembly statistics.Low Quality- Many fragments with little to no review of assembly other than reporting of standard assembly statistics. Assembly statistics include, but are not limited to, total assembly size, number of contigs, contig N50/L50, and maximum contig length. Example values - high-quality genome, medium-quality genome, low-quality genome [[Source]](nan)
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
  $('#myTable').DataTable({
    responsive: {
        details: {
            display: $.fn.dataTable.Responsive.display.modal( {
                header: function ( row ) {
                    var data = row.data();
                    return 'Details for '+data[0];
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
         targets: [4],
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