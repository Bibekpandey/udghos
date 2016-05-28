$('input').on('input', function() {
    $('#signup-message').text('');
    $('#signin-message').text('');
})

$( "#signup" ).hide("fast");
$( "#click-signup" ).click(function() {
  $( "#signin" ).hide( "fast");
  $(".box-signin").css( "margin-top", "10%" );
  $( "#signup" ).show("fast");


});
$( "#click-signin" ).click(function() {
  $(".box-signin").css( "margin-top", "12%" );
	$( "#signup" ).hide("fast");
	$( "#signin" ).show("fast");

});

$( "#click-signup-link" ).click(function() {
  $( "#signin" ).hide( "fast");
  $(".box-signin").css( "margin-top", "10%" );
  $( "#signup" ).show("fast");
});

$( "#click-signin-link" ).click(function() {
  $(".box-signin").css( "margin-top", "12%" );
	$( "#signup" ).hide("fast");

	$( "#signin" ).show("fast");

});


function signin() {
    $('#float-notification').show();
    $('.notification-heading').text("Signing in.. Please wait...");
    var inputuser = document.getElementById("inputEmail").value;
    $('.notification-body').fadeIn()
    $('.notification-body').text("Welcome back, " +inputuser);
    $('#float-notification').fadeOut(7000);

    $.post('/login/', $('#signin-form').serialize(), function(data) {
        if(data.success) {
            window.location = "/";
        }
        else {
            if(data.message=="NOT VERIFIED") {
                window.location = "/not-verified/";
            }
            $('#float-notification').show();
            $('.notification-heading').text(data.message);
            $('#float-notification').fadeOut(7000);
            $('.notification-body').hide();

        }
    });
    return false;
}


var mq = window.matchMedia( "(min-width: 5000px)" );
if (mq.matches) {
	$(".icons").show("fast");

}
else {
	$(".icons").hide("fast");

}

function signUp() {
    $('#float-notification').show();
    $('.notification-heading').text("Signing up.. Please Wait...");
    $('#float-notification').fadeOut(7000);

    $.post('/complain/signup/', $('#signup-form').serialize(), function(data) {
        $('.notification-heading').text(data.message);
        $('.notification-body').text("Please use another username");
        if(data.success) {
            window.location='/not-verified/';
        }
        else {
            document.getElementById('signup-form').reset();
            $('.notification-heading').text(data.message);
            return false;
            $('#signup-message').hide();
            $('#float-notification').show();  
            $('.notification-heading').text(data.message);
            $('#float-notification').fadeOut(7000);

            return false;
        }
    });
}

