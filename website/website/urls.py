"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from cgen import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('certificate/events/', views.events, name="events"),
    path('certificate/download/<int:certificate_id>/',
         views.certificate_download, name="certificate_download"),
    path('certificate/download/<int:certificate_id>/<str:email>/',
         views.certificate_download, name="certificate_download"),
    path('certificate/download_all/<int:certificate_id>/',
         views.certificate_download_all, name="certificate_download_all"),
    path('certificate/verify/', views.verify, name="verify"),
    path('certificate/verify/<str:key>/', views.verify, name="verify"),
    path('certificate/upload/<int:certificate_id>/',
         views.upload_csv_participants, name="upload"),
]
