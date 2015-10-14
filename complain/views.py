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


def vote(request):
    if request.method=='POST':
        if request.user.is_authenticated():
            user = request.user
            vote_type = request.POST.get('type', '')
            try:
                thread_id = request.POST['thread_id']
                thread_id = int(thread_id)

                thrd = Thread.objects.get(id=thread_id)
                accnt = Account.objects.get(user=user)

                upvote = Upvote.objects.filter(account=accnt, thread=thrd)
                downvote = Downvote.objects.filter(account=accnt, thread=thrd)

                if vote_type == 'upvote':
                    if len(upvote)==1: # means already upvoted
                        thrd.votes-=1
                        thrd.save()
                        upvote[0].delete()
                        return HttpResponse(-1)
                    elif len(upvote)==0:
                        # user has not upvoted the thread
                        inc = 1
                        if len(downvote)>0: # user has downvoted, so increase by 2
                            inc = 2
                            downvote[0].delete()
                        thrd.votes+=inc
                        thrd.save()
                        upvote = Upvote(account=accnt, thread=thrd)
                        upvote.save()
                        return HttpResponse(inc)
                    else:
                        raise 404('Error')

                elif vote_type == 'downvote':
                    if len(downvote)==1: # means already downvoted
                        thrd.votes+=1
                        thrd.save()
                        downvote[0].delete()
                        return HttpResponse(1)
                    elif len(downvote)==0:
                        # user has not upvoted the thread
                        inc = -1
                        if len(upvote)>0: # user has downvoted, so increase by 2
                            inc = -2
                            upvote[0].delete()
                        thrd.votes+=inc
                        thrd.save()
                        downvote = Downvote(account=accnt, thread=thrd)
                        downvote.save()
                        return HttpResponse(inc)
                    else:
                        raise 404('Error')

            except Exception as e:
                return HttpResponse(e.args)
        else:
            return HttpResponse('user not authenticated')

class ThreadPage(View):
    context = {}

    def get(self, request, thread_id):
        if request.user.is_authenticated():
            self.context['user'] = request.user

        thread = Thread.objects.get(id=thread_id)
        self.context['thread'] = thread

        comments = Comment.objects.filter(thread=thread)
        self.context['comments']= comments

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



