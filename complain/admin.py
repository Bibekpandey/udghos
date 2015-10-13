from django.contrib import admin
from complain.models import *

admin.autodiscover()

admin.site.register(Account)
admin.site.register(Tag)
admin.site.register(Thread)
admin.site.register(Comment)
