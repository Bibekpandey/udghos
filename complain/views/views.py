from django.shortcuts import render, redirect, Http404, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.core.exceptions import ObjectDoesNotExist

from django.views.generic import View
from complain.models import *
import json
import random
import os

dict_activity_type = {1:'COMMENT', 2:'SUPPORT', 4:'DOWNVOTE', 3:'MESSAGE'}
# view modules
from .ThreadViews import *

import math, traceback

COMPLAINT, DISCUSSION = 0, 1

#error message 
def error(request): return HttpResponse('Login error') 

class Index(View): 
    def get(self, request):
        self.context = {}
        if request.user.is_authenticated():
            self.context['authenticated'] = True
            self.context['user'] = request.user
            acc = Account.objects.get(user=request.user)
            tags = list(acc.tags_followed.all())
            self.context['tags'] = tags
            self.context['address'] = acc.address
            self.context['about'] = acc.about
            self.context['profile_pic'] = acc.profile_pic
            self.context['notifications'] = get_notifications(request)
        else:
            self.context['authenticated'] = False

        return render(request, "complain/home.html", self.context)


def get_comments(request):
    try:
        threadid = int(request.POST.get('threadid'))
        
        ret = {"comments":get_comments_by_thread_id(threadid)}
        return JsonResponse(ret)
    except Exception as e:
        print(repr(e))

def get_comments_by_thread_id(threadid):
    comments = Comment.objects.filter(thread__id=threadid)
    templist = []
    templist = map(lambda x:{'user':x.account.user.username,
                                'comment':x.text,
                                'date':x.time.strftime("%I:%M %p, %d %b %Y")
                                }, comments)
    return list(templist)
        

def delete_comment(request):
    if request.user.is_authenticated():
        try:
            comment_id = int(request.POST.get('commentid'))
            comment = comment.objects.get(id=comment_id)
            thrd = comment.thread
            comment.delete()
            ret = {"comments": get_comments_by_thread_id(thrd.id)}
            return JsonResponse(ret)
        except Exception as e:
            print(repr(e))
    else:
        return HttpResponse('')


# CREATE ACCOUNT, takes in user object
def createAccount(userobj):
    # check if Account already exists
    try:
        accnt = Account.objects.get(user=userobj)
        return
    except ObjectDoesNotExist:
        return 
    account = Account(user=userobj, address="home", email="abc@def.ghi", verified=True)
    account.save()
    

class Login(View):
    def get(self, request):
        if request.user.is_authenticated():
            return redirect('index')
        self.context = {}
        return render(request, "complain/signin.html", self.context)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if username=='' or password=='':
            return JsonResponse({'success':False, 'message':'Empty username/password'})
        user = authenticate(username=username, password=password)

        if user is None or username=="udghos":
            return JsonResponse({'success':False, 'message':'Wrong username/password'})
        else:
            acc = Account.objects.get(user=user)
            if acc.verified:
                login(request, user)
                return JsonResponse({'success':True, 'message':'Login Successful'})
            else:
                return JsonResponse({'success':False, 'message':'NOT VERIFIED'})


def logout_user(request):
    logout(request)
    return redirect('login')

class Signup(View):
    context = {}
    def get(self, request):
        pass

    def post(self, request):
        ret = {}
        usr = None
        acc = None
        try:
            firstName = request.POST['firstname'].strip()
            lastName = request.POST['lastname'].strip()
            email = request.POST['email'].strip()
            password = request.POST['password'].strip()
            username = request.POST['username'].strip()

            user = User.objects.filter(Q(username=username)| Q(email=email))
            if len(user)>0:
                ret['success'] = False
                ret['message'] = "username/email already taken"
                return JsonResponse(ret)

            newUser = User(username=username,
                            first_name=firstName,
                            last_name=lastName,
                            email=email)
            newUser.set_password(password)
            newUser.save()
            usr = newUser
            account = Account(user=newUser)
            account.save()
            acc = account
            user = authenticate(username=username, password=password)
            ret['success'] = True
            ret['message'] = "successfully signed up"
            code = generate_code()
            account.verification_key = code
            account.save()
            mail_send(code, email)
            #login(request, user)
            return JsonResponse(ret)
        except Exception as e:
            u = User.objects.filter(username=username)
            if len(u)==1:
                a = Account.objects.filter(user=u)
                a.delete()
                u.delete()
            ret['success'] = False
            ret['message'] = "Can't sign up right now. Please try social login"
            return JsonResponse(ret)

class Post(View):
    context = {}
    def get(self, request, thread_type):
        if not request.user.is_authenticated():
            return redirect('login')
        if thread_type=='complaint':
            self.context['thread_type'] = 'complaint'
        elif thread_type=='discussion':
            self.context['thread_type'] = 'discussion'
        else:
            raise Http404('URL: '+reverse('post', args=[thread_type])+' not found')
        self.context['form_heading']  = 'Post a '+thread_type
        return render(request, "complain/post-thread.html", self.context)
    
    def post(self, request):
        if not request.user.is_authenticated():
            return redirect('login')

        # check if anonymous
        anonymous = request.POST.get('anonymous', '')

        thread_type= request.POST.get('thread_type', '')
        thread_type='complaint'

        if thread_type=='' or thread_type not in ['complaint', 'discussion']:
            raise Http404('invalid thread type')

        if thread_type=='complaint': th_type = COMPLAINT
        elif thread_type=='discussion': th_type = DISCUSSION
        else: th_type = COMPLAINT

        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        tags = request.POST.get('tags', '')
        ''' MULTIPLE FILES UPLOAD
        for afile in request.FILES.getlist('files'):
        File(file=afile, files=test).save()
        '''
                
        if content =='': # or title==''
            return redirect('index')
            #self.context['message'] = 'Title/content can\'t be empty'
            #return self.get(request, thread_type)

        # now with storage of the thread
        account = Account.objects.get(user=request.user)
        thread = Thread(thread_type=th_type, title=title, 
                    content=content, account=account)
        if anonymous=="yes":
            thread.anonymous = True
        else: thread.anonymous = False

        thread.save()
        # now the tags
        strtagids = request.POST.get('tagids', '')
        #return HttpResponse(strtagids)
        #tagids = list(map(lambda x: int(x),strtagids.split(',')))
        tagids = []
        for x in strtagids.split(','):
            try:
                tagids.append(int(x))
            except ValueError:
                pass
        if tagids==[]:
            thread.tags.add(ThreadTag.objects.get(name__icontains='Not-Specified'))
        for tagid in tagids:
            thread.tags.add(ThreadTag.objects.get(pk=tagid))
        thread.save()

        # now the targets
        strtargetids = request.POST.get('targetids', '')
        targetids = []
        for x in strtargetids.split(','):
            try:
                targetids.append(int(x))
            except ValueError:
                pass
        for tid in targetids:
            thread.targets.add(Target.objects.get(pk=tid))
        if len(targetids)==0:
            t = Target.objects.filter(name__icontains='udghos')
            if not len(t)==0:
                thread.targets.add(t[0])
        thread.save()

        images = request.FILES.getlist('images')
        for image in images:
            img = ThreadImage(name=image.name, thread=thread)
            img.save()
            img.image = image # to get pk of image object
            img.save()

        return redirect('index')


def calculate_delta_vote(action, upvotes, downvotes): 
    return (1+action)/2 * (-2*upvotes + downvotes + 1) \
                + (1-action)/2 *(2*downvotes - upvotes - 1)


def vote_thread(request, thread_id, account, action): # action is 1 for upvote and -1 for downvote
    thread = Thread.objects.get(id=thread_id)
    upvotes = ThreadUpvote.objects.filter(account=account, thread=thread)
    n_ups = len(upvotes)
    downvotes = ThreadDownvote.objects.filter(account=account, thread=thread)
    n_downs = len(downvotes)

    useraction = ""

    event = None
    if n_ups==1 and action==1:
        useraction='undo'
        upvotes[0].delete()
    elif n_ups==0 and action==1:
        useraction="support" # support = upvote
        event=SUPPORTED
        upvote = ThreadUpvote.objects.create(account=account, thread=thread)
        upvote.save()
        # delete existing downvote
        if n_downs==1:downvotes[0].delete()
    elif n_downs==1 and action==-1:
        useraction='undo'
        downvotes[0].delete()
    elif n_downs==0 and action==-1:
        event=DOWNVOTED
        useraction="thumb down"
        downvote = ThreadDownvote.objects.create(account=account, thread=thread)
        downvote.save()
        # delete existing upvote
        if n_ups==1: 
            upvotes[0].delete()
    elif n_ups==0 and n_downs==0:pass
    else: raise Exception('error in vote evaluation')

    delta_vote = int(calculate_delta_vote(action, n_ups, n_downs))
    thread.votes+=delta_vote
    thread.save()
    acc = Account.objects.get(user=request.user)
    if acc != thread.account and event!=None:
        notif = Notification.objects.create(fromuser=acc,
                touser=thread.account, thread=thread, event=event)
        notif.save()
    return {"action":useraction, "increment":delta_vote}

def vote_comment(comment_id, account, action):
    comment = Comment.objects.get(id=comment_id)
    upvotes = CommentUpvote.objects.filter(account=account, comment=comment)
    n_ups = len(upvotes)
    downvotes = CommentDownvote.objects.filter(account=account, comment=comment)
    n_downs = len(downvotes)

    if n_ups==1 and action==1:
        upvotes[0].delete()
    elif n_ups==0 and action==1:
        upvote = CommentUpvote.objects.create(account=account, comment=comment)
        upvote.save()
        # delete existing downvote
        if n_downs==1:downvotes[0].delete()
    elif n_downs==1 and action==-1:
        downvotes[0].delete()
    elif n_downs==0 and action==-1:
        downvote = CommentDownvote.objects.create(account=account, comment=comment)
        downvote.save()
        # delete existing upvote
        if n_ups==1: upvotes[0].delete()
    elif n_downs==0 and n_ups==0:pass
    else: raise Exception('error in vote evaluation')

    delta_vote = int(calculate_delta_vote(action, n_ups, n_downs))
    comment.votes+=delta_vote
    comment.save()
    return delta_vote

def update_user_points(owner, voter, item, delta):
    if item=='thread':
        factor = 10 # hight weightage for threads
    else: # comment
        factor =  7 # less weightage for comments
    voter_points = voter.points
    item_votes = item.votes
    d_points = factor * math.e**(voter_points/100 - item_votes/10) * delta
    owner.points += d_points
    owner.save()
    return d_points


def vote(request):
    val = {'upvote':1, 'downvote':-1}
    if request.method=='POST':
        try:
            item = request.POST['vote_item']
            object_id = int(request.POST['object_id'])
            vote_type = request.POST.get('type', '')

            if request.user.is_authenticated():

                user = request.user
                account = Account.objects.get(user=user)

                # get the commment object if vote is for comment
                #comment_id = request.POST['comment_id'] # -1 if not a comment vote
                owner = None # owner is the user whose point/rating is to be updated 
                itm = object
                voter = account
                delta = None
                if item=='comment':
                    itm = Comment.objects.get(id=object_id)
                    owner = itm.account
                    delta = vote_comment(object_id, account, val[vote_type])
                    return HttpResponse(delta)
                else:
                    itm = Thread.objects.get(id=object_id)
                    owner = itm.account
                    vote_dict = vote_thread(request, object_id, account, val[vote_type])
                    return JsonResponse(vote_dict)
                update_user_points(owner, voter, item, delta)
        except Exception as e:
            return HttpResponse(traceback.format_exc())
          

class ThreadPage(View):
    context = {}

    def get(self, request, thread_id=None):
        if request.user.is_authenticated():
            self.context['user'] = request.user
            self.context['authenticated'] = True
            self.context['notifications'] = get_notifications(request)
            self.context['profile_pic'] = Account.objects.get(user=request.user).profile_pic
        else:
            self.context['authenticated'] = False

        threads = Thread.objects.filter(id=thread_id)
        if len(threads)>0:
            self.context['id'] = threads[0].id
            self.context['title'] = threads[0].title
            self.context['description'] = threads[0].content[:140] + '...'
            from .ThreadViews import REQUIRED_VOTES  as req
            self.context['votes'] = threads[0].votes
            self.context['required'] = req
            img = ThreadImage.objects.filter(thread=threads[0])
            if len(img)>0:
                self.context['image'] = img[0].name 
            else:
                self.context['image'] = None
        return render(request, "complain/post.html", self.context)


def comment(request):
    if request.method=='POST':
        try:
            content = request.POST['comment']
            if request.user.is_authenticated() and content.strip()!='':
                thread_id = int(request.POST['thread_id'])
                account = Account.objects.get(user=request.user)
                thread = Thread.objects.get(id=thread_id)
                # get comments, so that the commenting users could be notified
                comments = Comment.objects.filter(thread=thread)
                notified_users = []
                for comment in comments:
                    if comment.account not in notified_users:
                        if account != comment.account:
                            notif = Notification.objects.create(fromuser=account, touser=comment.account,event=COMMENTED,thread=thread)
                            notif.save()


                comment = Comment(account=account, 
                            thread=thread, text=content)
                comment.save()
                ret = {}
                ret['comment'] = {"comment":comment.text,
                                'date':comment.time.strftime("%I:%M %p, %d %b %Y"),
                                "user":comment.account.user.username
                }
                return JsonResponse(ret)
                #return redirect(reverse('thread', args=[str(thread_id)]))
        except TypeError:
            return HttpResponse('Invalid thread id')
        except Exception as e:
            return HttpResponse(e.args)
    return HttpResponse('nope')
    #return redirect('index')


def reply(request):
    if request.method=='POST':
        try:
            content = request.POST['reply']
            if request.user.is_authenticated() and content.strip()!='':
                thread_id = int(request.POST['thread_id'])
                comment_id = int(request.POST['comment_id'])
                account = Account.objects.get(user=request.user)
                comment = Comment.objects.get(id=comment_id)

                reply = Reply(account=account, 
                            comment=comment, text=content)
                reply.save()
                return redirect(reverse('thread', args=[str(thread_id)]))
        except TypeError:
            return HttpResponse('Invalid thread id')
        except Exception as e:
            return HttpResponse(e.args)
    return redirect('index')

def new_social(request):
    if request.method=="GET":
        return render(request, "complain/new-social.html", {})
    else:
        uid = request.POST.get("userid", "")
        uname = request.POST.get("username", "")
        if uid == "":
            raise Http404("user not found")
        if uname == "":
            return render(request, "complain/new-social.html", 
                {"message":"username can't be empty"}
            )
        else:
            try:
                user = User.objects.get(id=int(uid))
                usrs = User.objects.filter(username=uname)
                if len(usrs) > 1:
                    return render(request, "complain/new-social.html", 
                    {"message":"username not available"}
                    )
                user.username = uname
                user.save()
                # Create Account
                acc = Account(user=user, verified=True, address="")
                acc.save()
                return HttpResponseRedirect("/")
            except:
                raise Http404("user not found")


# for tags
def get_tags(request):
    if request.method=='GET':
        query = request.GET.get('query','')
        if query!='':
            tags = ThreadTag.objects.filter(name__contains=query)
            d = [] 
            for x in tags:
                d.append({'id':x.id,'name':x.name})
            return JsonResponse({'items':d})
        else:
            return JsonResponse({'items':[]})

def get_targets(request):
    if request.method=='GET':
        query = request.GET.get('query', '').strip()
        if query !='':
            words = query.split(' ')
            d = []
            temp = []
            for word in words:
                items = Target.objects.filter(name__contains=word)
                for x in items:
                    if x not in temp:
                        temp.append(x)
            for x in temp:
                d.append({'id':x.id, 'name':x.name})    
            return JsonResponse({'items':d})
        else:
            return JsonResponse({'items':[]})
                

class Profile(View):
    def get(self,request, profileid):
        self.context = {}
        if request.user.is_authenticated():
            try:
                profileid = int(profileid)
            except Exception:
                raise Http404('user not found')
            self.context['authenticated'] = True
            self.context['user'] = request.user
            acc = Account.objects.get(user_id=profileid)
            useracc = Account.objects.get(user=request.user)
            tags = useracc.tags_followed.all()
            self.context['address'] = acc.address
            self.context['profile_pic'] = useracc.profile_pic
            self.context['user_pic'] = acc.profile_pic
            self.context['notifications'] = get_notifications(request)
            self.context['account'] = acc
            self.context['about'] = acc.about
            self.context['edit'] = False
            self.context['tags'] = tags
            if request.user.id==profileid:
                self.context['edit'] = True
        else:
            self.context['authenticated'] = False
        return render(request, "complain/profile.html",self.context)

def image_update(request):
    if request.user.is_authenticated():
            uid = int(request.POST['userid'])
            account = Account.objects.get(pk=uid)
            image = request.FILES.get('image')
            if image is None:
                return redirect('profile', uid)
            if image is not None:
                try:
                    curr_img = account.profile_pic.path
                    os.system('rm '+curr_img)
                except:
                    pass
                finally:
                    account.profile_pic = image
                    account.save()
                    return redirect('profile', uid)

def profile_update(request):
    try:
        ret = {}
        username = request.POST['username']
        firstname = request.POST['first-name']
        lastname = request.POST['last-name']
        address = request.POST['address']
        about = request.POST['about']
        uid = request.POST['userid']
        try:
            image = request.FILES['image']
        except:
            pass
        try:
            uid = int(uid)
        except:
            ret['success'] = False
            ret['error'] = "Can't update profile. Try later."
            return JsonResponse(ret)

        # get account
        acc = Account.objects.get(pk=uid)
        usr = acc.user
        # check username exists or not
        usrs = User.objects.filter(username=username)

        if len(usrs)!=0 and usrs[0].pk != usr.pk:
            ret['success'] = False
            ret['error'] = "Username exists. Try next one"
            return JsonResponse(ret)

        usr.first_name = firstname
        usr.last_name = lastname
        usr.username=username
        acc.address = address
        acc.about = about;
        usr.save()
        acc.save()

        new_tags = request.POST.get('new_tags','')
        removed_tags = request.POST.get('removed_tags','')

        try:
            if new_tags!='':
                tags_new = list(map(lambda x: int(x), new_tags.split(',')))
                for x in tags_new:
                    tag = ThreadTag.objects.get(id=x)
                    acc.tags_followed.add(tag)
                acc.save()

            if removed_tags!='':
                tags_removed = list(map(lambda x:int(x),removed_tags.split(',')))
                for x in tags_removed:
                    tag = ThreadTag.objects.get(id=x)
                    acc.tags_followed.remove(tag)
                acc.save()
        except Exception as e:
            print(repr(e))  

        ret['success'] = True
        ret['error'] = "Changed profile"
        return(JsonResponse(ret))

    except ObjectDoesNotExist:
        ret['success'] = False
        ret['error'] = "No user found. Please refresh and try later"
        return JsonResponse(ret)
    except KeyError:
        ret['success'] = False
        ret['error'] = "Can't update profile. Try later."
        return JsonResponse(ret)
    except Exception as e:
        ret['success'] = False
        ret['error'] = repr(e)
        return(JsonResponse(ret))

def staff_page(request):
    if request.method=="GET" and request.user.is_staff:
        threads = Thread.objects.filter(status=0)
        return render(request, "complain/staff-page.html", {'threads':threads})
    else :
        raise Http404

def okay(request):
    if request.user.is_staff and request.method=="POST":
        try:
            pk = request.POST['id']
            thrd = Thread.objects.get(id=int(pk))
            thrd.status = VERIFIED
            thrd.save()
            return JsonResponse({'success':True})
        except Exception as e:
            return JsonResponse({'success':False, 'error':'something wrong' + repr(e)})
    else:
        return JsonResponse({'success':False,'error':'Invalid request or user'})

def edit(request):
    if request.user.is_staff and request.method=="POST":
        try:
            pk = request.POST['id']
            title = request.POST['title']
            content = request.POST['content']
            thrd = Thread.objects.get(id=int(pk))
            thrd.title = title
            thrd.content = content
            thrd.status=VERIFIED
            thrd.save()
            return JsonResponse({'success':True})
        except Exception as e:
            return JsonResponse({'success':False, 'error':repr(e)})
    else:
        return JsonResponse({'success':False, 'error':'something wrong'})

def delete(request):
    if request.user.is_staff:
        try:
            pk = int(request.GET['id'])
            thread = Thread.objects.filter(id=int(request.GET['id']))
            thread[0].delete()
        except Exception as e:
            pass
        finally:
            return redirect('staffpage')

class Concern(View):
    def get(self,request):
        self.context = {}
        if request.user.is_authenticated():
            acc = Account.objects.get(user=request.user)
            tags = list(acc.tags_followed.all())
            self.context['tags'] = tags
            self.context['address'] = acc.address
            self.context['profile_pic'] = acc.profile_pic
            self.context['notifications'] = get_notifications(request)

            self.context['authenticated'] = True
        else:
            self.context['authenticated'] = False
        return render(request, "complain/post-concern.html",self.context)

class Mynotifications(View):
    def get(self,request):
        self.context = {}
        if request.user.is_authenticated():
            acc = Account.objects.get(user=request.user)
            tags = list(acc.tags_followed.all())
            self.context['tags'] = tags
            self.context['address'] = acc.address
            self.context['profile_pic'] = acc.profile_pic
            self.context['notifications'] = get_notifications(request)

            self.context['authenticated'] = True
        else:
            self.context['authenticated'] = False
        return render(request, "complain/mynotifications.html",self.context)


class Settings(View):
    def get(self,request):
        self.context = {}
        if request.user.is_authenticated():
            acc = Account.objects.get(user=request.user)
            tags = list(acc.tags_followed.all())
            self.context['tags'] = tags
            self.context['address'] = acc.address
            self.context['profile_pic'] = acc.profile_pic
            self.context['notifications'] = get_notifications(request)
            self.context['password_set'] = True if request.user.has_usable_password() else False

            self.context['authenticated'] = True
            return render(request, "complain/settings.html",self.context)
        else:
            return redirect('index')        

def mark_read_notifications(request):
    if request.user.is_authenticated():
        notifs = Notification.objects.filter(read=False)
        for x in notifs:
            x.read=True
            x.save()
        return JsonResponse({'success':True})
    else:
        return JsonResponse({'success':False})

def get_notifications(request):
    if request.user.is_authenticated():
        acc = Account.objects.get(user=request.user)
        notifs = Notification.objects.filter(read=False, touser=acc)
        dicts = list(map(get_notification_dict, list(notifs)))
        return dicts
        #return JsonResponse({'notifications':dicts, 'success':True})
    else:
        return []
        #return JsonResponse({'notifications':[], 'success':False})

def get_notification_dict(notification):
    ret={}
    if notification.thread is not None:
        ret['thread'] = notification.thread.id
    else:ret['thread'] = None
    ret['by'] = notification.fromuser.user.username
    ret['by_image'] = notification.fromuser.profile_pic
    ret['message'] = -1
    if notification.event==COMMENTED:
        ret['type']='comment'
    elif notification.event==SUPPORTED:
        ret['type']='support'
    elif notification.event==DOWNVOTED:
        ret['type']='downvote'
    else:
        ret['type']='message'
    return ret


####################
# GET ACTIVITIES
####################
def get_activities(request):
    if request.user.is_authenticated():
        page = request.GET.get('page','')

        activities_list = Activity.objects.filter(account__user=request.user).order_by('-date')
        paginator = Paginator(activities_list, 5)

        try:
            activities = paginator.page(page)
        except PageNotAnInteger:
            activities = paginator.page(1)
        except EmptyPage:
            activities = paginator.page(paginator.num_pages)

        ret = {}
        ret['end'] = False if activities.has_next() else True
        if activities.has_next():
            ret['next'] = activities.next_page_number()
        else: ret['next'] = None
        ret['activities'] = dict_activities(activities.object_list)
        return JsonResponse(ret)
    return JsonResponse({'activities':[], 'end':True})



def dict_activities(activities):
    l = []
    for each in activities:
        activity = {}
        activity['action'] = dict_activity_type[each.activity_type]
        activity['time'] = time_since_event(each.date)
        activity['thread'] = {'id':each.thread.id, 
                            'title':each.thread.title}
        l.append(activity)
    return l



def change_password(request):
    if request.method=='POST' or 1:
        if request.user.is_authenticated():
            old_password = request.POST.get('old-password', '')
            if request.user.has_usable_password():
                if not request.user.check_password(old_password):
                    return JsonResponse({'success':False,'message':'Old password does not match'})
            new_password = request.POST.get('new-password', '')
            if len(new_password) < 8:
                return JsonResponse({'success':False, 'message':'Password needs to be at least 8 characters long'})
            request.user.set_password(new_password)
            request.user.save()
            return JsonResponse({'success':True, 'message':'Successfully changed password'})
    else:
        return JsonResponse({'success':False, 'message':'GET method not expected'})

def verify_page(request):
    return render(request, "complain/verify.html")

def verify(request, code):
    if request.user.is_authenticated():
        return redirect('index')
    else:
        accs = Account.objects.filter(verification_key=code)
        if len(accs)==0:
            return HttpResponse('Invalid code. Go to <a href="/">Home</a>')
        acc = accs[0]
        if acc.verified:
            acc.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, acc.user)
            return HttpResponse('Already Verified. Go to <a href="/">Home</a>')
        acc.verified = True
        acc.save()
        acc.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, acc.user)
        return HttpResponse('Congratulations!! You are Verified. Go to <a href="/">Home</a>')

def mail_send(code, email):
    subject, from_email, to = 'account verification', 'noreply@udghos.com', email
    text = "Welcome to udghos.com. This is the email that lets you verify your account in udghos.com. The following is the link to verify:"
    html = 'Please verify your account by clicking this link: <a href="http://udghos.com/verify/'+str(code)+'">udghos.com/verify/'+str(code)+'</a>'
    msg = EmailMultiAlternatives(subject, "", from_email, [to])
    msg.attach_alternative(html, "text/html")
    msg.send()

keys = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def generate_code(n=10):
    s = ''
    l = len(keys)
    for x in range(n):
        s+= keys[random.randrange(0,l)]
    return s


def post_review(request):
    if request.method=="POST":
        if request.user.is_authenticated():
            acc = Account.objects.get(user=request.user)
        else:acc = None

        title = request.POST.get('review-title','').strip()
        content = request.POST.get('review-content', '').strip()
        if content!='':
            review = Review(title=title, content=content, account=acc)
            review.save()
        return render(request, "complain/common.html", {"message":"Thank you so much for your reveiw!!"})

def stay_tuned(request):
    return render(request, 'complain/common.html', {"message":"We are Almost Done. STAY TUNED!!"}) 

def how_it_works(request):
    return render(request, 'complain/how-it-works.html',{})  

def about(request):
    return render(request, 'complain/about.html',{})  


