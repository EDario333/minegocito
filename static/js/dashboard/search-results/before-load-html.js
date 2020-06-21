var msg_wait;

$.ajax({
  method: "GET",
  url: "/translator/translate/",
  data: { msg: "Please wait"}
})
.done(function(result) {
  msg_wait = result;
});

function showDetails(obj, module_name, can_edit, can_delete, enter_and_edit, enter_and_delete, itm_menu) {
  show_msg_with_toastr("info", msg_wait);

  data = { 
    obj: obj, can_edit: can_edit, can_delete: can_delete, 
    itm_menu: itm_menu
  }

  module_name_=module_name.toUpperCase();
  if (module_name_.includes('USERS'))
    module_name = 'users/admin';

  $.ajax({
    method: "GET",
    url: '/' + module_name + "/view-details",
    data: data
  })
  .done(function(result) {
    //$("#dlgSearchResults").modal("hide");
    //$("#dlgSearchResults").modal().hide();
    //console.log(result);
    $("div#divViewDetails").html(result);

    $("#dlgViewDetails table.tbl-view-details tbody tr td:first-child").addClass("right-alignment");
    if (enter_and_edit) {
      $("#dlgViewDetails a#actEditData").click();
      prepareEditFrm();
    }
    if (enter_and_delete) {
      $("#dlgViewDetails a#actDelete").click();
    }

    if (module_name_.includes('USERS')) {
      if (can_edit)
        $("form #actAssignGroup").click(function() {
          if (permissions_assigned)
            permissions_assigned = !confirm("Perderá los permisos asignados. ¿Desea continuar?");

          if (permissions_assigned)
            return false;

          $("form input[name='permissions']").val("");

          $('#dlgAssignGroup').modal('show'); 
          return false;
        });

      $("form a.permissions").click(function() {
        var changing_permissions = $(this).hasClass("change-permissions");

        if (changing_permissions) {
          if (group_assigned)
            group_assigned = !confirm("Perderá los permisos asignados con base en el grupo seleccionado. ¿Desea continuar?");

          if (group_assigned)
            return false;

          $("form p#divUserGroup").html("Ninguno");
        }

        show_msg_with_toastr("info", msg_wait);

        if (changing_permissions)
          $("form input[name='usergroup']").val("");

        user = $("#dlgViewDetails .modal-footer input[name='user']").val();

        $.ajax({
          method: "GET",
          url: "/permissions/get-permissions/",
          cache: false,
          data: { user: user }
        })
        .done(function(result) {
          toastr.clear();

          if (result.status == "success") {
            $('#dlgAssignPermissions div#divPermissions').html(result.html);

            if (changing_permissions) {
              $('#dlgAssignPermissions #lblHeader').html("Editar permisos");
              permissions = $("form input[name='permissions']").val();
            }
            else {
              $('#dlgAssignPermissions #lblHeader').html("Ver permisos");
              $('#dlgAssignPermissions input[type="checkbox"]').attr("disabled", "true");
              $('#dlgAssignPermissions #parSelectAll').remove();
              $('#dlgAssignPermissions #parSelectNone').remove();
              $('#dlgAssignPermissions .select-all-group').remove();
              $('#dlgAssignPermissions .select-none-group').remove();
            }

            if (changing_permissions && 
              permissions.length > 0) {
              permissions = permissions.split(",");
              tope = permissions.length;
              x = 0;
              for (; x < tope; x++)
                //$('#dlgAssignPermissions #permission' + permissions[x]).attr("checked", "true");
                $('#dlgAssignPermissions #permission' + permissions[x]).click();

              all_permissions_granted = x == permissions.length;
            }

            if (changing_permissions) {
              $("#dlgAssignPermissions div#divPermissions #actSelectall").click(function() {
                show_msg_with_toastr("info", msg_wait);

                chks = $("#dlgAssignPermissions input[name='permissions']");
                tope = chks.length;
                for (x = 0; x < tope; x++)
                  if (!chks[x].checked)
                    $(chks[x]).click();
                //$("#dlgAssignPermissions input[name='permissions']").click();

                $("#dlgAssignPermissions div#divPermissions #parSelectNone").show();
                $("#dlgAssignPermissions div#divPermissions .select-none").show();
                $("#dlgAssignPermissions div#divPermissions #parSelectAll").hide();
                $("#dlgAssignPermissions div#divPermissions .select-all").hide();
                all_permissions_granted = true;
                toastr.clear();
                return false;
              });

              $("#dlgAssignPermissions div#divPermissions #actSelectNone").click(function() {
                show_msg_with_toastr("info", msg_wait);

                chks = $("#dlgAssignPermissions input[name='permissions']");
                tope = chks.length;
                for (x = 0; x < tope; x++)
                  if (chks[x].checked)
                    $(chks[x]).click();
                //$("#dlgAssignPermissions input[name='permissions']:checked").removeAttr("checked");

                $("#dlgAssignPermissions div#divPermissions #parSelectNone").hide();
                $("#dlgAssignPermissions div#divPermissions .select-none").hide();
                $("#dlgAssignPermissions div#divPermissions #parSelectAll").show();
                $("#dlgAssignPermissions div#divPermissions .select-all").show();
                all_permissions_granted = false;
                toastr.clear();
                return false;
              });

              // ****************
              $("#dlgAssignPermissions div#divPermissions a.select-all-group").click(function() {
                show_msg_with_toastr("info", msg_wait);
                group = this.id;
                group = group.substr("actSelectNoneGroup".length-1);

                chks = $("#dlgAssignPermissions input[class='group" + group + "']");
                tope = chks.length;
                for (x = 0; x < tope; x++)
                  if (!chks[x].checked)
                    $(chks[x]).click();
                //$("#dlgAssignPermissions input[class='group" +group + "']").click();

                $("#dlgAssignPermissions div#divPermissions a#actSelectNoneGroup" + group).show();

                $("#dlgAssignPermissions div#divPermissions a#actSelectNoneGroup" + group).parent().show();

                $("#dlgAssignPermissions div#divPermissions a#actSelectAllGroup" + group).hide();
                toastr.clear();
                return false;
              });

              $("#dlgAssignPermissions div#divPermissions a.select-none-group").click(function() {
                show_msg_with_toastr("info", msg_wait);
                group = this.id;
                group = group.substr("actSelectAllGroup".length+1);

                chks = $("#dlgAssignPermissions input[class='group" + group + "']");
                tope = chks.length;
                for (x = 0; x < tope; x++)
                  if (chks[x].checked)
                    $(chks[x]).click();
                //$("#dlgAssignPermissions input[class='group" + group + "']").click();

                $("#dlgAssignPermissions div#divPermissions a#actSelectNoneGroup" + group).hide();

                $("#dlgAssignPermissions div#divPermissions a#actSelectAllGroup" + group).show();
                toastr.clear();
                return false;
              });
              // *****

              if (all_permissions_granted) {
                $("#dlgAssignPermissions div#divPermissions #parSelectNone").show();
                $("#dlgAssignPermissions div#divPermissions .select-none").show();
                $("#dlgAssignPermissions div#divPermissions #parSelectAll").hide();
                $("#dlgAssignPermissions div#divPermissions .select-all").hide();
              }
              else {
                $("#dlgAssignPermissions div#divPermissions #parSelectNone").hide();

                $("#dlgAssignPermissions div#divPermissions .select-none").hide();
              }
            }

            $('#dlgAssignPermissions').modal('show'); 
          }
          else
            show_msg_with_toastr(result.status, result.msg);

        });

        return false;
      });
    }
    else if (module_name_.includes("PROVIDERS"))
      $('.hide-contact-persons').hide();
    else if (module_name_.includes("PURCHASES"))
      $(".hide-purchased-products").hide();

    $("#dlgViewDetails").modal("show");
    toastr.clear();
    on_close_dlgViewDetails();
  });
  return false;
}

function showDetailsAnalytics(obj, itm_menu, module_name) {
  show_msg_with_toastr("info", msg_wait);

  data = { 
    obj: obj, can_edit: false, can_delete: false, 
    itm_menu: itm_menu
  }

  module_name_=module_name.toUpperCase();

  $.ajax({
    method: "GET",
    url: '/' + module_name + "/view-details",
    data: data
  })
  .done(function(result) {
    $("div#divViewDetails").html(result);

    $("#dlgViewDetails table.tbl-view-details tbody tr td:first-child").addClass("right-alignment");

    if (module_name_=="PURCHASES")
      $(".hide-purchased-products").hide();
    else if (module_name_=="SALES")
      $(".hide-sold-products").hide();

    $("#dlgViewDetails").modal("show");
    toastr.clear();
  });
  return false;
}

function showDetailsPurchasesAnalytics(obj, itm_menu) {
  showDetailsAnalytics(obj, itm_menu, "purchases");
  return false;
}

function showDetailsSalesAnalytics(obj, itm_menu) {
  showDetailsAnalytics(obj, itm_menu, "sales");
  return false;
}