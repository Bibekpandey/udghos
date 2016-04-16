import os
import time

def hook(request):
	if request.method=="POST":
		os.system('echo hook obtained >> /tmp/hook')

