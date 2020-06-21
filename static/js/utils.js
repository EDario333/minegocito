function valid_csrftoken() {
  /* ***********************************
  For these lines please see: 
  https://docs.djangoproject.com/en/2.0/ref/csrf/
  ************************************/
  var csrftoken = $("[name=csrfmiddlewaretoken]").val();

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
  /* ***********************************
  End lines
  ************************************/
}

function showLoader() {
  $.ajax({
    method: "GET",
    url: "/dashboard/processing",
    data: { user: "{{user}}"}
  })
  .done(function(result) {
    //$("section.content").empty();
    $("section.content").html(result);
  });
}

function validField(field) {
  val = $(field).val();
  return val != null && val != undefined && val.trim().length > 0;
}

function verifyPasswordStrength(valToVerify, disableBtn) {
  var strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#.\$%\^&\*\>\<\,\;\:\-\_])(?=.{8,})/;

  // contains six characters or more and has at least 
  // one lowercase and one uppercase alphabetical 
  // character or has at least one lowercase and one 
  // numeric character or has at least one uppercase 
  // and one numeric character. We’ve chosen to leave 
  // special characters out of this one.
  var mediumRegex = /^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})/;

  if (!strongRegex.test(valToVerify)) {
    $(disableBtn).attr("disabled", "true");
    $.ajax({
      method: "GET",
      url: "/translator/translate/",
      data: { msg: "Required password strength" }
    })
    .done(function(result) {
      show_msg_with_toastr("error", result);
    });
  }
  else
    $(disableBtn).removeAttr("disabled");
}

function verifyPasswordMatching(val1, val2, disableBtn) {
  if (val1 != val2) {
    $(disableBtn).attr("disabled", "true");
    $.ajax({
      method: "GET",
      url: "/translator/translate/",
      data: { msg: "Passwords does not match" }
    })
    .done(function(result) {
      show_msg_with_toastr("error", result);
    });
  }
  else
    $(disableBtn).removeAttr("disabled");
}

function retrieveWaitMsg() {
  $.ajax({
    method: "GET",
    url: "/translator/translate/",
    data: {msg: "Please wait"}
  })
  .done(function(result) {
    return result;
  });
  return "Cargando...";
}