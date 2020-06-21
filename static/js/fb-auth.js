// All these lines were taken from:
// https://developers.facebook.com/docs/facebook-login/web

// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {
  //console.log('statusChangeCallback');
  //console.log(response);
  // The response object is returned with a status field that lets the
  // app know the current login status of the person.
  // Full docs on the response object can be found in the documentation
  // for FB.getLoginStatus().
  if (response.status === 'connected') {
    // Logged into your app and Facebook.
    //testAPI();
    //return response;
    //register_user_on_my_db();
    login_using_fb();
  } 
  else {
    // The person is not logged into your app or we are unable to tell.
    //document.getElementById('status').innerHTML = 'Please log into this app.';

    permissions = 
      'public_profile,email,user_gender,user_friends,'+
      'user_age_range,user_birthday';

    FB.login(function(response) {
      if (response.status === 'connected') {
        // Logged into your app and Facebook.
        //document.getElementById('status').innerHTML = 'yeeeja!';
        //testAPI();
        //return response;
        //console.log(response);
        register_user_on_my_db();
      } 
      else {
        // The person is not logged into this app or we are unable to tell. 
        //document.getElementById('status').innerHTML = ':(';
      }
    }, {scope: permissions});
  }
}

// This function is called when someone finishes with the Login
// Button.  See the onlogin handler attached to it in the sample
// code below.
function checkLoginState() {
  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });
}

window.fbAsyncInit = function() {
  FB.init({
    appId      : '460075351479081',
    cookie     : true,  // enable cookies to allow the server to access 
                        // the session
    xfbml      : true,  // parse social plugins on this page
    version    : 'v3.2' // The Graph API version to use for the call
  });

  // Now that we've initialized the JavaScript SDK, we call 
  // FB.getLoginStatus().  This function gets the state of the
  // person visiting this page and can return one of three states to
  // the callback you provide.  They can be:
  //
  // 1. Logged into your app ('connected')
  // 2. Logged into Facebook, but not your app ('not_authorized')
  // 3. Not logged into Facebook and can't tell if they are logged into
  //    your app or not.
  //
  // These three cases are handled in the callback function.

  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });

};

// Load the SDK asynchronously
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "https://connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

// Here we run a very simple test of the Graph API after login is
// successful.  See statusChangeCallback() for when this call is made.
function testAPI() {
  //console.log('Welcome!  Fetching your information.... ');
  FB.api('/me', function(response) {
    //console.log('Successful login for: ' + response.name);
    //document.getElementById('status').innerHTML = 'Thanks for logging in, ' + response.name + '!';
    return response;
  });
}

function send_notifs_to_my_friends() {
  fields = 
    'first_name,last_name,email';

  FB.api('/me/friends?fields=' + fields, function(response) {
    console.log("Friends: ");
    console.log(response);
  });
}

function register_user_on_my_db() {
  // alert("register_user_on_my_db");
  fields = 
    'first_name,last_name,email,gender,' +
    'age_range,birthday,picture';// +
    //'name,middle_name,short_name';

  FB.api('/me/?fields='+fields, function(response) {
    fn = response.first_name;
    ln = response["last_name"];
    gender = response.gender;
    dob = response.birthday;
    uid = response.id;
    email = response.email;
    profile_picture = response.picture;
    recaptcha_response=document.getElementById("txtRecaptchaResponse").value;

    data = {
      first_name: fn, last_name: ln, 
      gender: gender, dob: dob, uid: uid,
      register_with_fb: true, email: email,
      profile_picture: profile_picture,
      "g-recaptcha-response": recaptcha_response
    };
    
    valid_csrftoken();
    $.ajax({
      method: "POST",
      url: "/users/register/fb",
      data: data
    })
    .done(function(result) {
      $("#dlgCreateUserAccount").modal("hide")
      show_msg_with_toastr(result.status, result.msg);
      //document.write(result);
    });
    //send_notifs_to_my_friends();
  });
}

function login_using_fb() {
  fields = 'email,picture';

  FB.api('/me/?fields='+fields, function(response) {
    email = response.email;
    // console.log(response);
    profile_picture = response.picture;

    valid_csrftoken();

    csrftoken = $("#dlgLogin [name=csrfmiddlewaretoken]").val();

    data = {
      email: email, login_with_fb: true, 
      csrfmiddlewaretoken: csrftoken,
      profile_picture: profile_picture
    };

    $.ajax({
      method: "POST",
      url: "/users/login/fb",
      data: data
    })
    .done(function(result) {
      $("#dlgLogin").modal("hide");
      //$(document).html(result);

      if (result.show_modal != undefined && result.show_modal) {
        //$("#" + result.modal_name + " input[name='app-version']").val(result.app_version);
        //$("#" + result.modal_name + " input[name='expires']").val(result.expires);
        
        $.ajax({
          method: "GET",
          url: "dashboard/choose-app-version",
          data: data
        })
        .done(function(result_inner) {
          //node = document.createElement("div");
          //node.appendChild(result);
          $(document.body).append(result_inner);
          //$("#divDlgChooseAppVersion").append(result_inner);
          $("#" + result.modal_name + " input[name='email']").val(result.email);
          $("#" + result.modal_name + " input[name='password']").val(result.password);
          $("#" + result.modal_name).modal("toggle");
        });
      }
      else if (result.status != undefined) {
        show_msg_with_toastr(result.status, result.msg);
      }
      else {
        //document.documentElement.innerHTML = result;
        //$(".page-loader-wrapper").remove();
        data = "?email=" + email + "&login_with_fb=true";
        data += "&csrfmiddlewaretoken=" + csrftoken;
        data += "&app_version=" + result.app_version;
//        data += "&expires=" + result.expires;

        location.href = "/dashboard/index/" + data;
      }
    });
    //send_notifs_to_my_friends();
  });
}