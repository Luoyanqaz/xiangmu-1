"""
URL configuration for admin_panel app
"""
from django.urls import path
from . import views
from apps.regions.views import AdminRegionReportAISuggestionsView
from apps.reports.statistics_views import RegionReportStatisticsView

urlpatterns = [
    path('region-report/statistics/', RegionReportStatisticsView.as_view(), name='admin-region-report-statistics'),
    # 申请管理
    path('applications/', views.get_application_list, name='admin_application_list'),
    
    # 内容管理（管理员接口）
    path('content/<str:page_key>/', views.update_page_content, name='update_page_content'),
    
    # 实践动态管理（管理员接口）
    path('news/', views.create_news, name='create_news'),
    path('news/<int:pk>/', views.update_news, name='update_news'),
    path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),
    path('news/upload-image/', views.upload_news_image, name='upload_news_image'),
    path(
        "region-report/assessments/",
        views.admin_region_report_assessments,
        name="admin_region_report_assessments"
    ),
    path(
        "region-report/ai-suggestions/",
        AdminRegionReportAISuggestionsView.as_view(),
        name="admin_region_report_ai_suggestions"
    ),
    path(
        'create-region-admin/',
        views.create_region_admin,
        name='create_region_admin'
    ),

    path(
        'region-admin/<int:user_id>/delete/',
        views.delete_region_admin,
        name='delete_region_admin'
    ),
]
