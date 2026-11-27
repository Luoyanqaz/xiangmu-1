from typing import Any, Dict, List, Tuple

from apps.surveys.models import SurveyResponse


def _is_blank(val: Any) -> bool:
    """
    只把 None / 空字符串 / 空列表 / 空字典判为未填。
    注意：0 和 False 都算已填写。
    """
    if val is None:
        return True

    if isinstance(val, str) and val.strip() == "":
        return True

    if isinstance(val, (list, tuple, dict)) and len(val) == 0:
        return True

    return False


def _require(instance: Any, fields: List[str]) -> Tuple[bool, List[str]]:
    """
    instance 存在且 fields 都不空 => True
    """
    if not instance:
        return False, fields

    missing = []

    for field in fields:
        if _is_blank(getattr(instance, field, None)):
            missing.append(field)

    return len(missing) == 0, missing


def compute_module_status(assessment) -> Dict[str, bool]:
    """
    新版模块完成状态判断。

    - literacy：教师问卷、学生问卷各至少有 1 份答卷
    - institution：按新版 B11/B31/B32 三选一逻辑判断
    - behavior：按新版 C11/C12/C22 字段判断
    - asset：按 D21 两个前置判断和五类数据量逻辑判断
    - technology：按 E11/E21 联动逻辑判断
    """

    from apps.assessments.models import (
        InstitutionAssessment,
        BehaviorAssessment,
        AssetAssessment,
        TechnologyAssessment,
    )

    # -------------------------
    # A) 数据素养：新版仅教师、学生问卷
    # -------------------------
    if assessment.check_survey_quality:
        roles = assessment.survey_instances.values_list('template__survey_type', flat=True)
        literacy_ok = assessment.survey_snapshot is not None or {'teacher', 'student'}.issubset(roles)
    else:
        roles = SurveyResponse.objects.filter(instance__assessment=assessment).values_list(
            'instance__template__survey_type', flat=True)
        literacy_ok = {'teacher', 'student'}.issubset(roles)

    # -------------------------
    # B) 数据制度
    # -------------------------
    institution = InstitutionAssessment.objects.filter(
        assessment=assessment
    ).first()

    institution_ok = False

    if institution:
        base_ok, _ = _require(institution, [
            # B11 新版字段
            "leadership_group_type",

            # B12
            "meeting_activity_count",

            # B21 / B22 前置判断
            "has_data_staff",
            "has_training",

            # B31 / B32 新版三选一字段
            "management_doc_status",
            "practice_doc_status",
        ])

        cond_ok = True

        # B21：配备数据管理人员时，专兼职人数和职责明确情况必填
        if institution.has_data_staff is True:
            ok, _ = _require(institution, [
                "fulltime_staff_count",
                "parttime_staff_count",
                "has_clear_responsibilities",
            ])
            cond_ok = cond_ok and ok

        # B22：有培训时，培训次数和证书数量必填
        if institution.has_training is True:
            ok, _ = _require(institution, [
                "training_count",
                "national_cert_count",
                "provincial_cert_count",
                "city_cert_count",
            ])
            cond_ok = cond_ok and ok

        # B31：只有选择“已在相关制度或规范文件中作出明确要求”时，才要求文件份数和上传文件
        if institution.management_doc_status == "clear_required":
            ok, _ = _require(institution, [
                "management_doc_count",
                "management_doc_files",
            ])
            cond_ok = cond_ok and ok

        # B32：只有选择“已发布指南、操作说明或工作手册”时，才要求文件份数和上传文件
        if institution.practice_doc_status == "published":
            ok, _ = _require(institution, [
                "practice_doc_count",
                "practice_doc_files",
            ])
            cond_ok = cond_ok and ok

        institution_ok = base_ok and cond_ok

    # -------------------------
    # C) 数据行为
    # -------------------------
    behavior = BehaviorAssessment.objects.filter(
        assessment=assessment
    ).first()

    behavior_ok = False

    if behavior:
        base_ok, _ = _require(behavior, [
            # C11 教师数据行为
            "teacher_device_use_freq",
            "teacher_platform_use_freq",
            "teacher_data_behavior_items",

            # C12 学生数据行为
            "student_device_provision",
            "student_account_status",
            "student_data_behavior_items",

            # C21 数据应用特色成果
            "published_paper_count",
            "published_book_count",
            "case_national_count",
            "case_provincial_count",
            "case_city_count",
            "award_national_count",
            "award_provincial_count",
            "award_city_count",

            # C22 数据应用社会影响
            "media_national_count",
            "media_provincial_count",
            "media_city_count",
            "conference_national_count",
            "conference_provincial_count",
            "conference_city_count",
            "public_account_post_count",
            "visit_count",
        ])

        cond_ok = True

        teacher_items = behavior.teacher_data_behavior_items or []
        student_items = behavior.student_data_behavior_items or []

        # 选择“其他”时，补充说明必填
        if "other" in teacher_items:
            cond_ok = cond_ok and not _is_blank(behavior.teacher_data_behavior_other)

        if "other" in student_items:
            cond_ok = cond_ok and not _is_blank(behavior.student_data_behavior_other)

        behavior_ok = base_ok and cond_ok

    # -------------------------
    # D) 数据资产
    # -------------------------
    asset = AssetAssessment.objects.filter(
        assessment=assessment
    ).first()

    asset_ok = False

    if asset:
        # 第一问必须填写：是否统一管理
        asset_ok = not _is_blank(asset.has_unified_data_management)

        # 如果未统一管理，后续不强制填写
        if asset_ok and asset.has_unified_data_management is True:
            # 第二问必须填写：是否能统计查询
            asset_ok = not _is_blank(asset.can_query_data_assets)

            # 如果能统计查询，才要求四类主要数据的统计方式与必要数据量
            if asset_ok and asset.can_query_data_assets is True:
                stat_rules = [
                    ("teaching_data_stat_method", "teaching_data_volume"),
                    ("teacher_student_data_stat_method", "teacher_student_data_volume"),
                    ("digital_resource_data_stat_method", "digital_resource_data_volume"),
                    ("campus_admin_data_stat_method", "campus_admin_data_volume"),
                ]

                for method_field, volume_field in stat_rules:
                    method = getattr(asset, method_field, None)

                    if _is_blank(method):
                        asset_ok = False
                        break

                    # 无法统计时，不要求填写数据量
                    # 可部分估算 / 可系统查询时，要求填写数据量
                    if method in ["estimated", "system_query"]:
                        volume = getattr(asset, volume_field, None)

                        if _is_blank(volume):
                            asset_ok = False
                            break

                # other_type_data_volume 是选填，不参与完成状态判断

    # -------------------------
    # E) 数据技术
    # -------------------------
    technology = TechnologyAssessment.objects.filter(
        assessment=assessment
    ).first()

    technology_ok = False

    if technology:
        base_ok, _ = _require(technology, [
            "has_independent_data_center",
            "student_device_ratio",
            "teacher_device_ratio",
            "has_data_platform",
            "platform_build_mode",
            "has_security_incident",
        ])

        cond_ok = True

        # E11：已设立独立数据中心时，需要填写 B 级要求达成情况
        if technology.has_independent_data_center is True:
            cond_ok = cond_ok and not _is_blank(technology.data_center_standard)

        # E21：完全自建 / 外部和自建并行时，需要填写认证数量和认证比例
        if technology.platform_build_mode in ["self_built", "mixed"]:
            ok, _ = _require(technology, [
                "security_certified_count",
                "security_certified_ratio",
            ])
            cond_ok = cond_ok and ok

        # platform_build_mode == external 时，不要求认证数量和认证比例

        technology_ok = base_ok and cond_ok

    return {
        "literacy": literacy_ok,
        "institution": institution_ok,
        "behavior": behavior_ok,
        "asset": asset_ok,
        "technology": technology_ok,
    }
