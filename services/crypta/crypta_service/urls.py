"""
URL configuration for crypta_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from api.views import (
    FilterTreeView_v1,
    FilterResultsView_v1,
    SearchResultsView_v1,
    PersonViewSet,
    LocationViewSet,
)

router = DefaultRouter()
router.register('persons', PersonViewSet, basename='person')
router.register('locations', LocationViewSet, basename='location')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/filter_tree', FilterTreeView_v1.as_view(), name='filter_tree'),
    path('api/v1/filter_results', FilterResultsView_v1.as_view(), name='filter_results'),
    path('api/v1/search', SearchResultsView_v1.as_view(), name='search'),
    path('api/v1/', include(router.urls)),
]
