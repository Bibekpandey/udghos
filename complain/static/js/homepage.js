$( "#show-btn" ).hide("fast");
$( "#form-title" ).hide("fast");

$( ".form-control" ).click(function() {
  	$( "#show-btn" ).show("fast");
  	$( "#form-title" ).show("fast");

});
$("#comment-click").click(function(){
	$("#display-form").show("fast");
});

$('#myModal').on('shown.bs.modal', function () {
  $('#myModal').appendTo("body").modal('show');
  $('#myInput').focus()
  $('#myModal').modal({keyboard: true})

})

$('#myModalImage').on('shown.bs.modal', function () {
  $('#myModalImage').appendTo("body").modal('show');
  $('#myInput').focus()
  $('#myModalImage').modal({keyboard: true})
  $
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

$(document).keyup(function(e) { 
    if (e.keyCode == 27) { 
        $('#warning-box').empty();
    $('#warning-box').hide();
    $('#mask').css({"z-index":1});
    $('#mask').hide();
    } 
});

//..........IMAGE ON MODAL.............//

var arrimg=[];
var newarrimg=[];

$(function () {
     
    $(":file").change(function () {
     
        console.log(this.files);
         arrimg=this.files;
        newarrimg.push(arrimg);
        
        console.log(newarrimg);
        if (this.files) {
console.log(this.files.length);            
            for(i=0; i<=this.files.length;i++){
            var reader = new FileReader();
           // reader.onload = imageIsLoaded;
            reader.onload = showUploadedItem;
            reader.readAsDataURL(this.files[i]);
            }
        }
    });
});

function showUploadedItem (source) {
    console.log("archivos");
    console.log(source);
      var list = document.getElementById("image-list"),
        li   = document.createElement("li"),
        img  = document.createElement("img");  
      img.src = source.target.result;
      li.appendChild(img);
    list.appendChild(li);
  } 


