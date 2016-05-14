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
    $.post('/login/', $('#signin-form').serialize(), function(data) {
        if(data.success) {
            window.location = "/";
        }
        else {
            if(data.message=="NOT VERIFIED") {
                window.location = "/not-verified/";
            }
            $('#signin-message').text(data.message);
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
    $('#signup-message').text("Signing up.. Please Wait..");

    $.post('/complain/signup/', $('#signup-form').serialize(), function(data) {
        $('#message').text(data.message);
        if(data.success) {
            window.location='/not-verified/';
        }
        else {
            document.getElementById('signup-form').reset();
            $('#signup-message').text("Can't sign up right now. Please try Social signup");
            return false;
            $('#signup-message').hide();
            $('#float-notification').show();  
            $('#notification-text').text(data.message);
            setTimeout(function() { $('#float-notification').delay(100).fadeOut(); }, 900);
            $('#float-notification').hide();
            return false;
        }
    });
}

