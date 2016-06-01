from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt
from complain.views.views import *
from complain.views.ThreadViews import *

urlpatterns =  [
        url(r'^$', Index.as_view(), name='index'),

        url(r'^login/$', Login.as_view(), name='login'),
        url(r'^logout/$', logout_user, name='logout'),
        url(r'^signup/$', Signup.as_view(), name='signup'),
        url(r'^verify/([a-zA-Z0-9!@#$^*()]+)/$', verify, name='verify'),
        url(r'^not-verified/$', verify_page, name='verify-page'),

        url(r'^staffpage/$', staff_page, name="staffpage"),
        url(r'^delete/$', delete, name='delete'),
        url(r'^edit/$', edit, name='edit'),
        url(r'^okay/$', okay, name='okay'),

        url(r'^notifications/$', get_notifications, name='notifications'),
        url(r'^mark-read/$', mark_read_notifications, name="mark-read"),
        
        url(r'^thread/$', get_thread_json, name='thread'),
        url(r'^threads/$', get_threads_json, name='threads'),
        url(r'^threads/tagged/([a-zA-Z0-9]+)/', ThreadPage.as_view(), name='tagged-threads'),
        url(r'^threads/recent/', get_recent_threads, name='recent-threads'),
        url(r'^threads/top/', get_top_threads, name='top-threads'),
        url(r'^threads/favourite/', get_favourite_threads, name='favourite-threads'),
        url(r'^threads/user/([0-9]+)/', get_user_threads, name='user-threads'),
        url(r'^threads/search/$', ThreadPage.as_view(), name='search'),
        url(r'^thread/(?P<thread_id>[0-9]+)/', ThreadPage.as_view(), name='get-thread'),
        url(r'^thread/delete/([0-9]+)/', delete_thread, name='delete-thread'),
        url(r'^post-thread/', Post.as_view(), name='post'),

        url(r'^vote/', vote, name='vote'),
        url(r'^comment/', comment, name='comment'),
        url(r'^comment-delete/', delete_comment, name='delete_comment'),
        url(r'^get-comments/', get_comments, name='get_comments'),

        url(r'^tags/', get_tags, name='get-tags'),
        url(r'^targets/', get_targets, name='get-targets'),

        #url(r'^reply/', reply, name='reply'),
        url(r'^error/', error, name='error'),
        url(r'^new-social/', new_social, name='new_social'),

        url(r'^profile/([0-9]+)/', Profile.as_view(), name='profile'),
        url(r'^profile-update/', profile_update, name='profile_update'),
        url(r'^image-update/', image_update, name='image_update'),

        url(r'^post-concern/', Concern.as_view(), name='concern'),

        url(r'^post-review/', post_review, name='review'),
        url(r'^how-it-works/', how_it_works, name='work'),
        url(r'^about/', about, name='about'),
        url(r'^mynotifications/', Mynotifications.as_view(), name='mynotifications'),
        url(r'^settings/', Settings.as_view(), name='settingss'),



        # settings
        url(r'^change-password/', change_password, name='change-password'),

        # activities
        url(r'^activities/', get_activities, name='get-activities'),


]
