function get_csrf(){
        var a = document.getElementsByTagName("input");
        for(x in a)
        {
            if(a[x].getAttribute("type")=="hidden")
            {
                return a[x].value;
                break;
            }
        }
    }

    function vote(id, vote_type, item)
    {
        var inc;
        $.post("/complain/vote/",
            {
                object_id:id,
                csrfmiddlewaretoken:get_csrf(),
                type:vote_type,
                vote_item:item
            }, function(data, status) { 
                inc = parseInt(data);
                var votes = parseInt($("#vote_"+item+"_"+id).text());
                votes+=inc;
                $("#vote_"+item+"_"+id.toString()).text(votes.toString());

            }
        );
    }

function toggleComments(id) {
        $.post("/complain/get-comments/", 
            {"csrfmiddlewaretoken":get_csrf(), "threadid":id},
            function(data){
                $("#thread-comments"+id.toString()).html('');
                var comments = data.comments;
                $.each(comments, function(index, comment) {
                    appendComment($("#thread-comments"+id.toString()), comment);
                });
        });
        $("#display-form"+id.toString()).toggle("fast", function(){});
}

function postComment(id, user) {
    var txtarea = $("#comment-box"+id.toString());
    $.post("/complain/comment/",
            {"csrfmiddlewaretoken":get_csrf(), 
            "thread_id":id,
            "comment":txtarea.val()
            },
            function(data) {
                txtarea.val('');
                var comment = data.comment;
                appendComment($("#thread-comments"+id.toString()), comment);
                var numcmts = $("#num-comments"+id.toString());
                var num = parseInt(numcmts.text());
                numcmts.text(num+1);
                $("#comment-text"+id.toString()).text(num==0?" Comment":" Comments");
            }
    );
}

function appendComment(elem, commentobj) {
    var temp = document.createElement("div");
    var cmmtdiv = document.createElement("div");
    cmmtdiv.className = "comment";
    var userspan = document.createElement("span");
    userspan.innerHTML = commentobj.user;
    userspan.className = "comment-user";
    var datespan = document.createElement("span");
    datespan.innerHTML = commentobj.date;
    datespan.className = "comment-date";
    var txtdiv = document.createElement("div");
    txtdiv.innerHTML = commentobj.comment;
    txtdiv.className = "comment-text";
    cmmtdiv.appendChild(userspan);
    cmmtdiv.appendChild(datespan);
    cmmtdiv.appendChild(txtdiv);
    temp.appendChild(cmmtdiv);
    elem.append(temp.innerHTML);
}

function images_html(images) {
    var html = '';
    for(var x=0;x<images.length;x++) {
                html+='<a href="#myModalImage"><img src="../media/'+images[x]+'" height="50%" width="50%" data-toggle="modal" data-target="#myModalImage" data-keyboard="true"></img></a><br>' +
                '<div class="modal fade" id="myModalImage" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">'+
                  '<div class="modal-dialog modal-custom" role="document">'+
                    '<div class="modal-content">'+
                      '<div class="modal-post">'+
                        '<button type="button" class="close my-close close-image" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
                      '</div>'+
                      '<div class="row">'+
                        '<div class="col-md-8">'+
                          '<img class="post-image" src="../media/'+images[x]+'"></img>'+
                        '</div>'+
                        
                        '</div>'+
                      '</div>'+
                    '</div>'+
                  '</div>';
    }
    return html;
}

function generate_thread(threadobj, auth) {
    var thread_str = '<div class="box thread" id="thread-'+threadobj.id+'">'+
          '<div class="stbody">'+
            '<div id="recent" class="tab-pane fade in active">'+
              '<div class="stimg">'+
                '<img class="img-circle" src="/media/'+threadobj.user.image+'" width=50 height=50/>'+
                '</div>'+

              '<div id="textst" class="sttext">'+
                '<a href="/complain/thread/'+threadobj.id.toString()+'">'+
                '<div class="post-title">'+
                    (threadobj.title||threadobj.content)+
                '</div>'+
                '</a>'+
                '<div class="post-body">'+
                    '<span class="sttime"> &nbsp;'+threadobj.time+'</span>'+
                    '<span>by</span>'+
                    '<a href="/complain/profile">'+
                    '<span class="heading-property heading-post">'+threadobj.user.name+'</span></a>'+
                '</div>'+
                '<div class="post-content">'+
                 threadobj.content+
                '</div><br>'+
           images_html(threadobj.images)+
        '<div class="sttime">'+
                '</div>'+
                '<div class="row">'+
                  '<div class="display-tag">'+
                    '<span id="tag-post2" class="glyphicon glyphicon-tags"></span>';
                for(var x in threadobj.tags) {
                    thread_str+= '<a class="tagname tagname2" href="#">'+ threadobj.tags[x].name+'</a>';
                }
                thread_str+='</div>'+
                '</div>'+
              '</div>'+
            '</div>'+
          '</div>'+
          '<div class="row">'+
            '<div class="icons-ld">'+
                    '<a id="action-element" href="javascript:void()" onclick="'+ (auth==true?'vote('+threadobj.id+', \'upvote\', \'thread\')':'popMessage(this, \'You must be logged in!! \')')+'">'+
                      '<span class="glyphicon glyphicon-thumbs-up" aria-hidden="true"></span>'+
                    '</a>'+
                    '<span class="net-vote" data-toggle="tooltip" data-placement="right" id="vote_thread_'+threadobj.id+'">'+threadobj.votes+'</span>'+
                    '<a id="action-element" href="javascript:void()" onclick="'+ (auth==true?'vote('+threadobj.id+', \'downvote\', \'thread\')':'popMessage(this, \'You must be logged in!! \')')+'">'+
                      '<span class="glyphicon glyphicon-thumbs-down" aria-hidden="true"></span>'+
                    '</a>'+
                  
              '</div>'+
            '<div class="post-action">'+
              '<div class="comment-section">'+
                '<a href="javascript:void()" onclick="toggleComments('+threadobj.id+')">&nbsp;<span class="glyphicon glyphicon-comment" aria-hidden="true"></span>'+
                  '<span id="num-comments'+threadobj.id+'">'+threadobj.num_comments+'</span><span id="comment-text'+threadobj.id+'"> Comment'+(threadobj.num_comments!=1?'s':'')+'</span>'+
                '</a>'+
              '</div>'+
              '<div class="share">'+
                '<button class="facebook shadow" onclick="return fbs_click()" target="_blank"></button>'+
                '<button class="twitter shadow"></button>'+
              '</div>'+
            '</div>'+
          '</div>'+
          '<div id="display-form'+threadobj.id+'" class="comment-form">'+
            '<div id="thread-comments'+threadobj.id+'"></div>'+
            (auth==true?
            '<textarea id="comment-box'+threadobj.id+'" class="form-comment" placeholder="Your comment here."></textarea>'+
            '<button onclick="postComment('+threadobj.id+', \''+threadobj.user.name+'\')">Comment</button>':'')
            +
            
          '</div>'+
        '</div>';
    return thread_str;
}

function add_item(threadobj, divParentId, authenticated) {
    var elem = document.getElementById(divParentId);
    elem.innerHTML+=generate_thread(threadobj, authenticated);
}

function popMessage(elem, msg) {
    var child = elem.childNodes[0];
    var newdiv = document.createElement('div');
    newdiv.style.position="absolute";
    newdiv.style.color="#e33";
    newdiv.style.padding="1px";
    newdiv.style.fontSize="0.9em";
    newdiv.style.width="175px";
    newdiv.style.zIndex="100";
    newdiv.innerHTML = msg;
    newdiv.style.backgroundColor="#333";
    newdiv.style.border="solid 2px #555";
    newdiv.style.borderRadius="3px";
    child.appendChild(newdiv);
    setTimeout(function() { $(newdiv).delay(500).fadeOut(); newdiv.parentNode.removeChild(newdiv); }, 900);
    //$(newdiv).hide().delay(1000).fadeOut();
}
