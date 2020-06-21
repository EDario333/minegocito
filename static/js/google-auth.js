var googleUser = {};

var google_auth = function(attachTo) {
  gapi.load('auth2', function(){
    // Retrieve the singleton for the GoogleAuth library and set up the client.
    auth2 = gapi.auth2.init({
      client_id: '13309156621-egtd1tsk0mlmk1945jthu8q0s4pqluo2.apps.googleusercontent.com',
      cookiepolicy: 'single_host_origin',
      // Request scopes in addition to 'profile' and 'email'
      //scope: 'additional_scope'
    });
    attachSignin(document.getElementById(attachTo));
    document.getElementById(attachTo).click();
  });
};

function attachSignin(element) {
  //console.log(element.id);
  auth2.attachClickHandler(element, {},
    function(googleUser) {
      //document.getElementById(element.id).innerText = "Signed in: " +
          //googleUser.getBasicProfile().getName();
      // Sign in the user if they are currently signed in.
      if (auth2.isSignedIn.get() == true) {
        //auth2.signIn();
        // alert("aqui");
        register_user_on_my_db(googleUser);
        // login_using_google(googleUser);
      }
      else {
        register_user_on_my_db(googleUser);
      }
    }, 
    function(error) {
      //alert(JSON.stringify(error, undefined, 2));
    });
}

function register_user_on_my_db(googleUser) {
  bp = googleUser.getBasicProfile();
  fn = bp.getGivenName();
  ln = bp.getFamilyName();
  //gender = bp.getGender();
  //dob = response.birthday;
  uid = bp.getId();
  email = bp.getEmail();
  recaptcha_response=document.getElementById("txtRecaptchaResponse").value;

  data = {
    first_name: fn, last_name: ln, 
    uid: uid,
    register_with_google: true, email: email,
    "g-recaptcha-response": recaptcha_response
  };
  // console.log(data);
    
  valid_csrftoken();
  $.ajax({
    method: "POST",
    url: "/users/register/google/",
    data: data
  })
  .done(function(result) {
    $("#dlgCreateUserAccount").modal("hide")
    show_msg_with_toastr(result.status, result.msg);
    if (result.status=="success")
      login_using_google(googleUser);
    //document.write(result);
  });
  //send_notifs_to_my_friends();
}

function login_using_google(googleUser) {
  bp = googleUser.getBasicProfile();
  email = bp.getEmail();

  valid_csrftoken();

  csrftoken = $("#dlgLogin [name=csrfmiddlewaretoken]").val();

  data = {
    email: email, login_with_google: true, 
    csrfmiddlewaretoken: csrftoken
  };

  $.ajax({
    method: "POST",
    url: "/users/login/google/",
    data: data
  })
  .done(function(result) {
    $("#dlgLogin").modal("hide");

    if (result.show_modal != undefined && result.show_modal) {     
      $.ajax({
        method: "GET",
        url: "dashboard/choose-app-version",
        data: data
      })
      .done(function(result_inner) {
        $(document.body).append(result_inner);
        $("#" + result.modal_name + " input[name='email']").val(result.email);
        $("#" + result.modal_name + " input[name='password']").val(result.password);
        $("#" + result.modal_name).modal("toggle");
      });
    }
    else if (result.status != undefined) {
      show_msg_with_toastr(result.status, result.msg);
    }
    else {
      data = "?email=" + email + "&login_with_google=true";
      data += "&csrfmiddlewaretoken=" + csrftoken;
      data += "&app_version=" + result.app_version;
//        data += "&expires=" + result.expires;

      location.href = "/dashboard/index/" + data;
    }
  });
  //send_notifs_to_my_friends();
}