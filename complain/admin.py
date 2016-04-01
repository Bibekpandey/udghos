from django.contrib import admin
from complain.models import *

admin.autodiscover()

admin.site.register(Account)
admin.site.register(ThreadTag)
admin.site.register(Comment)
admin.site.register(Thread)
admin.site.register(ThreadUpvote)
admin.site.register(ThreadImage)
admin.site.register(ThreadDownvote)
