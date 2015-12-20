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
                alert(data);
                inc = parseInt(data);
                var votes = parseInt($("#vote_"+item+"_"+id).text());
                votes+=inc;
                $("#vote_"+item+"_"+id.toString()).text(votes.toString());

            }
        );
    }

