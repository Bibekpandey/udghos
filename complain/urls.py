from django.conf.urls import include, url
from complain.views import *

urlpatterns =  [
        url(r'^$', Index.as_view(), name='index'),
        url(r'^login/', Login.as_view(), name='login'),
        url(r'^post/', Post.as_view(), name='post'),
]
