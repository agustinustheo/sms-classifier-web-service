from django.urls import path
from . import views
from . import sms_classifier_model

urlpatterns = [
    path('', views.home, name="classify-home"),
    path('test/', sms_classifier_model.classify_text, name="classify-test"),
]