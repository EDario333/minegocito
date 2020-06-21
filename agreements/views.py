from django.shortcuts import render

def main(request):
	return render(request, 'agreements/main/index.html')