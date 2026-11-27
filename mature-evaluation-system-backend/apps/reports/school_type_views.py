from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsPlatformAdmin
from apps.regions.models import Region
from apps.schools.models import School
from .school_type_statistics import school_type_statistics
from .statistics_views import resolve_report_region


class SchoolTypeReportOptionsView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        regions = list(Region.objects.order_by('province', 'city', 'name', 'id')
                       .values('id', 'code', 'province', 'city', 'name'))
        known = {(row['province'], row['city'], row['name']) for row in regions}
        # Include complete legacy locations even when no Region row was created.
        locations = (School.objects.filter(region__isnull=True).exclude(province='').exclude(city='')
                     .exclude(district='').values_list('province', 'city', 'district').distinct())
        for province, city, name in locations:
            if (province, city, name) not in known:
                regions.append({'id': None, 'code': '', 'province': province, 'city': city, 'name': name})
        regions.sort(key=lambda row: (row['province'], row['city'], row['name'], row['id'] or 0))
        return Response({'success': True, 'data': {
            'regions': regions,
            'school_types': [{'value': key, 'label': label} for key, label in School.SCHOOL_TYPE_CHOICES],
        }})


class SchoolTypeReportStatisticsView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        school_type = request.query_params.get('school_type')
        if school_type not in dict(School.SCHOOL_TYPE_CHOICES):
            raise ValidationError('请选择有效的学校类型')
        scope = resolve_report_region(request)
        return Response({'success': True, 'data': school_type_statistics(scope, school_type)})
