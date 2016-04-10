$('#edit').click(function(){
  $('#edit').hide();
  $('.dataarea').each(function() {
    var content = $(this).html();
    $(this).html('<textarea>' + content + '</textarea>');
  });  

  $('.datainfo').each(function(){
    var content = $(this).html();
    $(this).html('<input type="text" placeholder="'+$(this).attr('id')+'" name="'+$(this).attr('id')+'" value="'+content+'"/></input>');
  });
  
  $('#profile-image-form').show();
  $('#save').show();
  $('#nameinfo').show();
  $('.info').fadeIn('fast');
});

$('#save').click(function(){
    $('#profile-image-form').hide();
    $('#error').text('Changing profile...');
    $.ajax({   
        type: 'POST',   
        url: '/complain/profile-update/',   
        data: $('#updateform').serialize(),
        success: function(data) { 
            $('#error').text(data.error);
            if(data.success==true) {
                window.location="";
                $('#save, .info').hide();
                $('textarea').each(function(){
                var content = $(this).val();//.replace(/\n/g,"<br>");
                $(this).html(content);
                $(this).contents().unwrap();    
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
