from django.urls import path

from . import views

urlpatterns = [
    path(
        'v1/password/',
        views.PSPViewSet.as_view({'get': 'list'}),
        name='passwords'
    ),
    path(
        'v1/password/<str:service_name>',
        views.PSPViewSet.as_view({'get': 'retrieve', 'post': 'create'}),
        name='password'
    ),
    path('v1/auth/signup/', views.signup, name='signup'),
    path('v1/auth/activate/', views.activate, name='activate'),
    path('v1/auth/token/', views.get_token, name='token'),
]
