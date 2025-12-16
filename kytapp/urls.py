# kytapp/urls.py
from django.urls import path
from .views import Round1View
from .views import Round2View
from .views import Round3View
from .views import Round4View
from .views import StartNewSessionView
from .views import HomeView
from .views import CompleteView
from django.urls import path
from django.shortcuts import render

app_name = 'kytapp'

urlpatterns = [
    path('start/', StartNewSessionView.as_view(), name='start'),
    path('home/<int:pk>/', HomeView.as_view(), name='home'),
    path('round1/<int:pk>/', Round1View.as_view(), name='round1'),
    path('round2/<int:pk>/', Round2View.as_view(), name='round2'),
    path('round3/<int:pk>/', Round3View.as_view(), name='round3'),
    path('round4/<int:pk>/', Round4View.as_view(), name='round4'),
    path('complete/<int:pk>/', CompleteView.as_view(), name='complete'),
]

