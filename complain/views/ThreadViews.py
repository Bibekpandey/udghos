from django.http import JsonResponse, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q
from complain.models import *
NEW_THREADS = 3 # new number of threads when scrolled in browser

def get_thread_json(request):
    if request.user.is_authenticated():auth=True
    else: auth=False
    try:
        threadid = int(request.GET['id'])
        thread = Thread.objects.get(pk=threadid)
        return JsonResponse({"thread":thread_to_dict(request.user, thread, less=False),"authenticated":auth})
    except (ValueError, KeyError):
        return JsonResponse({"success":False, "message":"Invalid request"}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({"success":False, "message":"Thread doesnot exist"}, status=404)


def get_threads_json(request):
    # first check if its search query 
    auth=True if request.user.is_authenticated() else False
    query = request.GET.get('query', '')
    earlierthan = request.GET.get('earlierthan', '')
    kwargs = {}
    orderby = ['-time']
    if earlierthan.strip()!='':
        try:
            earlierthan = int(earlierthan)
            kwargs['id__lt'] = earlierthan
        except:
            return JsonResponse({'threads':[]})
    if query.strip()!='':
        words = list(map(lambda x: x.strip(),query.split(' ')))
        full = ' '.join(words)
        q = Q()
        q |= Q(title__icontains=full)
        for word in words:
            q |= Q(title__icontains=word)

        result = get_threads(request.user, NEW_THREADS, orderby, kwargs, [q])
        return JsonResponse({'threads':result['threads'], 
            'end':result['end'], 'authenticated':auth, 
            'lastid':result['lastid'],
            'lastvote':result['lastvote']
        }) 

    # if not search, check tag query
    tagname = request.GET.get('tagname', '')
    tagname = tagname.strip()
    if tagname!='':
        q = Q(tags__name__icontains=tagname)
        result = get_threads(request.user, NEW_THREADS, orderby, kwargs, [q])
        return JsonResponse({'threads':result['threads'], 
            'end':result['end'], 'authenticated':auth, 
            'lastid':result['lastid'],
            'lastvote':result['lastvote']
        })
    return JsonResponse({'threads':[]})


def get_recent_threads(request):
    #print('in get recent ')
    # auth is to check user login which lets like/comment
    if request.user.is_authenticated():auth=True
    else:auth=False
    orderby = ['-time']
    try:
        earlier = int(request.GET['earlierthan'])
        filterby = {'id__lt':earlier}
        result = get_threads(request.user, NEW_THREADS, orderby, filterby)
        return JsonResponse({'threads':result['threads'], 
            'end':result['end'], 'authenticated':auth, 
            'lastid':result['lastid'],
            'lastvote':result['lastvote']
        }) 
    except ValueError: # invalid get parameter
        #print('invalid')
        return JsonResponse({'status':False, 
                        'message':'Invalid request parameter'},
                        status=404)
    except KeyError:# earlierthan is not specified
        #print('earlierthan not specified');
        result = get_threads(request.user, 5, orderby, {}) # initial display threads=5
        return JsonResponse({'threads':result['threads'], 
            'end':result['end'], 'authenticated':auth,
            'lastid':result['lastid'],
            'lastvote':result['lastvote']
        })

def get_user_threads(request, userid):
    if request.user.is_authenticated():
        auth = True
        try:
            userid = int(userid)
        except:
            pass
        orderby = ['-time']
        filterby = {'account__pk':int(userid)}
        try:
            earlier = int(request.GET['earlierthan'])
            filterby['id__lt'] = earlier
            result = get_threads(request.user, NEW_THREADS, orderby, filterby)
        except KeyError: # means no earlierthan
            result = get_threads(request.user, 5, orderby, filterby)
        finally:
            return JsonResponse({'threads':result['threads'], 
                'end':result['end'], 'authenticated':auth,
                'lastid':result['lastid'],
                'lastvote':result['lastvote']
            })

    else:
        return redirect('signin')


def get_top_threads(request):
    earlier = request.GET.get('earlierthan','').strip()
    lessthan = request.GET.get('lessthan', '').strip()
    filterby={}
    if earlier!='' and lessthan!='':
        try:
            earlier = int(earlier)
            lessthan = int(lessthan)
            filterby['votes__lt'] = lessthan+1
            filterby['id__lt'] = earlier
        except:
            return JsonResponse({'threads':[], 'authenticated':True})
    try:
        orderby = ['-votes', '-time']
        result = get_threads(request.user, NEW_THREADS, orderby, filterby)
        return JsonResponse({'threads':result['threads'], 
            'end':result['end'], 'authenticated':request.user.is_authenticated(),
            'lastid':result['lastid'],
            'lastvote':result['lastvote']
        })

    except Exception as e: # invalid get parameter
        return JsonResponse({'status':False, 
                        'message':repr(e)+'Invalid request parameter'},
                        status=404)



def get_favourite_threads(request):
    if request.user.is_authenticated():
        acc = Account.objects.get(user=request.user)
        tags = acc.tags_followed.all()
        orderby = ['-time']
        earlierthan = request.GET.get('earlierthan', '').strip()
        kwargs = {}
        if earlierthan!='':
            try:
                earlierthan = int(earlierthan)
            except:
                return JsonResponse({'threads':[], 'authenticated':True})
            kwargs['id__lt'] = earlierthan

        q = Q()
        for tag in tags:
            q |= Q(tags__name=tag.name)

        result = get_threads(request.user, NEW_THREADS, orderby, kwargs, [q])
        return JsonResponse({'threads':result['threads'], 
            'end':result['end'], 'authenticated':True, 
            'lastid':result['lastid'],
            'lastvote':result['lastvote']
        }) 

    else:
        return JsonResponse({'threads':[], 'authenticated':False})

def iget_threads_json(request):
    return get_recent_threads(request)
    if request.user.is_authenticated():
        # auth is to check if user has logged in or not and thereby can comment or not
        auth = True
    else: auth = False

    # first check if only one thread is asked
    threadid = request.GET.get('id', '')
    try: 
        if not threadid=='':
            threadid = int(threadid)
            thread = get_object_or_404(Thread, pk=threadid)
            return JsonResponse({'thread':thread_to_dict(thread), 'authenticated':auth})
    except:
        pass

    # list of threads asked 
    threadtype = request.GET.get('type', '')
    try:
        beforeid = int(request.GET.get('earlierthan',''))
    except:
        beforeid = -1
    try:
        votelt = int(request.GET.get('votelt', ''))
    except:
        votelt = -1
    temp = get_threads(request.user, 3, threadtype=threadtype, earlierthan=beforeid, votelt=votelt)
    return JsonResponse({'threads':temp[1], 'end':temp[0], 'authenticated':auth})

def delete_thread(request, threadid):
    if request.user.is_authenticated():
        try:
            threadid = int(threadid)
            thread = get_object_or_404(Thread, pk=threadid)
            if thread.account.user == request.user:
                thread.delete()
                return JsonResponse({"success":True,"message":"Thread Deleted"}, status=200)
            else:
                return JsonResponse({"success":False, "message":"Unauthorized Access"}, status=403)
        except ValueError:
            return JsonResponse({"success":False,"message":"Bad Request"}, status=400)
        except Http404:
            return JsonResponse({"success":False, "message":"Thread not Found"}, status=404)

#########################################
#####       HELPER FUNCTIONS        #####
#########################################

def get_threads(user, n, orderby, filterby, args=()): # args is for Q objects and the like
    end = False
    try:
        lastid = None
        lastvote = None
        threads = list(Thread.objects.order_by(*orderby).filter(*args, **filterby))
        if len(threads)<= n:
            end = True
        else:
            threads = threads[:n]
            lastid = threads[-1].id
            lastvote = threads[-1].votes

    except: # most probably n being greater
        threads = list(Thread.objects.order_by(*orderby).filter(*args, **filterby))
        end = True

    data = {'end':end,
        'threads':[thread_to_dict(user, x) for x in threads],
    }
    data['lastid'] = lastid
    data['lastvote'] = lastvote

    return data


def thread_to_dict(user, thread, less=True):
    #thread_list = []
    if len(thread.content)< 140 or less==False:
        content = thread.content
    else:
        content = thread.content[:140] + ' <a href="/complain/thread/'+str(thread.pk)+'"> More . . .</a>'
    
    downvotes = []
    upvotes = ThreadUpvote.objects.filter(account__user=user, 
                        thread=thread)
    if len(upvotes) == 0:
        downvotes = ThreadDownvote.objects.filter(account__user=user,
                        thread=thread)
    return {'id':thread.id,
            'votes':thread.votes,
            'time':thread.time.strftime("%I:%M %p, %d %b %Y"),
            'title':thread.title,
            'content':content,
            'tags':list(map(lambda x: {
                            'name':x.name,
                            'id':x.id }
                            , thread.tags.all()
                            )),
            'user':{'name':thread.account.user.username,
                    'id':thread.account.pk,
                    'image':thread.account.profile_pic.name, # need to code this
                    },
            'num_comments':Comment.objects.all().filter(thread=thread).count(),
            'can_edit':True if thread.account.user == user else False,
            'supported':True if len(upvotes)>0 else False,
            'thumbed_down':True if len(downvotes)>0 else False,
            'images':list(map(lambda x: x.name,
                                ThreadImage.objects.filter(thread=thread))),
            }
    

