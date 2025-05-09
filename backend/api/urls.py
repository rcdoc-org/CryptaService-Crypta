from django.urls import path
from django.conf.urls import handler404
from . import views

# Declare namespace for URLs
app_name = 'api'

handler404 = views.view_404

urlpatterns = [
    path("", views.home, name="home"),
    path('test-404', views.view_404, name='test_404'),
    path('demo/filters/', views.enhanced_filter_view, name='enhanced_filter'),
    path('api/filter_results/', views.filter_results, name='filter_results'),
    path('api/upload-tmp', views.upload_temp, name='upload_temp'),
    path('send-email/', views.send_email, name='send_email'),
    path('demo/details-page/', views.details_page, name='details_page_test'),
    path(
        'demo/details-page/<str:base>/<int:pk>/',
        views.details_page,
        name='details_page'
    )
    
]