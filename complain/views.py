from django.shortcuts import render, redirect, Http404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q

from django.views.generic import View


class Index(View):
    def get(self, request):
        self.context = {}
        return render(request, "complain/index.html", self.context)

class Login(View):
    def get(self, request):
        self.context = {}
        return render(request, "complain/login.html", self.context)

class Post(View):
    def get(self, request): 
        self.context = {}
        return HttpResponse('ulala')
