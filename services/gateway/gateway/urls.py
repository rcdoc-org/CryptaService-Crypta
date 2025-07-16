"""
URL configuration for gateway project.

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
from django.urls import path
from api.views import (
    CreateUserView_v1,
    LoginView_v1,
    TokenRefreshView_v1,
    UsersView_v1,
    RolesView_v1,
    RoleDetailView_v1,
    TokensView_v1,
    OrganizationsView_v1,
    OrganizationDetailView_v1,
    LoginAttemptsView_v1,
    CryptaGroupsView_v1,
    CryptaGroupDetailView_v1,
    QueryPermissionsView_v1,
    QueryPermissionDetailView_v1,
    VerifyMfaView_v1,
    SSOLoginView_v1,
    SSOCallbackView_v1,
    FilterTreeView_v1,
    FilterResultsView_v1,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/register/', CreateUserView_v1.as_view(), name='register'),
    path('users/', UsersView_v1.as_view(), name='users'),
    path('users/<int:pk>/', UsersView_v1.as_view(), name='user-detail'),
    path('roles/', RolesView_v1.as_view(), name='roles'),
    path('roles/create/', RoleDetailView_v1.as_view(), name='roles-create'),
    path('roles/<int:pk>/', RoleDetailView_v1.as_view(), name='role-detail'),
    path('tokens/', TokensView_v1.as_view(), name='tokens'),
    path('organizations/', OrganizationsView_v1.as_view(), name='organizations'),
    path('organizations/create/', OrganizationDetailView_v1.as_view(), name='organization-detail'),
    path('organizations/<int:pk>/', OrganizationDetailView_v1.as_view(), name='organization-detail'),
    path('login_attempts/', LoginAttemptsView_v1.as_view(), name='login_attempts'),
    path('crypta_groups/', CryptaGroupsView_v1.as_view(), name='crypta_groups'),
    path('crypta_groups/create/', CryptaGroupDetailView_v1.as_view(), name='crypta_group-detail'),
    path('crypta_groups/<int:pk>/', CryptaGroupDetailView_v1.as_view(), name='crypta_group-detail'),
    path('query_permissions/', QueryPermissionsView_v1.as_view(), name='query_permissions'),
    path('query_permissions/create/', QueryPermissionDetailView_v1.as_view(), name='query_permission-detail'),
    path('query_permissions/<int:pk>/', QueryPermissionDetailView_v1.as_view(), name='query_permission-detail'),
    path('api/v1/users/register/', CreateUserView_v1.as_view(), name='register'),
    path('users/verify_mfa/', VerifyMfaView_v1.as_view(), name='verify_mfa'),
    path('users/login/', LoginView_v1.as_view(), name='login'),
    path('api/v1/tokens/retrieve/', LoginView_v1.as_view(), name='get_token'),
    path('tokens/refresh/', TokenRefreshView_v1.as_view(), name='token_refresh'),
    path('sso/login/', SSOLoginView_v1.as_view(), name='sso_login'),
    path('sso/callback/', SSOCallbackView_v1.as_view(), name='sso_callback'),
    path('filter_tree/', FilterTreeView_v1.as_view(), name='filter_tree'),
    path('filter_results/', FilterResultsView_v1.as_view(), name='filter_results'),
]
