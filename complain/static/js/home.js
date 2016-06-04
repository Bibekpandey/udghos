function submitPost() {
        // first collect tags
        var selected = document.getElementsByClassName('selected-tags');
        var tagids =[];
        for(var x=0;x<selected.length;x++) {
            tagids.push(selected[x].getAttribute('id').replace('selected-tag-', ''))
        }

        // then collect targets
        selected = document.getElementsByClassName('selected-targets');
        var targetids =[];
        for(var x=0;x<selected.length;x++) {
            targetids.push(selected[x].getAttribute('id').replace('selected-target-', ''))
        }

        // check if title is empty
        var tit = $('input[name=title]').val();
        if(tit.trim() =='') {
            $('#title-warning').show();
            return false;
        }
        // now check if description is empty
        var desc = $('textarea[name=content]').val();
        if (desc.trim() == '') {
            $('#description-warning').show();
            return false;
        }
        if(tagids.length==0) {
            //$('#tags-warning').show();
            //return false;
        }

        if(targetids.length==0) {
            //$('#targets-warning').show();
           // return false;
        }
        var taginputelem = document.createElement('input');
        taginputelem.setAttribute("type", "hidden");
        taginputelem.setAttribute("name", "tagids");
        taginputelem.setAttribute("value", tagids.toString());

        var targetinputelem = document.createElement('input');
        targetinputelem.setAttribute("type", "hidden");
        targetinputelem.setAttribute("name", "targetids");
        targetinputelem.setAttribute("value", targetids.toString());

        var form = document.getElementById("thread-form");
        form.appendChild(taginputelem);
        form.appendChild(targetinputelem);
    }    


//////////////////////////////////////////////////////////////////////////////////////////////

    var g_end_of_posts = false;

    var g_select_items = {
        'tag':{max:4, current:[]},
        'target':{max:1,current:[]}
    };

    $('#tagbox').on('input', function(){$('#tags-suggest-list').show(); getItems('tag');});
    $('#tagbox').focus(function() {$('#targets-suggest-list').hide();});

    $('#targetbox').on('input', function(){$('#targets-suggest-list').show();getItems('target');}); 
    $('#targetbox').focus(function() { $('#tags-suggest-list').hide();});

    window.onload = function()  { 
	$('html').click(function() {
		$('#tags-suggest-list').hide();
            	$('#tagbox,#targetbox').val('');
            	$('#targets-suggest-list').hide();
	});
	$('#tags-suggest-list,#targets-suggest-list').click(function(event) { event.stopPropagation(); });

        $('html,body').animate({scrollTop:0}, 500);
        $('.comment-form').hide();
        //$('#error').text(window.localStorage.getItem("message"));
        //window.localStorage.setItem("message","");
        showRecent(); 
    };

    var g_thread_container = "recent-threads";
    var g_thread_type = 'recent';
    var g_earliertop = window.scrollY;  // global to check direction of scroll
    var g_lastId;
    var g_lastVote;

    var g_tags_selected = [];

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
            var data = {earlierthan:g_lastId.toString(),
                lessthan:g_lastVote.toString()};
            g_lastId = null;
            getAndRenderThreads(g_thread_type, data);
        }
    }

    function showTop() {
	    g_end_of_posts = false;
        g_thread_container = "top-threads";
        g_thread_type = 'top';
        g_earliertop = 0;
        $('#recent-threads').empty();
        $('#favourite-threads').empty();
        var query='';
        if (g_lastId != undefined && g_lastVote != undefined) {
            query = 'earlierthan='+g_lastId.toString()+'&';
            query += 'lessthan='+g_lastVote.toString();
        }
        getAndRenderThreads('top', query);
    }

    function showRecent() {
	g_end_of_posts = false;
        g_thread_container = "recent-threads";
        g_thread_type = "recent";
        g_earliertop = 0;
        $('#top-threads').empty();
        $('#favourite-threads').empty();
        var query='';
        if (g_lastId != undefined)
            query = 'earlierthan='+g_lastId.toString();
        else query = '';
        getAndRenderThreads('recent', query);
    }
    

    function showFavs() {
	g_end_of_posts = false;
        g_thread_container = "favourite-threads";
        g_thread_type = "favourite";
        g_earliertop = 0;
        $('#top-threads').empty();
        $('#recent-threads').empty();
        var query='';
        if (g_lastId != undefined)
            query = 'earlierthan='+g_lastId.toString();
        else query = '';
        getAndRenderThreads('favourite', query);

    }

    function getAndRenderThreads(type, data) {
        // now get threads from server
        if (g_end_of_posts) {
            return;
        }

        $.get('/complain/threads/'+type, data, function(data) {
            g_lastId = data.lastid;
            if(g_lastId==null) g_end_of_posts = true;
            g_lastVote = data.lastvote;
            if(data.end==true) {
                g_end_of_posts=true;
            }
            for(var x=0;x<data.threads.length;x++) {
                add_item(data.threads[x], g_thread_container, data.authenticated);
            }


            $('.fb-share').click(function(e){
                        var img = $(this).attr('data-image');
                            e.preventDefault();
                            FB.ui(
                            {
                            method: 'feed',
                            name: $(this).attr('data-title'),
                            link: 'http://udghos.com/thread/'+$(this).attr('data-id'),
                            caption: ($(this).attr('supported')=="supported"?'I supported this thread on ' :'') + 'udghos.com',
                            description: $(this).attr('data-content'),
                            picture:(img!=''?'http://udghos.com/media/'+img:'http://udghos.com/static/img/navbarlogo.png'),
                            message: ''
                            });
            });

        });
    }
function getItems(itemtype) {
        var query = $('#'+itemtype+'box').val();
        if (query != '') {
            $.get('/complain/'+itemtype+'s/?query='+query, function(data) {
                renderItem(itemtype, data);
            });
        }
    }

    function renderItem(itemtype, data) {
        var items = data.items;
		var ul = document.getElementById(itemtype+'s-suggest-list');
		ul.innerHTML="";
        for(var x in items) {
            if (g_select_items[itemtype].current.indexOf(items[x].name)<0 && g_select_items[itemtype].current.length < g_select_items[itemtype].max)
			    ul.innerHTML += '<li class="suggestion" id="'+itemtype+'-'+items[x].id+'" onclick="addItem(this,\''+itemtype+'\')">'+items[x].name+'</li>';
        }
    }
	
	function addItem(elem, itemtype) {
        $('#'+itemtype+'s-warning').hide();
        $('#'+itemtype+'box').val('');
        $('#'+itemtype+'s-suggest-list').empty();
        g_select_items[itemtype].current.push(elem.innerHTML);
        var id = elem.getAttribute('id').replace(itemtype+'-', '');
		var items_elem = document.getElementById(itemtype+'s-chosen');	
		items_elem.innerHTML+= '<span id="selected-'+itemtype+'-'+id+'"class="btn selected-'+itemtype+'s">' +elem.innerHTML+ '<button type="button" class="close my-close" ><span onclick="removeItem(\''+id+'\''+',\''+itemtype+'\', \''+elem.innerHTML+'\')" aria-hidden="true">&times;</span></button></span>';
	}

    function removeItem(id, itemtype, name) {
        var index = g_select_items[itemtype].current.indexOf(name);
        g_select_items[itemtype].current.splice(index, 1);
        $('#selected-'+itemtype+'-'+id).remove();
    }

    function profile_add_tags() {
            var id = $("input[name=uid]").val();
            window.localStorage.setItem("edit", "ok");
            window.location = "profile/"+id;
        }

