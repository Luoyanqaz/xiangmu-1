from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.regions.models import Region
from .statistics import region_statistics


def resolve_report_region(request, submitted_region=None):
    """Resolve scope on the server; school accounts cannot enumerate regional results."""
    if request.user.role == 'region_admin':
        region = Region.objects.filter(region_admin=request.user).first()
        if not region:
            raise PermissionDenied('账号尚未绑定区域')
        if submitted_region:
            supplied_id = submitted_region.get('id')
            supplied_code = submitted_region.get('code')
            if ((supplied_id and str(supplied_id) != str(region.id)) or
                    (supplied_code and str(supplied_code) != str(region.code))):
                raise PermissionDenied('不能访问其他区域的报告')
    elif request.user.is_admin_user():
        params = submitted_region if submitted_region is not None else request.query_params
        region_id = params.get('region_id') or params.get('id')
        if region_id:
            try:
                region_id = int(region_id)
            except (ValueError, TypeError):
                raise ValidationError('区域编号不合法')
            region = get_object_or_404(Region, pk=region_id)
        elif params.get('code'):
            region = get_object_or_404(Region, code=params['code'])
        else:
            names = {'province': params.get('province'), 'city': params.get('city'),
                     'name': params.get('district') or params.get('name')}
            if not all(names.values()):
                raise ValidationError('请提供区域编号或完整省、市、区县')
            region = Region.objects.filter(**names).first()
            if not region:
                return {'id': None, 'code': '|'.join(names.values()), **names}
    else:
        raise PermissionDenied('只有区域管理员或平台管理员可以访问区域报告')
    return {'id': region.id, 'code': region.code, 'province': region.province,
            'city': region.city, 'name': region.name}


class RegionReportStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = resolve_report_region(request)
        return Response({'success': True, 'data': region_statistics(scope)})
