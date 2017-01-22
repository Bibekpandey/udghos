function clickEdit(){
  $('#edit').hide();
  $('#save').show();
  $('.box-profile').css("min-height", "550px");
  $('#bloodgroup').css("display","none");
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
}

function checkEdit() {
    if(window.localStorage.getItem("edit") == "ok") {
        window.localStorage.setItem("edit", undefined);
        clickEdit();
    }
}

$('#edit').click(clickEdit);

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

// JS for the profile page
        $('#tagbox').on('input', getTags);

        var g_lastId;
        var g_tagedit =false;
        var g_tags_selected = [];
        var g_current_tags = [];
        var g_new_tags = [];
        var g_removed_tags = [];
        var g_earliertop = window.scrollY;

        $('.taginfo').each(function(index, element) {
            var parts = $(element).val().split(',');
            g_current_tags.push({name:parts[0], id:parseInt(parts[1])});

        });

        function getUserThreads(querydata) {
            var temp = location.href.split('/');
            var id = temp[temp.length-2];
            $.get('/complain/threads/user/'+id+'/', querydata, function(data) {
                g_lastId = data.lastid;
                for(var x = 0;x<data.threads.length;x++) {
                    add_item(data.threads[x], "recent-threads", data.authenticated);
                }
        // set fb-click function
$('.fb-share').click(function(e){
                        var img = $(this).attr('data-image');
                            e.preventDefault();
                            FB.ui(
                            {
                            method: 'feed',
                            name: $(this).attr('data-title')+ ' -- Support and Solve!!',
                            link: 'http://udghos.com/thread/'+$(this).attr('data-id'),
                            caption: ($(this).attr('data-supported')=="supported"?$('#userfullname').val()+' supported this thread on ' :'') + 'udghos.com',
                            description: $(this).attr('data-content')+ '... '+ $(this).attr('data-requiredvotes')+' more supports required for Action',
                            picture:(img!=''?'http://udghos.com/media/'+img:'http://udghos.com/static/img/navbarlogo.png'),
                            message: ''
                            });
            });

            });
        }
        window.onscroll = function() {
            // first get direction of scroll
            var curr = window.scrollY;
            if (curr <= g_earliertop) {
                return;
            }
            g_earliertop = curr;
            var elems = document.getElementsByClassName('box thread');
            var last = elems[elems.length-1];

            var lastRect = last.getBoundingClientRect();
            var windowH = window.innerHeight;
            if(lastRect.top <= 0.85*windowH) {
                if(g_lastId==null) return;
                var data = {earlierthan:g_lastId.toString()};
                g_lastId = null;
                getUserThreads(data);
            }
        }

function getTags() {
        var query = $('#tagbox').val();
        if (query != '') {
            $.get('/complain/tags?query='+query, function(data) {
                renderTags(data);
            });
        }
    }

    function renderTags(data) {
        var tags = data.items;
		var ul = document.getElementById('tags-suggest-list');
		ul.innerHTML="";
        for(var x in tags) {
            if (!tagInArr(tags[x], g_current_tags) && !tagInArr(tags[x], g_new_tags) || tagInArr(tags[x], g_removed_tags)) {
			    ul.innerHTML += '<li id="tag-'+tags[x].id+'" onclick="selectTag(this)">'+tags[x].name+'</li>';
            }
        }
    }
	
    function drawTagBoxes(tags) {
        $(tags).each(function(index, element) {
            drawTabBox(element.id, element.name);
        });
    }
    function drawTabBox(id, txt) {
        var tags_elem = document.getElementById('tags-chosen');	
		tags_elem.innerHTML+= '<span id="selected-'+id+'"class="btn selected-tags"> <span onclick="location=\'/threads/tagged/'+txt+'\'">'+txt+ '</span><button type="button" class="close my-close" id="close-tag"><span class="hidden-cross" onclick="removeTag(\''+id+'\''+',\''+txt+'\')" aria-hidden="true">&times;</span></button></span>';

    }
	function selectTag(elem) {
        $('#tags-warning').hide();
        $('#tagbox').val('');
        $('#tags-suggest-list').empty();
        var tag = {name:elem.innerHTML, id:parseInt(elem.id.split('-')[1])};

        // first remove if it is in removed array
        if(tagInArr(tag, g_removed_tags)) {
            removeTagFromArr(tag, g_removed_tags);
        }

        if(!tagInArr(tag, g_new_tags) && !tagInArr(tag, g_current_tags)) {
            g_new_tags.push(tag);
        }
        var id = elem.getAttribute('id').replace('tag-', '');
        drawTabBox(id, elem.innerHTML);
	}

    function tagInArr(tag, arr) {
        for(var x=0;x<arr.length;x++) {
            if(tag.name==arr[x].name && tag.id==arr[x].id)
                return true;
        }
        return false;
    }

    function removeTagFromArr(tag, arr) {
        for(var x=0;x<arr.length;x++) {
            if(tag.name==arr[x].name && tag.id==arr[x].id) {
                arr.splice(x, 1);
                return;
            }
        }
    }
    function removeTag(id, tagname) {
        var tag = {id:parseInt(id), name:tagname};
        if(tagInArr(tag, g_new_tags)) {
            removeTagFromArr(tag, g_new_tags);
            $('#selected-'+id).remove();
        }
        //var index = g_tags_selected.indexOf(tagname);
        //g_tags_selected.splice(index, 1);
        // check if it is in current or not
        if(tagInArr(tag, g_current_tags)) {
            g_removed_tags.push(tag);
            $('#selected-'+id).remove();
        }
    }

