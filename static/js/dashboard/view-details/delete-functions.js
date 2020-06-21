function cancelDelete() {
  $("#dlgViewDetails .confirm-delete").addClass("hidden");
}

function confirmDelete() {
	prepareDeleteFrm();
  $("#dlgViewDetails .confirm-delete").removeClass("hidden");
  $("#dlgViewDetails form textarea").focus();
}