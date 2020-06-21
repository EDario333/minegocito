from django.conf.urls import url

from .views import subscribe, notify_phishing, verify_unique_email

urlpatterns = [
  url(r'^subscribe/', subscribe, name='subscribe-to-newsletter'),
  url(r'^notify-phishing/', notify_phishing, name='notify-phishing-newsletter'),
  url(r'^verify-unique-email/', verify_unique_email, name='verify-unique-email-newsletter'),
]