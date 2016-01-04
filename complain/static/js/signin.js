$( "#signup" ).hide("fast");

$( "#click-signup" ).click(function() {
  $( "#signin" ).hide( "fast");
  	$( "#signup" ).show("fast");

});
$( "#click-signin" ).click(function() {
	$( "#signup" ).hide("fast");

	$( "#signin" ).show("fast");

});

$( "#click-signup-link" ).click(function() {
  $( "#signin" ).hide( "fast");
  	$( "#signup" ).show("fast");

});
$( "#click-signin-link" ).click(function() {
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

