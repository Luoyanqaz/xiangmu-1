"""
计分配置文件
所有计分规则集中管理，便于后续调整
"""
from .maturity import MATURITY_LEVELS as SHARED_MATURITY_LEVELS

# 问卷题目范围和满分配置
# ==================== 数据素养维度 (A) ====================

# 问卷题目范围和满分配置
# 注意：题号按照系统保存的 q1、q2、q3... 连续编号计算
LITERACY_SURVEY_CONFIG = {
    'teacher': {
        # 教师问卷：q1-q5 为基本信息，q6-q34 为数据素养量表
        'A11': {'range': (6, 13), 'max_score': 40, 'name': '教师数据意识与思维'},
        'A12': {'range': (14, 20), 'max_score': 35, 'name': '教师数据知识与技能'},
        'A13': {'range': (21, 23), 'max_score': 15, 'name': '教师数据评价与交流'},
        'A14': {'range': (24, 31), 'max_score': 40, 'name': '教师数据应用与创新'},
        'A15': {'range': (32, 34), 'max_score': 15, 'name': '教师数据伦理与隐私'},
    },
    'student': {
        # 学生问卷：q1-q3 为基本信息，q4-q28 为数据素养量表
        # 注意：学生属于 A2 二级指标，但观测点编号仍按正式权重表使用 A31-A35
        'A31': {'range': (4, 10), 'max_score': 35, 'name': '学生数据意识与思维'},
        'A32': {'range': (11, 17), 'max_score': 35, 'name': '学生数据知识与技能'},
        'A33': {'range': (18, 19), 'max_score': 10, 'name': '学生数据评价与交流'},
        'A34': {'range': (20, 25), 'max_score': 30, 'name': '学生数据应用与创新'},
        'A35': {'range': (26, 28), 'max_score': 15, 'name': '学生数据伦理与隐私'},
    }
}

# 5点量表计分规则
SCALE_SCORE_MAPPING = {
    'A': 1, '非常不符合': 1,
    'B': 2, '不符合': 2,
    'C': 3, '一般': 3,
    'D': 4, '符合': 4,
    'E': 5, '非常符合': 5
}


# ==================== 数据制度维度 (B) ====================

INSTITUTION_SCORING_RULES = {
    # B1 数据组织机构
    'B11': {
        'name': '数据领导/工作小组',
        'field': 'leadership_group_type',
        'max_score': 10,
        'rules': {
            'standard': 10,
            'basic': 5,
            'none': 0
        }
    },
    'B12': {
        'name': '数据组织运行情况',
        'field': 'meeting_activity_count',
        'max_score': 10,
        'rules': [
            {'condition': 'lte', 'value': 0, 'score': 0},
            {'condition': 'between', 'min': 0, 'max': 5, 'score': 3},
            {'condition': 'between', 'min': 5, 'max': 15, 'score': 6},
            {'condition': 'gt', 'value': 15, 'score': 10}
        ]
    },
    
    # B2 数据人员配备
    'B21': {
        'name': '数据专职/兼职管理人员',
        'max_score': 20,
        'sub_items': [
            {
                'field': 'has_data_staff',
                'type': 'boolean',
                'rules': {True: 'continue', False: 0}  # False则整个B21为0分
            },
            {
                'field': 'staff_count',
                'type': 'staff_count',
                'max_score': 10,
                'rules': {
                    'fulltime': 5,  # 每名专职5分
                    'parttime': 3   # 每名兼职3分
                }
            },
            {
                'field': 'has_clear_responsibilities',
                'type': 'boolean',
                'rules': {True: 10, False: 0}
            }
        ]
    },
    'B22': {
        'name': '数据人员进修与培训情况',
        'max_score': 30,
        'sub_items': [
            {
                'field': 'has_training',
                'type': 'boolean',
                'rules': {True: 'continue', False: 0}  # False则整个B22为0分
            },
            {
                'field': 'training_count',
                'type': 'range',
                'max_score': 10,
                'rules': [
                    {'condition': 'lte', 'value': 0, 'score': 0},
                    {'condition': 'between', 'min': 0, 'max': 10, 'score': 3},
                    {'condition': 'between', 'min': 10, 'max': 20, 'score': 6},
                    {'condition': 'gt', 'value': 20, 'score': 10}
                ]
            },
            {
                'field': 'certificates',
                'type': 'certificates',
                'max_score': 20,
                'rules': {
                    'national': 5,
                    'provincial': 3,
                    'city': 1
                }
            }
        ]
    },
    
    # B3 数据管理文件
    'B31': {
        'name': '数据管理制度类文件',
        'max_score': 40,
        'status_field': 'management_doc_status',
        'rules': {
            'clear_required': 'continue',
            'follow_policy': 20,
            'self_awareness': 10
        },
        'sub_items': [
            {
                'field': 'management_doc_count_total',
                'type': 'doc_count',
                'max_score': 20,
                'score_per_doc': 5
            },
            {
                'field': 'management_doc_files',
                'type': 'llm_quality',
                'max_score': 20,
                'llm_prompt': '请从规范性、专业性、完整性、特色化四个维度分析该数据管理制度文件的整体质量，给出0-20分的评分。'
            }
        ]
    },
    'B32': {
        'name': '数据实践指导类文件',
        'max_score': 40,
        'status_field': 'practice_doc_status',
        'rules': {
            'published': 'continue',
            'internal_training': 20,
            'self_practice': 10
        },
        'sub_items': [
            {
                'field': 'practice_doc_count_total',
                'type': 'doc_count',
                'max_score': 20,
                'score_per_doc': 5
            },
            {
                'field': 'practice_doc_files',
                'type': 'llm_quality',
                'max_score': 20,
                'llm_prompt': '请从规范性、完整性、可操作性、实用性四个维度分析该数据实践指导文件的整体质量，给出0-20分的评分。'
            }
        ]
    },
}


# ==================== 数据行为维度 (C) ====================

BEHAVIOR_SCORING_RULES = {
    # C1 数据行为监测
    'C11': {
        'name': '教师数据行为',
        'max_score': 30,
        'sub_items': [
            {
                'name': '教师数字化设备使用频次',
                'field': 'teacher_device_use_freq',
                'max_score': 10,
                'rules': [
                    {'condition': 'lte', 'value': 0, 'score': 0},
                    {'condition': 'between', 'min': 0, 'max': 10, 'score': 3},
                    {'condition': 'between', 'min': 10, 'max': 20, 'score': 6},
                    {'condition': 'gt', 'value': 20, 'score': 10}
                ]
            },
            {
                'name': '教师数据相关平台使用频次',
                'field': 'teacher_platform_use_freq',
                'max_score': 10,
                'rules': [
                    {'condition': 'lte', 'value': 0, 'score': 0},
                    {'condition': 'between', 'min': 0, 'max': 10, 'score': 3},
                    {'condition': 'between', 'min': 10, 'max': 20, 'score': 6},
                    {'condition': 'gt', 'value': 20, 'score': 10}
                ]
            },
            {
                'name': '教师常态化数据行为',
                'field': 'teacher_data_behavior_items',
                'max_score': 10,
                'type': 'multi_count',
                'rules': [
                    {'condition': 'lte', 'value': 0, 'score': 0},
                    {'condition': 'between', 'min': 0, 'max': 2, 'score': 3},
                    {'condition': 'between', 'min': 2, 'max': 4, 'score': 6},
                    {'condition': 'gt', 'value': 4, 'score': 10}
                ]
            }
        ]
    },
    'C12': {
        'name': '学生数据行为',
        'max_score': 30,
        'sub_items': [
            {
                'name': '学生数字化设备配备情况',
                'field': 'student_device_provision',
                'max_score': 10,
                'rules': {
                    'none': 3,
                    'computer_room': 6,
                    'computer_room_and_terminal': 10
                }
            },
            {
                'name': '学生平台账号开通情况',
                'field': 'student_account_status',
                'max_score': 10,
                'rules': {
                    'none': 3,
                    'partial': 6,
                    'all': 10
                }
            },
            {
                'name': '学生常态化数据行为',
                'field': 'student_data_behavior_items',
                'max_score': 10,
                'type': 'multi_count',
                'rules': [
                    {'condition': 'lte', 'value': 0, 'score': 0},
                    {'condition': 'between', 'min': 0, 'max': 1, 'score': 3},
                    {'condition': 'between', 'min': 1, 'max': 3, 'score': 6},
                    {'condition': 'gt', 'value': 3, 'score': 10}
                ]
            }
        ]
    },
    
    # C2 数据应用成效
    'C21': {
        'name': '数据应用特色成果',
        'max_score': 60,
        'sub_items': [
            {
                'name': '公开发表成果',
                'max_score': 20,
                'fields': {
                    'published_paper_count': 3,  # 每篇论文3分
                    'published_book_count': 6    # 每部著作6分
                }
            },
            {
                'name': '入选优秀案例',
                'max_score': 20,
                'fields': {
                    'case_national_count': 5,
                    'case_provincial_count': 3,
                    'case_city_count': 1
                }
            },
            {
                'name': '荣誉奖励',
                'max_score': 20,
                'fields': {
                    'award_national_count': 5,
                    'award_provincial_count': 3,
                    'award_city_count': 1
                }
            }
        ]
    },
    'C22': {
        'name': '数据应用社会影响',
        'max_score': 60,
        'sub_items': [
            {
                'name': '媒体宣传报道',
                'max_score': 20,
                'fields': {
                    'media_national_count': 5,
                    'media_provincial_count': 3,
                    'media_city_count': 1
                }
            },
            {
                'name': '会议交流分享',
                'max_score': 20,
                'fields': {
                    'conference_national_count': 5,
                    'conference_provincial_count': 3,
                    'conference_city_count': 1
                }
            },
            {
                'name': '公众号经验分享或创新实践',
                'field': 'public_account_post_count',
                'max_score': 10,
                'score_per_post': 2
            },
            {
                'name': '参观学习',
                'field': 'visit_count',
                'max_score': 10,
                'score_per_visit': 2
            }
        ]
    },
    'C23': {
        'name': '教师对数据应用效果的主观评价',
        'type': 'survey',
        'max_score': 30,
        'survey_ranges': {
            # 教师问卷第四部分：数据应用效果主观评价量表，共6题
            'teacher': (49, 54)
        }
    }
}


# ==================== 数据资产维度 (D) ====================

ASSET_SCORING_RULES = {
    # D1 数据资产意识
    'D11': {
        'name': '教师数据资产价值意识',
        'type': 'survey',
        'max_score': 20,
        # 教师问卷第三部分：q35-q38，共4题
        'survey_range': (35, 38),
        'survey_type': 'teacher'
    },
    'D12': {
        'name': '教师数据资产应用意识',
        'type': 'survey',
        'max_score': 20,
        # 教师问卷第三部分：q39-q42，共4题
        'survey_range': (39, 42),
        'survey_type': 'teacher'
    },
    'D13': {
        'name': '教师数据资产治理意识',
        'type': 'survey',
        'max_score': 30,
        # 教师问卷第三部分：q43-q48，共6题
        'survey_range': (43, 48),
        'survey_type': 'teacher'
    },

    # D2 数据资产积累
        'D21': {
        'name': '数据资产总量',
        'field': 'total_data_volume',
        'max_score': 10,
        # 当前规则单位为 GB：
        # 10TB=10000GB，55TB=55000GB，90TB=90000GB
        'rules': [
            {'condition': 'lte', 'value': 10000, 'score': 2},
            {'condition': 'between', 'min': 10000, 'max': 55000, 'score': 4},
            {'condition': 'between', 'min': 55000, 'max': 90000, 'score': 6},
            {'condition': 'gt', 'value': 90000, 'score': 10}
        ],
        # 新增：不能统一管理或不能统计查询时，D21 原始分直接给 4 分
        'fallback_raw_score': 4
    },

    'D22': {
        'name': '人均数据资产量',
        'field': 'per_capita_data_volume',
        'max_score': 10,
        'rules': [
            {'condition': 'lte', 'value': 0, 'score': 0},
            {'condition': 'between', 'min': 0, 'max': 10, 'score': 2},
            {'condition': 'between', 'min': 10, 'max': 20, 'score': 4},
            {'condition': 'between', 'min': 20, 'max': 40, 'score': 6},
            {'condition': 'gt', 'value': 40, 'score': 10}
        ]
    }
}


# ==================== 数据技术维度 (E) ====================

TECHNOLOGY_SCORING_RULES = {
    # E1 数据基础设施
    'E11': {
        'name': '数据硬件设施',
        'max_score': 30,
        'sub_items': [
            {
                'name': '数据中心标准',
                'field': 'data_center_standard',
                'max_score': 10,
                'rules': {
                    'fully_compliant': 10,
                    'partially_compliant': 6,
                    'not_compliant': 3
                }
            },
            {
                'name': '生机比',
                'field': 'student_device_ratio',
                'max_score': 10,
                'rules': {
                    'high': 3,    # ≥15:1
                    'medium': 6,  # 6:1≤生机比<15:1
                    'low': 10     # <6:1
                }
            },
            {
                'name': '师机比',
                'field': 'teacher_device_ratio',
                'max_score': 10,
                'rules': {
                    'high': 3,    # ≥4:1
                    'medium': 6,  # 1:1≤师机比<4:1
                    'low': 10     # <1:1
                }
            }
        ]
    },

    'E12': {
        'name': '数据系统平台',
        'field': 'has_data_platform',
        'max_score': 10,
        'rules': {
            True: 10,
            False: 0
        }
    },

    # E2 数据安保水平
    'E21': {
        'name': '数据安全合规与认证',
        'max_score': 20,
        # 完全接入外部平台时，5分制直接给2.5分。
        # 因为后面会做 raw / max_score * 5，所以这里 raw_score = 10。
        'external_platform_raw_score': 12,
        'sub_items': [
            {
                'name': '安保认证数量',
                'field': 'security_certified_count',
                'max_score': 10,
                'rules': [
                    {'condition': 'lte', 'value': 0, 'score': 0},
                    {'condition': 'between', 'min': 0, 'max': 2, 'score': 3},
                    {'condition': 'between', 'min': 2, 'max': 4, 'score': 6},
                    {'condition': 'gte', 'value': 5, 'score': 10}
                ]
            },
            {
                'name': '安保认证比例',
                'field': 'security_certified_ratio',
                'max_score': 10,
                'rules': {
                    'zero': 0,
                    'low': 3,     # 0<比例≤40%
                    'medium': 6,  # 40%<比例≤80%
                    'high': 10    # >80%
                }
            }
        ]
    },

    'E22': {
        'name': '数据风险事件记录',
        'field': 'has_security_incident',
        'max_score': 10,
        'rules': {
            True: 0,    # 发生过风险事件
            False: 10   # 未发生风险事件
        }
    }
}


# ==================== 维度权重配置 ====================

# 一级指标权重（五个维度）
DIMENSION_WEIGHTS = {
    'A': 0.3501,  # 数据素养
    'B': 0.1609,  # 数据制度
    'C': 0.1920,  # 数据行为
    'D': 0.1549,  # 数据资产
    'E': 0.1400   # 数据技术
}

# 二级指标权重（在各自一级指标内的权重）
SECONDARY_WEIGHTS = {
    # A 数据素养
    'A1': 0.5716,  # 教师数据素养
    'A2': 0.4284,  # 学生数据素养

    # B 数据制度
    'B1': 0.3599,
    'B2': 0.4131,
    'B3': 0.2270,

    # C 数据行为
    'C1': 0.4679,
    'C2': 0.5321,

    # D 数据资产
    'D1': 0.4795,
    'D2': 0.5205,

    # E 数据技术
    'E1': 0.5440,
    'E2': 0.4551,
}

# 观测点权重（在各自二级指标内的权重）
OBSERVATION_WEIGHTS = {
    # A1 教师数据素养
    'A11': 0.2184,
    'A12': 0.2060,
    'A13': 0.1503,
    'A14': 0.2532,
    'A15': 0.1721,

    # A2 学生数据素养
    'A31': 0.1907,
    'A32': 0.2176,
    'A33': 0.1910,
    'A34': 0.2340,
    'A35': 0.1666,

    # B1 数据组织机构
    'B11': 0.4757,  # 数据领导/工作小组
    'B12': 0.5243,  # 数据组织运行情况

    # B2 数据人员配备
    'B21': 0.5833,  # 数据专职/兼职管理人员
    'B22': 0.4167,  # 数据人员进修与培训情况

    # B3 数据管理文件
    'B31': 0.5347,  # 数据管理制度类文件
    'B32': 0.4653,  # 数据实践指导类文件

    # C1 数据行为监测
    'C11': 0.5091,  # 教师数据行为
    'C12': 0.4909,  # 学生数据行为

    # C2 数据应用成效
    'C21': 0.4058,  # 数据应用特色成果
    'C22': 0.3641,  # 数据应用社会影响
    'C23': 0.2300,  # 应用效果主观评价

    # D1 数据资产意识
    'D11': 0.2913,  # 数据资产价值意识
    'D12': 0.4479,  # 数据资产应用意识
    'D13': 0.2608,  # 数据资产治理意识

    # D2 数据资产积累
    'D21': 0.3958,  # 数据资产总量
    'D22': 0.6042,  # 人均数据资产量

    # E1 数据基础设施
    'E11': 0.4792,  # 数据硬件设施
    'E12': 0.5208,  # 数据系统平台

    # E2 数据安保水平
    'E21': 0.6597,  # 数据安全合规与认证
    'E22': 0.3403   # 数据风险事件记录
}

# 总分满分（5分制）
TOTAL_MAX_SCORE = 5.0


# ==================== 等级划分（5分制） ====================

# 成熟度等级划分（基于5分制总分）
MATURITY_LEVELS = list(reversed(SHARED_MATURITY_LEVELS))

# 等级对应百分制（用于报告展示）
MATURITY_LEVEL_PERCENT = {
    'leading': {'min': 80, 'max': 100, 'name': '创新级'},
    'mature': {'min': 60, 'max': 80, 'name': '成熟级'},
    'growing': {'min': 30, 'max': 60, 'name': '成长级'},
    'initial': {'min': 0, 'max': 30, 'name': '初始级'}
}


# ==================== DeepSeek API 配置 ====================

DEEPSEEK_CONFIG = {
    'api_base': 'https://api.deepseek.com/v1',
    'model': 'deepseek-chat',
    'temperature': 0.7,
    'max_tokens': 500
}
