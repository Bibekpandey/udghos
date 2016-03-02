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
  
  $('#save').show();
  $('#nameinfo').show();
  $('.info').fadeIn('fast');
});

$('#save').click(function(){
  $('#save, .info').hide();
  $('textarea').each(function(){
    var content = $(this).val();//.replace(/\n/g,"<br>");
    $(this).html(content);
    $(this).contents().unwrap();    
  }); 

  $('#edit').show(); 
});
