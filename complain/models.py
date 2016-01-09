from django.db import models
from django.contrib.auth.models import User

from django.template.defaultfilters import slugify
from datetime import datetime


(COMPLAINT, DISCUSSTION) = (0, 1)

class Account(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name="Account")
    verification_key = models.CharField(max_length=10)
    verified = models.BooleanField(default=False)
    address = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True, max_length=30)
    points = models.IntegerField(default=10)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=50)  

    def __str__(self):
        return self.name


class Thread(models.Model):
    thread_type = models.IntegerField(default=0) # 0 for complaint, 1 for discussion thread
    title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    account = models.ForeignKey(Account)
    time = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)
    #downvotes = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + ' [' + self.account.user.username+']'


class Comment(models.Model):
    account = models.ForeignKey(Account)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread)
    votes = models.IntegerField(default=0)
    #downvotes = models.IntegerField(default=0)
    
    def __str__(self):
        return  self.text[:5] + '... [' + self.account.user.username+']'


class Reply(models.Model):
    account = models.ForeignKey(Account)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment)

    def __str__(self):
        return  self.text[:5] + '... [' + self.account.user.username+']'


class ThreadUpvote(models.Model):
    account = models.ForeignKey(Account)
    thread = models.ForeignKey(Thread)

class ThreadDownvote(models.Model):
    account = models.ForeignKey(Account)
    thread = models.ForeignKey(Thread)

class CommentUpvote(models.Model):
    account = models.ForeignKey(Account)
    comment = models.ForeignKey(Comment)

class CommentDownvote(models.Model):
    account = models.ForeignKey(Account)
    comment = models.ForeignKey(Comment)

def getFileName(instance, filename):
    ext = filename.split('.')[-1]
    name = str(instance.thread.id) + '_' + str(instance.pk) + '.'+ ext
    return  'images/' + name

class ThreadImage(models.Model):
    name = models.CharField(max_length=100)
    thread = models.ForeignKey(Thread)
    image = models.ImageField(upload_to=getFileName)

    def save(self, *args, **kwargs):
        super(ThreadImage, self).save(*args, **kwargs)
        self.name = self.image.name
        super(ThreadImage, self).save(*args, **kwargs)
