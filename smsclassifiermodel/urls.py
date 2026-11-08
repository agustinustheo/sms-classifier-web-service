from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home, name="classify-home"),
    path("", views.classify_text, name="classify-test"),
]
