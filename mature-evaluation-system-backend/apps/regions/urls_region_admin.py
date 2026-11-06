from django.urls import path
from .views_region_admin import (
    RegionAdminOverviewView,
    RegionAdminSchoolListView,
    RegionAdminSchoolAssessmentsView,
    RegionAdminAssessmentDetailView,
    RegionAdminAssessmentListView,
    RegionAdminCreateSchoolView,
    RegionAdminSchoolResetPasswordView,
    RegionAdminSchoolApproveView,
    RegionAdminSchoolDeleteView,
    RegionAdminApplicationApproveView,
    RegionAdminApplicationRejectView,
    RegionAdminApplicationDeleteView,
    RegionAdminSchoolImportView,
    RegionAdminSchoolTemplateView,
)
from .views import RegionReportAISuggestionsView
from apps.reports.statistics_views import RegionReportStatisticsView

urlpatterns = [
    path('region-report/statistics/', RegionReportStatisticsView.as_view(), name='region-report-statistics'),
    path("overview/", RegionAdminOverviewView.as_view(), name="region_admin_overview"),
    path("schools/", RegionAdminSchoolListView.as_view(), name="region_admin_school_list"),
    path("schools/create/", RegionAdminCreateSchoolView.as_view(), name="region_admin_school_create"),
    path("schools/<int:school_id>/assessments/", RegionAdminSchoolAssessmentsView.as_view(), name="region_admin_school_assessments"),
    path("assessments/", RegionAdminAssessmentListView.as_view(), name="region_admin_assessment_list"),
    path("assessments/<int:assessment_id>/", RegionAdminAssessmentDetailView.as_view(), name="region_admin_assessment_detail"),
    path("schools/<int:school_id>/reset-password/", RegionAdminSchoolResetPasswordView.as_view()),
    path("schools/<int:school_id>/approve/", RegionAdminSchoolApproveView.as_view(), name="region_admin_school_approve"),
    path("schools/<int:school_id>/", RegionAdminSchoolDeleteView.as_view(), name="region_admin_school_delete"),
    path("applications/<int:application_id>/approve/", RegionAdminApplicationApproveView.as_view()),
    path("applications/<int:application_id>/reject/", RegionAdminApplicationRejectView.as_view()),
    path("applications/<int:application_id>/", RegionAdminApplicationDeleteView.as_view()),
    path("schools/template/", RegionAdminSchoolTemplateView.as_view()),
    path("schools/import/", RegionAdminSchoolImportView.as_view(), name="region_admin_school_import"),
    path("region-report/ai-suggestions/", RegionReportAISuggestionsView.as_view(), name="region-report-ai-suggestions"),
]
