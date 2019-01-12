from django.urls import path
from . import views
from . import sms_classifier_model

urlpatterns = [
    path('home/', views.home, name="classify-home"),
    path('', sms_classifier_model.classify_text, name="classify-test"),
]