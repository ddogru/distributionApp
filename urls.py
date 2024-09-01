"""
URL configuration for distributionApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from distributionApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('add-package/', views.add_package, name='add-package'),
    path('add-vehicle/', views.add_vehicle, name='add-vehicle'),
    path('assign-packages/', views.assign_packages, name='assign-packages'),
    path('assign-packages-2/', views.assign_packages_2, name='assign-packages-2'),
    path('package-table/', views.package_table, name='package-table'),
    path('vehicle-table/', views.vehicle_table, name='vehicle-table'),
    path('area-table/', views.area_table, name='area-table'),
path('save-temporary-selection/', views.save_temporary_selection, name='save-temporary-selection'),
]
