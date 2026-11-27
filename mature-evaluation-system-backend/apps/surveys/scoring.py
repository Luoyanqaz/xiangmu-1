"""
问卷计分逻辑
"""
from decimal import Decimal
from .models import SurveyInstance, SurveyResponse
from .quality import scored_responses


class SurveyScoring:
    """问卷计分类"""
    
    # 教师问卷维度配置（A11-A15）
    TEACHER_DIMENSIONS = {
        'A11': {'name': '数据意识与思维', 'question_range': range(6, 14), 'max_score': 40},  # 题6-13（8题）
        'A12': {'name': '数据知识与技能', 'question_range': range(14, 21), 'max_score': 35},  # 题14-20（7题）
        'A13': {'name': '数据评价与交流', 'question_range': range(21, 24), 'max_score': 15},  # 题21-23（3题）
        'A14': {'name': '数据应用与创新', 'question_range': range(24, 32), 'max_score': 40},  # 题24-31（8题）
        'A15': {'name': '数据伦理与隐私', 'question_range': range(32, 35), 'max_score': 15},  # 题32-34（3题）
    }
    
    # 学生问卷维度配置（A31-A35）
    STUDENT_DIMENSIONS = {
        'A31': {'name': '数据意识与思维', 'question_range': range(4, 11), 'max_score': 35},  # 题4-10（7题）
        'A32': {'name': '数据知识与技能', 'question_range': range(11, 18), 'max_score': 35},  # 题11-17（7题）
        'A33': {'name': '数据评价与交流', 'question_range': range(18, 20), 'max_score': 10},  # 题18-19（2题）
        'A34': {'name': '数据应用与创新', 'question_range': range(20, 26), 'max_score': 30},  # 题20-25（6题）
        'A35': {'name': '数据伦理与隐私', 'question_range': range(26, 29), 'max_score': 15},  # 题26-28（3题）
    }

    
    @classmethod
    def get_dimensions_config(cls, survey_type):
        """根据问卷类型获取维度配置"""
        if survey_type == 'teacher':
            return cls.TEACHER_DIMENSIONS
        elif survey_type == 'student':
            return cls.STUDENT_DIMENSIONS
        else:
            raise ValueError(f"未知的问卷类型: {survey_type}")
    
    @classmethod
    def calculate_response_score(cls, response):
        """计算单份问卷回答的得分"""
        instance = response.instance
        survey_type = instance.template.survey_type
        dimensions_config = cls.get_dimensions_config(survey_type)
        
        answers = response.answers
        dimension_scores = {}
        
        # 计算每个维度的得分
        for dimension_code, config in dimensions_config.items():
            dimension_score = 0
            question_count = 0
            
            # 遍历该维度的题目
            for question_order in config['question_range']:
                question_key = f"q{question_order}"
                if question_key in answers:
                    answer = answers[question_key]
                    # 5点量表：非常符合=5, 符合=4, 一般=3, 不符合=2, 非常不符合=1
                    score = cls._get_answer_score(answer)
                    dimension_score += score
                    question_count += 1
            
            # 计算标准化得分（0-1之间）
            max_score = config['max_score']
            normalized_score = Decimal(dimension_score) / Decimal(max_score) if max_score > 0 else Decimal(0)
            
            dimension_scores[dimension_code] = {
                'raw_score': dimension_score,
                'max_score': max_score,
                'normalized_score': float(normalized_score),
                'question_count': question_count
            }
        
        return dimension_scores
    
    @classmethod
    def _get_answer_score(cls, answer):
        """根据答案获取分数"""
        # 5点量表映射
        score_mapping = {
            '非常符合': 5,
            '符合': 4,
            '一般': 3,
            '不符合': 2,
            '非常不符合': 1,
            # 英文选项（备用）
            'E': 5,
            'D': 4,
            'C': 3,
            'B': 2,
            'A': 1,
        }
        
        return score_mapping.get(answer, 0)
    
    @classmethod
    def calculate_instance_average_score(cls, instance):
        """计算问卷实例的平均得分（所有回答的平均值）"""
        responses = scored_responses(instance, instance.assessment)
        
        if not responses.exists():
            return None
        
        survey_type = instance.template.survey_type
        dimensions_config = cls.get_dimensions_config(survey_type)
        
        # 初始化维度累计得分
        dimension_totals = {code: {'raw_score': 0, 'normalized_score': 0} for code in dimensions_config.keys()}
        response_count = responses.count()
        
        # 累加所有回答的得分
        for response in responses:
            response_scores = cls.calculate_response_score(response)
            for dimension_code, scores in response_scores.items():
                dimension_totals[dimension_code]['raw_score'] += scores['raw_score']
                dimension_totals[dimension_code]['normalized_score'] += scores['normalized_score']
        
        # 计算平均值
        dimension_averages = {}
        for dimension_code, totals in dimension_totals.items():
            dimension_averages[dimension_code] = {
                'average_raw_score': totals['raw_score'] / response_count,
                'average_normalized_score': totals['normalized_score'] / response_count,
                'max_score': dimensions_config[dimension_code]['max_score'],
                'response_count': response_count
            }
        
        return dimension_averages

    @classmethod
    def calculate_assessment_literacy_score(cls, assessment):
        """
        计算评估的数据素养总分
        新版仅综合教师问卷和学生问卷。
        """
        # 获取教师、学生问卷实例
        teacher_instance = assessment.survey_instances.filter(
            template__survey_type='teacher'
        ).first()

        student_instance = assessment.survey_instances.filter(
            template__survey_type='student'
        ).first()

        # 计算各问卷的平均得分
        teacher_scores = cls.calculate_instance_average_score(teacher_instance) if teacher_instance else None
        student_scores = cls.calculate_instance_average_score(student_instance) if student_instance else None

        # 如果两份问卷都没有数据，返回 None
        if not any([teacher_scores, student_scores]):
            return None

        total_normalized_score = 0
        valid_survey_count = 0

        if teacher_scores:
            teacher_avg = sum(
                dim['average_normalized_score']
                for dim in teacher_scores.values()
            ) / len(teacher_scores)

            total_normalized_score += teacher_avg
            valid_survey_count += 1

        if student_scores:
            student_avg = sum(
                dim['average_normalized_score']
                for dim in student_scores.values()
            ) / len(student_scores)

            total_normalized_score += student_avg
            valid_survey_count += 1

        final_normalized_score = (
            total_normalized_score / valid_survey_count
            if valid_survey_count > 0
            else 0
        )

        literacy_score = Decimal(final_normalized_score) * Decimal(20)

        return {
            'literacy_score': float(literacy_score),
            'normalized_score': final_normalized_score,
            'teacher_scores': teacher_scores,
            'student_scores': student_scores,
            'valid_survey_count': valid_survey_count
        }
