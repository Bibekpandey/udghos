from django.contrib import admin
from complain.models import *

admin.autodiscover()

admin.site.register(Account)
admin.site.register(Tag)
admin.site.register(Complaint)
admin.site.register(Comment)
