from django.views.decorators.csrf import csrf_exempt
import os
import time

@csrf_exepmt
def hook(request):
	if request.method=="POST":
		os.system('echo hook obtained >> /tmp/hook')

