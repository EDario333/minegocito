function startTutorialFirstTime() {
  setTimeout(function () {
   $("#tutorialStep1").click();
  }, 500);
}

function continueFirstTutorial(step) {
  step += 1;
  setTimeout(function () {
   $("#tutorialStep" + step).click();
  }, 500);
}

function finishTheFirstTutorial(user) {
  $.ajax({
    method: "GET",
    url: "/users/check-first-tutorial-completed",
    data: {user: user}
  })
  .done(function(result) {
    //console.log(msg);
    if (result.status != undefined)
      show_msg_with_toastr("info", result.msg);
  });
}

function gotoStep1(user) {
  $('#tutorialStep1').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 0}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep2(user) {
  $('#tutorialStep2').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 1}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep3(user) {
  $('#tutorialStep3').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 2}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep4(user) {
  $('#tutorialStep4').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 3}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep5(user) {
  $('#tutorialStep5').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 4}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep6(user) {
  $('#tutorialStep6').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 5}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep7(user) {
  $('#tutorialStep7').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 6}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep8(user) {
  $('#tutorialStep8').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 7}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep9(user) {
  $('#tutorialStep9').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 8}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep10(user) {
  $('#tutorialStep10').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 9}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}

function gotoStep11(user) {
  $('#tutorialStep11').click();
  $(".modal-backdrop").remove();
  $.ajax({
    method: "GET",
    url: "/users/update-step-first-tutorial",
    data: {user: user, step: 10}
  })
  .done(function(msg) {
    //console.log(msg);
  });
}