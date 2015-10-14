from django.conf.urls import include, url
from complain.views import *

urlpatterns =  [
        url(r'^$', Index.as_view(), name='index'),
        url(r'^login/', Login.as_view(), name='login'),
        url(r'^logout/', logout_user, name='logout'),
        url(r'^upvote/', upvote, name='upvote'),
        url(r'^post-thread/([a-z]+)/', Post.as_view(), name='post'),
]
