from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.assessments.models import Assessment
from apps.assessments.serializers import RegionAssessmentListSerializer

from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated

from apps.assessments.models import Assessment
from apps.regions.pagination import StandardPagePagination
from .permissions import IsRegionAdmin
from .serializers_region_admin import RegionAssessmentListItemSerializer
from .region_report_ai_service import RegionReportAIService
import logging

from apps.assessments.serializers import (
    InstitutionAssessmentSerializer,
    BehaviorAssessmentSerializer,
    AssetAssessmentSerializer,
    TechnologyAssessmentSerializer,
)

logger = logging.getLogger(__name__)
class RegionAssessmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 必须是区域管理员
        if user.role != 'region_admin':
            return Response(
                {'success': False, 'message': '无权限访问'},
                status=403
            )

        # 必须绑定区县
        region = getattr(user, 'managed_region', None)
        if not region:
            return Response(
                {'success': False, 'message': '未绑定区域'},
                status=400
            )

        # 查询该区县下的评估
        assessments = Assessment.objects.filter(
            school__region=region
        ).select_related('school').order_by('-created_at')

        serializer = RegionAssessmentListSerializer(assessments, many=True)

        return Response({
            'success': True,
            'message': 'success',
            'data': {
                'region': {
                    'id': region.id,
                    'name': region.name,
                    'province': region.province,
                    'city': region.city,
                },
                'assessments': serializer.data
            }
        })

class RegionAssessmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        user = request.user

        # 必须是区域管理员
        if user.role != 'region_admin':
            return Response(
                {'success': False, 'message': '无权限访问'},
                status=403
            )

        # 必须绑定区域
        region = getattr(user, 'managed_region', None)
        if not region:
            return Response(
                {'success': False, 'message': '未绑定区域'},
                status=400
            )

        # 获取评估
        assessment = get_object_or_404(
            Assessment.objects.select_related('school'),
            id=assessment_id
        )

        # 校验评估是否属于该区域
        if assessment.school.region_id != region.id:
            return Response(
                {'success': False, 'message': '无权限访问该评估'},
                status=403
            )

        # 组装返回数据（只读）
        data = {
            'assessment': {
                'id': assessment.id,
                'school': {
                    'id': assessment.school.id,
                    'name': assessment.school.name
                },
                'status': assessment.status,
                'total_score': assessment.total_score,
                'maturity_level': assessment.maturity_level,
                'completed_at': assessment.completed_at,
            },
            'institution': InstitutionAssessmentSerializer(
                getattr(assessment, 'institution', None)
            ).data if hasattr(assessment, 'institution') else None,
            'behavior': BehaviorAssessmentSerializer(
                getattr(assessment, 'behavior', None)
            ).data if hasattr(assessment, 'behavior') else None,
            'asset': AssetAssessmentSerializer(
                getattr(assessment, 'asset', None)
            ).data if hasattr(assessment, 'asset') else None,
            'technology': TechnologyAssessmentSerializer(
                getattr(assessment, 'technology', None)
            ).data if hasattr(assessment, 'technology') else None,
        }

        return Response({
            'success': True,
            'message': 'success',
            'data': data
        })


def api_ok(data=None, message="success"):
    return Response({"success": True, "message": message, "data": data or {}})


def api_fail(message="error", http_code=http_status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "message": message}, status=http_code)


class RegionAdminAssessmentListView(APIView):
    permission_classes = [IsAuthenticated, IsRegionAdmin]

    def get(self, request):
        region = request.user.managed_region

        qs = (
            Assessment.objects
            .select_related("school", "school__region")
            .filter(school__region=region)
        )

        # ---- filters ----
        status_v = request.query_params.get("status")
        if status_v:
            qs = qs.filter(status=status_v)

        maturity = request.query_params.get("maturity_level")
        if maturity:
            qs = qs.filter(maturity_level=maturity)

        school_name = request.query_params.get("school_name")
        if school_name:
            qs = qs.filter(school__name__icontains=school_name)

        has_report = request.query_params.get("has_report")
        if has_report in ("true", "false"):
            if has_report == "true":
                qs = qs.exclude(report_file="").exclude(report_file__isnull=True)
            else:
                qs = qs.filter(Q(report_file="") | Q(report_file__isnull=True))

        # ---- ordering ----
        ordering = request.query_params.get("ordering") or "-completed_at,-created_at"
        allowed = {
            "completed_at", "-completed_at",
            "created_at", "-created_at",
            "total_score", "-total_score",
            "school__name", "-school__name",
        }
        order_fields = [f.strip() for f in ordering.split(",") if f.strip() in allowed]
        if order_fields:
            qs = qs.order_by(*order_fields)

        # ---- summary（基于过滤前 or 过滤后？建议：过滤后更符合页面）----
        # 这里用过滤后的 qs 统计：更符合“当前筛选结果”
        summary = qs.aggregate(
            school_count=Count("school", distinct=True),
            has_assessment_count=Count("id"),
            completed_count=Count("id", filter=Q(status="completed")),
            report_count=Count("id", filter=~Q(report_file="") & Q(report_file__isnull=False)),
        )

        # ---- paginate ----
        paginator = StandardPagePagination()
        page_qs = paginator.paginate_queryset(qs, request, view=self)

        serializer = RegionAssessmentListItemSerializer(
            page_qs, many=True, context={"request": request}
        )

        data = {
            "region": {
                "id": region.id,
                "code": region.code,
                "province": region.province,
                "city": region.city,
                "name": region.name,
            },
            "summary": summary,
            "assessments": serializer.data,
            "pagination": {
                "page": paginator.page.number,
                "page_size": paginator.get_page_size(request),
                "total": paginator.page.paginator.count,
                "total_pages": paginator.page.paginator.num_pages,
            },
        }
        return api_ok(data)


import hashlib
import json
from .models import RegionReportSuggestionCache

class RegionReportAISuggestionsView(APIView):
    """
    区域报告 AI 建议接口。

    逻辑：
    1. 前端提交当前区域报告数据；
    2. 后端根据数据生成 data_hash；
    3. 如果缓存存在且 data_hash 一致，直接返回缓存；
    4. 如果缓存不存在或 data_hash 变化，则调用大模型重新生成并保存。
    """

    permission_classes = [IsAuthenticated]
    CACHE_SCHEMA_VERSION = 3

    def post(self, request):
        try:
            report_data = request.data or {}

            region = report_data.get("region") or {}
            region_code = self._get_region_code(region)
            region_name = self._get_region_name(region)

            if not region_code:
                return Response({
                    "success": False,
                    "message": "缺少区域信息，无法生成区域报告建议",
                    "data": {}
                }, status=400)

            data_hash = self._make_data_hash(report_data)

            cache = RegionReportSuggestionCache.objects.filter(
                region_code=region_code
            ).first()

            # 命中缓存：不调用大模型
            if cache and cache.data_hash == data_hash and cache.suggestions:
                return Response({
                    "success": True,
                    "message": "success",
                    "cache_hit": True,
                    "data_hash": data_hash,
                    "updated_at": cache.updated_at,
                    "data": cache.suggestions
                })

            # 未命中缓存：调用大模型
            service = RegionReportAIService()
            suggestions = service.generate_all_suggestions(report_data)

            if cache:
                cache.region_name = region_name
                cache.data_hash = data_hash
                cache.suggestions = suggestions
                cache.payload_snapshot = self._safe_snapshot(report_data)
                cache.save()
            else:
                RegionReportSuggestionCache.objects.create(
                    region_code=region_code,
                    region_name=region_name,
                    data_hash=data_hash,
                    suggestions=suggestions,
                    payload_snapshot=self._safe_snapshot(report_data)
                )

            return Response({
                "success": True,
                "message": "success",
                "cache_hit": False,
                "data_hash": data_hash,
                "data": suggestions
            })

        except Exception as e:
            logger.exception("区域报告 AI 建议生成失败")

            return Response({
                "success": False,
                "message": str(e) or "区域报告 AI 建议生成失败",
                "data": {
                    "level_suggestions": {
                        "initial": "",
                        "growing": "",
                        "mature": "",
                        "leading": ""
                    },
                    "development": {
                        "summary": "",
                        "items": [],
                        "conclusion": ""
                    }
                }
            }, status=500)

    def _get_region_code(self, region):
        """
        优先使用行政编码 code。
        如果没有 code，则退化使用 id。
        """
        code = region.get("code") or region.get("id")
        return str(code) if code else ""

    def _get_region_name(self, region):
        return "".join([
            str(region.get("province") or ""),
            str(region.get("city") or ""),
            str(region.get("name") or "")
        ])

    def _make_data_hash(self, report_data):
        """
        计算区域报告数据指纹。

        前端如果传了 _hash_base，则优先用 _hash_base。
        这样可以避免把样式、颜色、无关字段纳入 hash。
        """
        hash_base = {
            "schema_version": self.CACHE_SCHEMA_VERSION,
            "report_data": report_data.get("_hash_base") or report_data,
        }

        normalized = json.dumps(
            hash_base,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":")
        )

        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _safe_snapshot(self, report_data):
        """
        保存生成时的数据快照。
        避免后续排查时不知道 AI 建议是基于什么数据生成的。
        """
        return {
            "region": report_data.get("region") or {},
            "summary": report_data.get("summary") or {},
            "dimension_average": report_data.get("dimension_average") or {},
            "level_distribution": report_data.get("level_distribution") or [],
            "level_analysis": report_data.get("level_analysis") or [],
            "_hash_base": report_data.get("_hash_base") or {}
        }


class AdminRegionReportAISuggestionsView(RegionReportAISuggestionsView):
    """超级管理员：指定区域报告 AI 建议接口"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_admin_user():
            return Response({
                "success": False,
                "message": "只有超级管理员可以访问",
                "data": {}
            }, status=403)

        return super().post(request)
