from django.db import models
from django.contrib.auth.models import User

from django.template.defaultfilters import slugify
from datetime import datetime


class Account(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name="Account")
    verification_key = models.CharField(max_length=10)
    verified = models.BooleanField(default=False)
    address = models.CharField(max_length=50)
    email = models.EmailField(max_length=30)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=50)  

    def __str__(self):
        return self.name


class Complaint(models.Model):
    title = models.CharField(max_length=100)
    complaint = models.TextField()
    tag = models.ForeignKey(Tag)
    account = models.ForeignKey(Account)
    time = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return self.title + ' [' + self.account.user.username+']'


class Comment(models.Model):
    account = models.ForeignKey(Account)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    complaint = models.ForeignKey(Complaint)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    def __str__(self):
        return  self.text[:5] + '... [' + self.account.user.username+']'


class Reply(models.Model):
    account = models.ForeignKey(Account)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment)

    def __str__(self):
        return  self.text[:5] + '... [' + self.account.user.username+']'
