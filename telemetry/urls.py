from django.urls import path
from . import views

urlpatterns = [
    path('get_balloon_image/<slug:balloon_id>/', views.get_balloon_image, name='get_balloon_image'),
    path('rotate_balloon_image/<int:image_id>/', views.rotate_balloon_image, name='rotate_balloon_image'),
    path('deactivate_balloon/<slug:balloon_id>/', views.deactivate_balloon, name='deactivate_balloon'),
]
