"""
URL configuration for school assessment project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API文档配置
schema_view = get_schema_view(
    openapi.Info(
        title="School Data Culture Assessment API",
        default_version='v1',
        description="中小学校数据文化成熟度评估监测系统API文档",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # 使用命名路由跳转到 Django 管理入口，避免地址变更后跳转失效。
    path('', RedirectView.as_view(pattern_name='admin:index', permanent=False)),
    
    path('django-admin/', admin.site.urls),
    
    # API文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API路由
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.schools.urls')),
    path('api/', include('apps.assessments.urls')),
    path('api/surveys/', include('apps.surveys.urls')),
    path('api/', include('apps.reports.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),
    path('api/schools/', include('apps.schools.urls')),
    
    # 公开内容接口
    path('api/', include('apps.admin_panel.public_urls')),

    path('api/region-admin/', include('apps.regions.urls_region_admin')),

]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
