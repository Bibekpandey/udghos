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
