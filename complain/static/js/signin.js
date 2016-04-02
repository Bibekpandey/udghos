
$( "#signup" ).hide("fast");
$( "#click-signup" ).click(function() {
  $( "#signin" ).hide( "fast");
  $(".box-signin").css( "margin-top", "20%" );
  $( "#signup" ).show("fast");


});
$( "#click-signin" ).click(function() {
  $(".box-signin").css( "margin-top", "30%" );
	$( "#signup" ).hide("fast");
	$( "#signin" ).show("fast");

});

$( "#click-signup-link" ).click(function() {
  $( "#signin" ).hide( "fast");
  $(".box-signin").css( "margin-top", "20%" );
  $( "#signup" ).show("fast");

});
$( "#click-signin-link" ).click(function() {
  $(".box-signin").css( "margin-top", "30%" );
	$( "#signup" ).hide("fast");

	$( "#signin" ).show("fast");

});


var mq = window.matchMedia( "(min-width: 5000px)" );
if (mq.matches) {
	$(".icons").show("fast");

}
else {
	$(".icons").hide("fast");

}

function signUp() {
    $('#message').text("Signing up.. Please Wait..");
    alert($('#signup-form').serialize());

    $.post('/complain/signup/', $('#signup-form').serialize(), function(data) {
        $('#message').text(data.message);
        if(data.success) {
            window.location='/';
        }
        else {
            document.getElementById('signup-form').reset();  
            return false;
        }
    });
}

