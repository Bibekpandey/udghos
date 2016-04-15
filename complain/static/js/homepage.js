$( "#show-btn" ).hide("fast");
$( "#form-title" ).hide("fast");

$( ".form-control" ).click(function() {
  	$( "#show-btn" ).show("fast");
  	$( "#form-title" ).show("fast");

});
$("#comment-click").click(function(){
	$("#display-form").show("fast");
});

$(document).ready(function(){
  $('.notifications').popover({ 
    html : true,
    content: function() {
      return $('#popover_notification_content').html();
    }
  });
});

$('#myModal').on('shown.bs.modal', function () {
  $('#myModal').appendTo("body").modal('show');
  $('#myInput').focus()
  $('#myModal').modal({keyboard: true})

})

$('#myModalImage').on('shown.bs.modal', function () {
  $('#myModalImage').appendTo("body").modal('show');
  $('#myInput').focus()
    $('#myModalImage').modal({keyboard: false})

})

$('#textbox').click(function() {
    $('#boxtypetag').css({
        position: "absolute",
        top: (this.offsetTop + this.offsetHeight) + "px",
        left: this.offsetLeft + "px"
    });
    $('#boxtypetag').animate({
            height: 'toggle'
    });
    
});

$('#textbox').on('keypress',function(){
    $('#boxtag').css({
        position: "absolute",
        top: (this.offsetTop + this.offsetHeight) + "px",
        left: this.offsetLeft + "px"
    });
    $('#boxtypetag').hide();
    $('#boxtag').show();
});

$("body").click(function(){
    $('#boxtag').hide();
});

$("#close-tag").click(function(){
        $("#remove-tag").remove();
});




