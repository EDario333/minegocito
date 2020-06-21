from django.shortcuts import render

from django.db.models import Q

from .models import AppVersions, FeaturesAppVersion, Features

# Create your views here.

def index(request):
	versions = AppVersions.objects.exclude(disabled=True)
	#features = Features.objects.exclude(disabled=True)
	features = Features.objects.all()

	versions_list = []

	for version in versions:
		features_app = []

		for feature in features:
			query = \
				Q(app_version_id=version.id) & \
				Q(feature_id=feature.id) #& \
				#Q(disabled=False)

			feature_app = FeaturesAppVersion.objects.get(query)
			features_app.append({'name': feature.name, 'feature': feature_app})

		versions_list.append({'version': version, 'features': features_app})

	context = {
		'list': versions_list
	}

	return render(request, 'app-versions/index.html', context=context)