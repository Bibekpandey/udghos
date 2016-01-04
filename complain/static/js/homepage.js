$( "#show-btn" ).hide("fast");
$( "#form-title" ).hide("fast");

$( ".form-control" ).click(function() {
  	$( "#show-btn" ).show("fast");
  	$( "#form-title" ).show("fast");

});
$("#comment-click").click(function(){
	$("#display-form").show("fast");
});


var windowWidth = $(window).width();
    if(windowWidth >= 768){
		$("#navcolor2").hide("fast");
		$("#navcolor1").show("fast");
	}
    else if(windowWidth < 768){
    $( "#navcolor2" ).show("fast");
    $( "#navcolor1" ).hide("fast");
 }

$(function () {
  $('.net-vote').tooltip("show")
})