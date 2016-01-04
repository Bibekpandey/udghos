$(document).ready(function(){
  	$('[data-toggle="popover"]').popover();  

    $(".dropdown").on("show.bs.dropdown", function(event){
        var x = $(event.relatedTarget).text(); // Get the button text
        alert("You clicked on: " + x);
    });
});


