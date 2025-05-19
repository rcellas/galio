from django.urls import path
from .views import scraped_items

urlpatterns = [
    path('api/scraped-items/', scraped_items),
]