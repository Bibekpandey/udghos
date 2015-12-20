from django.conf.urls import include, url
from complain.views import *

urlpatterns =  [
        url(r'^$', Index.as_view(), name='index'),
        url(r'^login/', Login.as_view(), name='login'),
        url(r'^logout/', logout_user, name='logout'),
        url(r'^vote/', vote, name='vote'),
        url(r'^post-thread/([a-z]+)/', Post.as_view(), name='post'),
        url(r'^thread/([0-9]+)/', ThreadPage.as_view(), name='thread'),
        url(r'^comment/', comment, name='comment'),
        url(r'^reply/', reply, name='reply'),
        url(r'^error/', error, name='error'),
        url(r'^new-social/', new_social, name='new_social'),

]
