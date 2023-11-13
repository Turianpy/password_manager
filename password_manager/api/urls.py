from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

v1_router = DefaultRouter()

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', views.signup, name='signup'),
    path('v1/auth/activate/', views.activate, name='activate'),
    path('v1/auth/token/', views.get_token, name='token'),
]
