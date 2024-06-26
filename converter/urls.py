"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert', views.convert, name='convert'),
    path('conversion/<str:project_link>', views.conversion, name='conversion'),
    path('download/<str:project_link>', views.download, name='download'),
    path('download-sb3/<str:project_link>', views.download_sb3, name='download_sb3'),
    path('delete/<str:project_link>', views.delete, name='delete'),
    path('delete-confirmed/<str:project_link>', views.delete_confirmed, name='delete_confirmed'),
]
