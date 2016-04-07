from django.http import JsonResponse
from complain.models import *
NEW_THREADS = 3 # new number of threads when scrolled in browser

def get_recent_threads(request):
    # auth is to check user login which lets like/comment
    print('get recent threads')
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
        print('invalid')
        return JsonResponse({'status':False, 
                        'message':'Invalid request parameter'},
                        status=404)
    except KeyError:# earlierthan is not specified
        print('earlierthan not specified');
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
    earlier = request.GET.get('earlierthan','') 
    try:
        earlier = int(earlier)
        orderby = ['-time']
        filterby = {}
        threads = get_threads(request.user, NEW_THREADS, orderby, filterby)
    except: # invalid get parameter
        return JsonResponse({'status':False, 
                        'message':'Invalid request parameter'},
                        status=404)

    pass
def get_favourite_threads(request):
    pass

def get_threads_json(request):
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

#########################################
#####       HELPER FUNCTIONS        #####
#########################################

def get_threads(user, n, orderby, filterby): 
    end = False
    try:
        lastid = None
        lastvote = None
        threads = list(Thread.objects.order_by(*orderby).filter(**filterby))
        if len(threads)<= n:
            end = True
        else:
            threads = threads[:n]
            lastid = threads[-1].id
            lastvote = threads[-1].votes

    except: # most probably n being greater
        threads = list(Thread.objects.order_by(*orderby).filter(**filterby))
        end = True

    data = {'end':end,
        'threads':[thread_to_dict(user, x) for x in threads],
    }
    data['lastid'] = lastid
    data['lastvote'] = lastvote

    return data


def get_threads1(n, threadtype='recent', earlierthan=-1, votelt=-1): # return n threads with number of comments
    end = False
    if threadtype == 'top':
        order=['-votes', '-id']
        kwargs = {
            'votes__lt':votelt,
            'id__lt':earlierthan,
        }
        if votelt==-1:
            del kwargs['votes__lt']
        if earlierthan==-1:
            del kwargs['id__lt']
    else:
        order=['-time']
        kwargs = {
            'id__lt':earlierthan
        }
        if earlierthan==-1:
            del kwargs['id__lt']

    try:
        threads = list(Thread.objects.order_by(*order).filter(**kwargs)[:n])
        print('in try')
    except: # most probably n being greater
        threads = list(Thread.objects.order_by(*order).filter(**kwargs))
        end = True
    return {'end':end,
        'threads':list(map(thread_to_dict, threads)),
        'lastid':threads[:-1].id,
        'lastvote':threads[:-1].votes
    }

    
    return (end, list(map(thread_to_dict, threads)))

def thread_to_dict(user, thread):
    #thread_list = []
    return {'id':thread.id,
            'votes':thread.votes,
            'time':thread.time.strftime("%I:%M %p, %d %b %Y"),
            'title':thread.title,
            'content':thread.content,
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
            'images':list(map(lambda x: x.name,
                                ThreadImage.objects.filter(thread=thread))),
            }

