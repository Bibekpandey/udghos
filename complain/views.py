from django.shortcuts import render, redirect, Http404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import Q

from django.views.generic import View
from complain.models import *

COMPLAINT, DISCUSSION = 0, 1

class Index(View):
    def get(self, request):
        self.context = {}
        if request.user.is_authenticated():
            self.context['user'] = request.user

        self.context['threads'], self.context['num_comments'] = get_recent_threads(20)
        return render(request, "complain/index.html", self.context)


class Login(View):
    def get(self, request):
        self.context = {}
        return render(request, "complain/login.html", self.context)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if username=='' or password=='':
            return HttpResponse('username/password can\'t be empty')
        user = authenticate(username=username, password=password)

        if user is None:
            return HttpResponse('username/password error')
        else:
            login(request, user)
            return redirect('index') 


def logout_user(request):
    logout(request)
    return redirect('index')


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
    
    def post(self, request, thread_type):
        if not request.user.is_authenticated():
            return redirect('login')

        thread_type= request.POST.get('thread_type', '')

        if thread_type=='' or thread_type not in ['complaint', 'discussion']:
            raise Http404('invalid thread type')

        if thread_type=='complaint': th_type = COMPLAINT
        elif thread_type=='discussion': th_type = DISCUSSION
        else: raise Http404('invalid thread type')

        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        tags = request.POST.get('tags', '')
        
        if title=='' or content =='':
            self.context['message'] = 'Title/content can\'t be empty'
            return self.get(request, thread_type)

        # now with storage of the thread
        account = Account.objects.get(user=request.user)
        thread = Thread(thread_type=th_type, title=title, 
                    content=content, account=account)
        thread.save()
        return HttpResponse('Thread posted.<br>Go to <a href="/complain/">Home</a> page')


def calculate_delta_vote(action, upvotes, downvotes): 
    return (1+action)/2 * (-2*upvotes + downvotes + 1) \
                + (1-action)/2 *(2*downvotes - upvotes - 1)


def vote_thread(thread_id, account, action): # action is 1 for upvote and -1 for downvote
    thread = Thread.objects.get(id=thread_id)
    upvotes = ThreadUpvote.objects.filter(account=account, thread=thread)
    n_ups = len(upvotes)
    downvotes = ThreadDownvote.objects.filter(account=account, thread=thread)
    n_downs = len(downvotes)

    if n_ups==1:
        upvotes[0].delete()
    elif n_ups==0:
        upvote = ThreadUpvote.create(account=account, thread=thread)
        upvote.save()
    else: raise Exception('error in vote evaluation')

    delta_vote = calculate_delta_vote(action, n_ups, n_downs)
    thread.votes+=delta_vote
    thread.save()
    print(delta_vote)
    return delta_vote

def vote_comment(thread_id, account, comment_id, action):
    thread = Thread.objects.get(id=thread_id)
    comment = Comment.objects.get(id=comment_id)
    upvotes = CommentUpvote.objects.filter(account=account, thread=thread)
    n_ups = len(upvotes)
    downvotes = CommentDownvote.objects.filter(account=account, thread=thread)
    n_downs = len(downvotes)

    if n_ups==1:
        upvotes[0].delete()
    elif n_ups==0:
        upvote = CommentUpvote.create(account=account, comment=comment)
        upvote.save()
    else: raise Exception('error in vote evaluation')

    delta_vote = calculate_delta_vote(action, n_ups, n_downs)
    comment.votes+=delta_vote
    comment.save()
    return delta_vote


def vote(request):
    val = {'upvote':1, 'downvote':0}
    if request.method=='POST':
        try:
            item = request.POST['vote_item']
            thread_id = int(request.POST['thread_id'])
            vote_type = request.POST.get('type', '')

            if request.user.is_authenticated():

                user = request.user
                account = Account.objects.get(user=user)

                # get the commment object if vote is for comment
                #comment_id = request.POST['comment_id'] # -1 if not a comment vote
                cmmt = None
                return HttpResponse('testing')
                if item=='comment':
                    return HttpResponse('comment')
                    return HttpResponse(vote_comment(thread_id, account, comment_id, val[vote_type]))
                else:
                    return HttpResponse('thread')
                    return HttpResponse(vote_thread(thread_id, account, val[vote_type]))
        except Exception as e:
            return HttpResponse(e.args)
          

class ThreadPage(View):
    context = {}

    def get(self, request, thread_id):
        if request.user.is_authenticated():
            self.context['user'] = request.user

        thread = Thread.objects.get(id=thread_id)
        self.context['thread'] = thread

        comments = Comment.objects.filter(thread=thread)
        self.context['comments']= comments

        replies = []
        for comment in comments:
            replys = Reply.objects.filter(comment=comment)
            replies.append(list(replys))

        self.context['replies'] = replies

        self.context['total_comments'] = len(comments)

        return render(request, "complain/thread.html", self.context)


def comment(request):
    if request.method=='POST':
        try:
            content = request.POST['comment']
            if request.user.is_authenticated() and content.strip()!='':
                thread_id = int(request.POST['thread_id'])
                account = Account.objects.get(user=request.user)
                thread = Thread.objects.get(id=thread_id)

                comment = Comment(account=account, 
                            thread=thread, text=content)
                comment.save()
                return redirect(reverse('thread', args=[str(thread_id)]))
        except TypeError:
            return HttpResponse('Invalid thread id')
        except Exception as e:
            return HttpResponse(e.args)
    return redirect('index')


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


#########################################
#####       HELPER FUNCTIONS        #####
#########################################

def get_recent_threads(n): # return n threads with number of comments
    try:
        threads = Thread.objects.order_by('-time')[:n]
    except: # n greater than total length
        threads = Thread.objects.order_by('-time')

    num_comments = []    
    for thread in threads:
        num_cmts = Comment.objects.all().filter(thread=thread).count()
        num_comments.append(num_cmts)

    return (threads, num_comments)



