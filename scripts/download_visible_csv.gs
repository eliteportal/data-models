# add this to download scripts without hidden rows or columns
function onOpen() {
  SpreadsheetApp.getUi().createMenu('⇩ M E N U ⇩')
      .addItem('👉 DownloadVisible Data as CSV', 'downloadCSVOnlyVisible')
      .addToUi();
}

function downloadCSVOnlyVisible() {
  const ss = SpreadsheetApp.getActiveSpreadsheet()
  const sh = ss.getActiveSheet()
  let source = []
  const sep = ',';
  sh.getDataRange().getValues().forEach((r, i) => {
    if (!sh.isRowHiddenByFilter(i + 1) && !sh.isRowHiddenByUser(i + 1)) {
      let prov = []
      r.forEach((c, j) => {
        if (!sh.isColumnHiddenByUser(j + 1)) {
          // Logger.log("Value of c: %s \nType : %s\nIs Number: %s", c, typeof c, isNaN(c))
          if (typeof c == 'string') { // Check if value is not a number
              c = c.replace(/\s{1,}[\t\r\n\f\v​]+/g, ''); // Clear all whitespace
              // Logger.log("first pass: %s", c)
              if (c.length === 0) { 
                  prov.push(''); // Empty cell
              } else {
                  if (c.includes(sep)) {
                      c = c.replace(/[\n\r]+/g, ' ').replace('"', '\\"'); // Replace newlines, escape quotes
                      prov.push(`"${c}"`); // Add quotes 
                  } else { 
                      c = c.replace(/[\n\r]+/g, ' ');  // Replace newlines
                      prov.push(c);
                  }
              }
          } else {
              prov.push(c); // Value is a number
          }
        }
      })
      source.push([prov])
    }
  })
  const content = source.map(r => r.join(sep) + '\n').join('');
  const type = 'csv'
  const mimeTypes = { csv: MimeType.CSV };
  const name = ss.getName() + ' ' + sh.getName() + '.csv'
  const id = DriveApp.createFile(name, content).getId();
  const blob = DriveApp.getFileById(id).getBlob();
  const infoHtml = {
    data: `data:${mimeTypes[type]};base64,` + Utilities.base64Encode(blob.getBytes()),
    filename: `${name}`,
  };
  const html = HtmlService.createHtmlOutput(`<a href="${infoHtml.data}" download="${infoHtml.filename}">${infoHtml.filename}</a>`)
    .setWidth(420).setHeight(100);
  SpreadsheetApp.getUi().showModalDialog(html, "Download your file ...")
}


# to add to a new file
# scriptID used to add library: 1jo0JCUzwpxKuKl7kpi1R37bNAmvbduWTJSx9d0lzlQG9iKZpjJpxF5w6

function onOpen() {
  SpreadsheetApp.getUi().createMenu('⇩ M E N U ⇩')
      .addItem('👉 DownloadVisible Data as CSV', 'toolbox.downloadCSVOnlyVisible')
      .addToUi();
}