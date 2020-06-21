toastr.clear();

$('[data-toggle="tooltip"]').tooltip();

//Exportable table
$('.js-exportable').DataTable({
  dom: 'Bfrtip',
  responsive: true,
  buttons: [
    'copy', 'csv', 'excel', 'pdf', 'print'
  ]
});

$.ajax({
  method: "GET",
  url: "/translator/many/",
  data: { msgs: "Show,entries,Search,Showing,to,of,Previous,Next,Copy,Print"}
})
.done(function(result) {
  result = result.split(',');

  if ($("#tblResults_length label")[0] != undefined) {
 		$("#tblResults_length label")[0].childNodes[0].textContent = result[0] + ": ";
  	$("#tblResults_length label")[0].childNodes[2].textContent = result[1];
  }

  $("#tblResults_filter label")[0].childNodes[0].textContent = result[2] + ": ";

  msg = $("#tblResults_info")[0].innerText;

  strings = msg.split(' ');

  msg = result[3];
  for (x = 0; x < strings.length; x++) {
    str = strings[x];
    if (str == "Showing")
      msg += ' ' + strings[x+1];
    else if (str == "to")
      msg += result[4] + ' ' + strings[x+1];
    else if (strings[x] == "of")
      msg += result[5] + ' ' + strings[x+1];
    else if (strings[x] == "entries")
      msg += result[1];
  }

  $("#tblResults_info")[0].innerText = msg;
  $("#tblResults_previous")[0].childNodes[0].textContent = result[6];
  $("#tblResults_next")[0].childNodes[0].textContent = result[7];

 	$("#tblResults_wrapper .dt-buttons a.buttons-copy span")[0].innerText = result[8];
 	$("#tblResults_wrapper .dt-buttons a.buttons-print span")[0].innerText = result[9];
});