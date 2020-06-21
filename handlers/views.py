from django.shortcuts import render, redirect

from users.views import login
# Create your views here.

def csrf_failure(request, reason=""):
	if request.method == 'POST' and \
	'users/login' in request.path:
		return login(request)
		'''
		context = {
			'csrfmiddlewaretoken': request.POST['csrfmiddlewaretoken']
		}

		return render(request, 'dashboard/index.html', context=context)
		'''

	return redirect('/')