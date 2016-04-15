from django.conf.urls import include, url
from complain.views.views import *
from complain.views.ThreadViews import *

urlpatterns =  [
        url(r'^$', Index.as_view(), name='index'),
        url(r'^login/$', Login.as_view(), name='login'),
        url(r'^delete/$', delete, name='delete'),
        url(r'^edit/$', edit, name='edit'),
        url(r'^okay/$', okay, name='okay'),
        url(r'^staffpage/$', staff_page, name="staffpage"),
        url(r'^signup/$', Signup.as_view(), name='signup'),
        url(r'^thread/$', get_thread_json, name='thread'),
        url(r'^notifications/$', get_notifications, name='notifications'),
        url(r'^threads/$', get_threads_json, name='threads'),
        url(r'^threads/tagged/([a-zA-Z0-9]+)/', ThreadPage.as_view(), name='tagged-threads'),
        url(r'^threads/recent/', get_recent_threads, name='recent-threads'),
        url(r'^threads/top/', get_top_threads, name='top-threads'),
        url(r'^threads/favourite/', get_favourite_threads, name='favourite-threads'),
        url(r'^threads/user/([0-9]+)/', get_user_threads, name='user-threads'),
        url(r'^logout/$', logout_user, name='logout'),
        url(r'^vote/', vote, name='vote'),
        url(r'^post-thread/', Post.as_view(), name='post'),
        url(r'^threads/search/$', ThreadPage.as_view(), name='search'),
        url(r'^thread/([0-9]+)/', ThreadPage.as_view(), name='get-thread'),
        url(r'^thread/delete/([0-9]+)/', delete_thread, name='delete-thread'),
        url(r'^comment/', comment, name='comment'),
        url(r'^get-comments/', get_comments, name='get_comments'),
        url(r'^reply/', reply, name='reply'),
        url(r'^error/', error, name='error'),
        url(r'^new-social/', new_social, name='new_social'),
        url(r'^comment-delete/', delete_comment, name='delete_comment'),
        url(r'^tags/', get_tags, name='get_tags'),
        url(r'^profile/([0-9]+)/', Profile.as_view(), name='profile'),
        url(r'^profile-update/', profile_update, name='profile_update'),
        url(r'^image-update/', image_update, name='image_update'),

        url(r'^post-concern/', Concern.as_view(), name='concern'),

]
