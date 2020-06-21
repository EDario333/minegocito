function editData() {
  $('[data-toggle="tooltip"]').tooltip();

  //$('table.tbl-view-details').editableTableWidget();
  $(".edit").removeClass("hidden");
  $(".view").addClass("hidden");

  $("tr#rowBtnSave").removeClass("hidden");
  $("tr#rowBtnSave").removeAttr("hidden");

  $("#dlgViewDetails table.tbl-view-details").removeClass("table-striped");
  $("#dlgViewDetails table.tbl-view-details tbody tr td:first-child").removeClass("right-alignment");

  $("#dlgViewDetails form.update input")[2].select();
}

function cancelEdit() {
  $('[data-toggle="tooltip"]').tooltip();

  $(".edit").addClass("hidden");
  $(".view").removeClass("hidden");
  $("#dlgViewDetails table.tbl-view-details").addClass("table-striped");
  $("#dlgViewDetails table.tbl-view-details tbody tr td:first-child").addClass("right-alignment");

  $("tr#rowBtnSave").addClass("hidden");
  $("tr#rowBtnSave").attr("hidden", "true");
}