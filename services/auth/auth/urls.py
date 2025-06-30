"""
URL configuration for auth project.

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
from api.views import (
    CreateUserView,
    UserListView,
    UserDetailView,
    RoleListCreateView,
    RoleDetailView,
    TokenListView,
    OrganizationListCreateView,
    OrganizationDetailView,
    LoginAttemptListView,
    CryptaGroupListCreateView,
    CryptaGroupDetailView,
    QueryPermissionListCreateView,
    QueryPermissionDetailView,
    LoggingTokenObtainPairView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/register/', CreateUserView.as_view(), name='register'),
    path('api/v1/users/', UserListView.as_view(), name='user-list'),
    path('api/v1/users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    path('api/v1/roles/', RoleListCreateView.as_view(), name='role-list'),
    path('api/v1/roles/create/', RoleListCreateView.as_view(), name='role-list'),
    path('api/v1/roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),

    path('api/v1/tokens/', TokenListView.as_view(), name='token-list'),

    path('api/v1/organizations/', OrganizationListCreateView.as_view(), name='organization-list'),
    path('api/v1/organizations/create/', OrganizationListCreateView.as_view(), name='organization-list'),
    path('api/v1/organizations/<int:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),

    path('api/v1/login_attempts/', LoginAttemptListView.as_view(), name='login-attempt-list'),

    path('api/v1/crypta_groups/', CryptaGroupListCreateView.as_view(), name='crypta-group-list'),
    path('api/v1/crypta_groups/create/', CryptaGroupListCreateView.as_view(), name='crypta-group-list'),
    path('api/v1/crypta_groups/<int:pk>/', CryptaGroupDetailView.as_view(), name='crypta-group-detail'),

    path('api/v1/query_permissions/', QueryPermissionListCreateView.as_view(), name='query-permission-list'),
    path('api/v1/query_permissions/create/', QueryPermissionListCreateView.as_view(), name='query-permission-list'),
    path('api/v1/query_permissions/<int:pk>/', QueryPermissionDetailView.as_view(), name='query-permission-detail'),
    # path('api/v1/tokens/retrieve/', TokenObtainPairView.as_view(), name='get_token'),
    path('api/v1/tokens/retrieve/', LoggingTokenObtainPairView.as_view(), name='get_token'),
    path('api/v1/tokens/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
