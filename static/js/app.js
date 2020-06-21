function config_toastr() {
  // Please see http://codeseven.github.io/toastr/demo.html for more details
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
}

config_toastr();

function validField(field_id) {
  val = $(field_id).val();
  return val != null && val != undefined && val.trim().length > 0;
}

// level could be:
// success
// info
// warning
// error

// Please see http://codeseven.github.io/toastr/demo.html for more details
function show_msg_with_toastr(level, msg) {
  toastr[level](msg);
}

function inactiveAllNavigationItems() {
  $("nav.site-navigation li").removeClass("active");
}

// function registerDashboardActions() {
//   $(".menu a.action").click(function() {
//     action = this.href.substring(this.href.indexOf("#")+1);
//     showLoader();

//     data = {
//       user: "{{user}}", app_version: "{{app_version}}",
//       itm_menu: this.id
//     };

//     $.ajax({
//       method: "GET",
//       url: action,
//       data: data
//     })
//     .done(function(result) {
//       //$("section.content").empty();
//       $("div.menu li.active").removeClass("active");
//       $("section.content").html(result);
//       if ($("section.content form") != undefined)
//         if ($("section.content form input")[0] != undefined)
//           $("section.content form input")[0].focus();
//     });
//     return false;
//   });
// }