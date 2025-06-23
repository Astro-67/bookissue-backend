from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tickets'

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'', views.TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
]
