function showMainPanel() {
	showLoader();
  $.ajax({
    method: "GET",
    url: "/dashboard/main-panel",
    data: { user: "{{user}}"}
  })
  .done(function(result) {
    //$("section.content").empty();
    $("section.content").html(result);
    $("div.menu li.active").removeClass("active");
    $("div.menu a#lnkHome").parent().addClass("active");
  });
  return false;
}