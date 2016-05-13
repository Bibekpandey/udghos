$('#edit').click(function(){
  $('#edit').hide();
  $('#save').show();
  $('.box-profile').css("min-height", "500px");
  $('.hidden-text').show();
  $('.hidden-cross').show();
  $('.dataarea').each(function() {
    var content = $(this).html();
    $(this).html('<textarea name="'+$(this).attr('id')+'">' + content + '</textarea>');
  });  

  $('.datainfo').each(function(){
    var content = $(this).html();
    $(this).html('<input type="text" placeholder="'+$(this).attr('id')+'" name="'+$(this).attr('id')+'" value="'+content+'"/></input>');
  });
  
  $('#profile-image-form').show();
  $('#nameinfo').show();
  $('.info').fadeIn('fast');
});

$('#save').click(function(){
    $('#profile-image-form').hide();
    //$('#error').text('Changing profile...');
    var new_tag_ids = '';
    var removed_tag_ids = '';
    for(var x=0;x<g_new_tags.length;x++) new_tag_ids+=g_new_tags[x].id.toString()+',';
    for(var x=0;x<g_removed_tags.length;x++) removed_tag_ids+=g_removed_tags[x].id.toString()+',';
    $('#updateform').append(
            $('<input>').attr("type","hidden")
                    .attr("name", "new_tags")
                    .attr("value", new_tag_ids.substring(0, new_tag_ids.length-1)));
    $('#updateform').append(
            $('<input>').attr("type","hidden")
                    .attr("name", "removed_tags")
                    .attr("value", removed_tag_ids.substring(0, removed_tag_ids.length-1)));
    $.ajax({   
        type: 'POST',   
        url: '/complain/profile-update/',   
        data: $('#updateform').serialize(),
        success: function(data) { 
            //$('#error').text(data.error);
            if(data.success==true) {
                window.location="";
                $('#save, .infoo').hide();
                $('textarea').each(function(){
                var content = $(this).val();//.replace(/\n/g,"<br>");
                $(this).html(content);
                //  $(this).contents().unwrap();    
  }); 
                $('#edit').show(); 

            }
            else {
            }
            $('#picture_update').submit();
        },
        error: function(data) { alert(JSON.stringify(data));}
    }); 
});

//.............Profile IMAGE Display ..............///

$(function () {
    $(":file").change(function () {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = imageIsLoaded;
            reader.readAsDataURL(this.files[0]);
        }
    });
});

function imageIsLoaded(e) {
    $('.img-profile').attr('src', e.target.result);
};

