from django.urls import path
from . import views

urlpatterns = [
    path('get_balloon_image/<slug:balloon_id>/', views.get_balloon_image, name='get_balloon_image'),
]
