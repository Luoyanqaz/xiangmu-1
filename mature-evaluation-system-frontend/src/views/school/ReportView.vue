<template>
  <div class="report-container" ref="reportContainer">
    <!-- 顶部操作栏 -->
    <div class="report-header no-print">
      <div class="header-left">
        <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1>评估报告</h1>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="downloadPDF" :loading="downloading" :icon="Download">
          {{ downloading ? '生成中...' : '下载PDF' }}
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>正在加载报告数据...</p>
    </div>

    <!-- 报告内容 -->
    <div v-else-if="reportData && reportData.school_name" class="report-content" ref="reportContent">
      <!-- 报告封面/标题 -->
      <div class="report-title-section">
        <h1 class="main-title" style="font-weight: bold !important;">{{ reportData.school_name }}数据文化成熟度评估报告</h1>
        <p class="report-date">报告生成时间：{{ formatDate(reportData.report_date) }}</p>
      </div>

      <!-- 新增：学校基础信息展示区 -->
      <div class="school-basic-card">
        <div class="basic-info-grid">
          <div class="grid-item">
            <span class="grid-label">办学类型</span>
            <span class="grid-value">{{ schoolTypeLabel(reportData.school_type) }}</span>
          </div>
          <div class="grid-item">
            <span class="grid-label">所属地区</span>
            <span class="grid-value">{{ reportData.area_display || '未填写' }}</span>
          </div>
          <div class="grid-item">
            <span class="grid-label">建校年份</span>
            <span class="grid-value">{{ reportData.founding_year ? reportData.founding_year + '年' : '未填写' }}</span>
          </div>
          <div class="grid-item">
            <span class="grid-label">教职工人数</span>
            <span class="grid-value">{{ reportData.teacher_count ? reportData.teacher_count + '人' : '未填写' }}</span>
          </div>
          <div class="grid-item">
            <span class="grid-label">学生人数</span>
            <span class="grid-value">{{ reportData.student_count ? reportData.student_count + '人' : '未填写' }}</span>
          </div>
        </div>
      </div>
      <!-- 报告说明 -->
      <div class="report-intro">
        <p style="text-indent: 2em;">本报告旨在帮助您全面了解学校数据文化建设情况。数据文化是指学校在数据使用和管理方面的制度、规范、实践和价值观的集合；而数据文化成熟度则是学校在数据使用、管理和价值实现方面的成熟程度。平台基于学校填报的多维度数据，通过科学的评估规则，并辅助于DeepSeek大模型进行智能评估，准确识别学校数据文化的建设水平与现实问题，以促进学校数据使用、管理和价值实现，推动学校数据治理能力的提升。本报告包括以下五个核心分析维度：</p>
        <!-- padding-left: 0 确保列表整体不左偏 -->
        <!-- padding-left: 0 确保列表整体不左偏 -->
          <ol style="padding-left: 0; list-style: none;">
            <li style="text-indent: 2em; margin-bottom: 10px; line-height: 1.6; text-align: justify;">
              1. <strong>数据素养</strong>：评估学校教师和学生在数据应用方面的综合能力，包括数据意识与思维、数据知识与技能、数据伦理与隐私等，为数据文化的落地提供核心人才支撑。
            </li>
            <li style="text-indent: 2em; margin-bottom: 10px; line-height: 1.6; text-align: justify;">
              2. <strong>数据制度</strong>：评估学校在组织架构、人员配备与管理规范方面的制度化水平，包括数据组织机构、数据人员配备、数据管理文件等，为学校数据文化的有序发展提供制度依据。
            </li>
            <li style="text-indent: 2em; margin-bottom: 10px; line-height: 1.6; text-align: justify;">
              3. <strong>数据行为</strong>：评估数据在工作、学习与决策中的实际应用情况，包括学生数据行为、教师数据行为、数据应用成效等。
            </li>
            <li style="text-indent: 2em; margin-bottom: 10px; line-height: 1.6; text-align: justify;">
              4. <strong>数据资产</strong>：评估学校对数据资源的认知水平、积累规模等内容，包括数据资产意识、数据资产总量等。
            </li>
            <li style="text-indent: 2em; margin-bottom: 10px; line-height: 1.6; text-align: justify;">
              5. <strong>数据技术</strong>：评估学校在数据采集、存储、处理与安全保障方面的技术支撑能力，包括数据硬件设施、数据系统平台、数据安全合规与认证等，为数据文化提供可靠的底层支撑。
            </li>
          </ol>
      </div>

      <!-- 第一部分：学校数据文化评估概况 -->
      <section class="report-section">
        <h2 class="section-title" style="display: flex; justify-content: center; align-items: center; gap: 10px; text-align: center;">
          <el-icon><DataAnalysis /></el-icon>
          <span>学校数据文化评估概况</span>
        </h2>
        
        <p class="section-summary">
          经综合评估，学校数据文化成熟度总得分为{{ reportData.total_score?.toFixed(2) }}分，整体发展水平为{{ reportData.maturity_level }}。从五大维度来看，数据素养维度得分{{ dimensionScores.literacy?.toFixed(2) }}分，数据制度维度得分{{ dimensionScores.institution?.toFixed(2) }}分，数据行为维度得分{{ dimensionScores.behavior?.toFixed(2) }}分，数据资产维度得分{{ dimensionScores.asset?.toFixed(2) }}分，数据技术维度得分{{ dimensionScores.technology?.toFixed(2) }}分。
        </p>

        <!-- 总分和等级展示 -->
        <div class="overview-scores">
          <div class="score-card total">
            <span class="label">学校数据文化得分:{{ reportData.total_score?.toFixed(2) }}</span>
          </div>
          <div class="score-card level">
            <span class="label">学校数据文化等级:{{ reportData.maturity_level }}</span>
          </div>
        </div>

        <!-- 概况图表区域 -->
        <div class="overview-chart-container">
          <div class="overview-left">
            <div class="dimension-list">
              <div class="dimension-header">
                <span class="total-score-badge">评分维度</span>
                <span class="level-badge">得分</span>
              </div>
              <div class="dimension-item" v-for="(item, key) in dimensionList" :key="key">
                <span class="dim-name">{{ item.name }}</span>
                <span class="dim-score">{{ item.score?.toFixed(2) }}分</span>
              </div>
            </div>
          </div>
          <div class="overview-right">
            <div ref="overviewChart" class="chart-box" style="height: 350px;"></div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <p style="text-indent: 2em;"><strong>评估建议：</strong>{{ reportData.suggestions?.overall || '暂无建议' }}</p>
        </div>

        <div class="evaluation-note">
          <p style="text-indent: 2em;"><strong style="font-weight: bold; color: #909399;">评估说明：</strong>中小学校数据文化成熟度得分，由各观测点分值经标准化与分层加权计算得出，最终得分区间为 0 至 5 分。结合得分可判定学校数据文化所处等级：初始级（0≤得分＜1.5 分）、成长级（1.5≤得分＜3.0 分）、成熟级（3.0≤得分＜4.0 分）、创新级（4.0≤得分≤5.0 分）</p>
        </div>
      </section>

      <!-- 第二部分：学校数据素养分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Reading /></el-icon>
          学校数据素养分析
        </h2>

        <!-- 计分规则说明 -->
        <p class="section-summary">
          学校数据素养得分为{{ dimensionScores.literacy?.toFixed(2) }}分。
          其中，教师数据素养得分为{{ secondaryScores.A1?.toFixed(2) }}分，
          学生数据素养得分为{{ secondaryScores.A2?.toFixed(2) }}分。
          具体情况如下：
        </p>

        <!-- 三个群体得分展示 -->
        <!-- 两个群体得分展示 -->
        <div class="literacy-scores two-columns">
          <div class="literacy-score-card teacher">
            <span class="score">{{ secondaryScores.A1?.toFixed(2) }}分</span>
            <span class="label">教师平均分</span>
          </div>
          <div class="literacy-score-card student">
            <span class="score">{{ secondaryScores.A2?.toFixed(2) }}分</span>
            <span class="label">学生平均分</span>
          </div>
        </div>

        <!-- 参评人数 -->
        <div class="participant-info">
          <span>教师参评人数：{{ reportData.participant_counts?.teacher || 0 }}人</span>
          <span>学生参评人数：{{ reportData.participant_counts?.student || 0 }}人</span>
        </div>

        <!-- 三个雷达图 -->
        <!-- 两个雷达图 -->
        <div class="literacy-radar-section">
          <h4>教师与学生数据素养雷达图</h4>
          <div class="radar-charts-row two-columns">
            <div class="radar-chart-item">
              <div ref="teacherRadarChart" class="chart-box" style="height: 280px;"></div>
            </div>
            <div class="radar-chart-item">
              <div ref="studentRadarChart" class="chart-box" style="height: 280px;"></div>
            </div>
          </div>
        </div>

        <!-- 综合对比柱状图 -->
        <div class="literacy-comparison-section">
          <h4>数据素养综合对比</h4>
          <div ref="literacyComparisonChart" class="chart-box" style="height: 350px;"></div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <p style="text-indent: 2em;"><strong>评估建议：</strong>{{ reportData.suggestions?.literacy || '暂无建议' }}</p>
        </div>

        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据素养维度下设两个二级指标：</p>
          <ul>
            <li>
              <strong>A1 教师数据素养</strong>：<br/>
              包含A11教师数据意识与思维、A12教师数据知识与技能、A13教师数据评价与交流、A14教师数据应用与创新、A15教师数据伦理与隐私等5个观测点，基于教师问卷中的《数据素养自我评价量表》，由教师对各题项的认同程度综合计分。
            </li>
            <li>
              <strong>A2 学生数据素养</strong>：<br/>
              包含A21学生数据意识与思维、A22学生数据知识与技能、A23学生数据评价与交流、A24学生数据应用与创新、A25学生数据伦理与隐私等5个观测点，基于学生问卷中的《数据素养自我评价量表》，由学生对各题项的认同程度综合计分。
            </li>
          </ul>
          <p class="rule-note">
            注：教师问卷和学生问卷均采用5点量表计分。计分完成后，对每个观测点分值进行归一化处理，转化为相同分值区间后参与加权计算。
          </p>
        </div>
      </section>

      <!-- 第三部分：学校数据制度分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Document /></el-icon>
          学校数据制度分析
        </h2>

        <!-- 计分规则说明 -->

        <p class="section-summary">
          学校数据制度得分为{{ formatScore(dimensionScores.institution) }}。
          其中，数据组织机构得分{{ formatScore(secondaryScores.B1) }}，
          数据人员配备得分{{ formatScore(secondaryScores.B2) }}，
          数据管理文件得分{{ formatScore(secondaryScores.B3) }}。
          具体情况如下：
        </p>

        <!-- 数据组织机构 -->
        <!-- 数据组织机构 -->
        <div class="institution-card">
          <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
            <span class="card-title">数据组织机构：{{ secondaryScores.B1?.toFixed(2) }}分</span>
          </div>

          <div class="card-content institution-grid">
            <div class="info-item">
              <span class="info-label">数据领导/工作小组</span>
              <div class="info-value">
                <p>学校数据领导/工作小组设置情况为：{{ getLeadershipGroupText() }}。</p>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">数据组织运行情况</span>
              <div class="info-value">
                <p>近3年，学校组织开展数据相关会议、活动{{ institutionDetails.meeting_activity_count || 0 }}次。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据人员配备 -->
        <!-- 数据人员配备 -->
        <div class="institution-card">
          <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
            <span class="card-title">数据人员配备：{{ secondaryScores.B2?.toFixed(2) }}分</span>
          </div>

          <div class="card-content institution-grid">
            <div class="info-item">
              <span class="info-label">数据专职/兼职管理人员</span>
              <div class="info-value">
                <template v-if="institutionDetails.has_data_staff">
                  <p>1. 学校配备专职数据管理人员{{ institutionDetails.fulltime_staff_count || 0 }}位，兼职数据管理人员{{ institutionDetails.parttime_staff_count || 0 }}位。</p>
                  <p>2. 相关人员{{ institutionDetails.has_clear_responsibilities ? '已有明确职责分工' : '暂未形成明确职责分工' }}。</p>
                </template>
                <template v-else>
                  <p>学校暂未配备专职或兼职数据管理人员。</p>
                </template>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">数据人员进修与培训情况</span>
              <div class="info-value">
                <template v-if="institutionDetails.has_training">
                  <p>1. 学校近3年组织或参与数据相关进修、培训{{ institutionDetails.training_count || 0 }}次。</p>
                  <p>2. 相关人员获得数据相关认证或考核证书{{ getTotalCertificates() }}份。</p>
                </template>
                <template v-else>
                  <p>学校近5年暂无数据相关进修或培训记录。</p>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据管理文件 -->
        <!-- 数据管理文件 -->
        <div class="institution-card">
          <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
            <span class="card-title">数据管理文件：{{ secondaryScores.B3?.toFixed(2) }}分</span>
          </div>

          <div class="card-content institution-grid">
            <div class="info-item">
              <span class="info-label">数据管理制度类文件</span>
              <div class="info-value">
                <p>1. {{ getManagementDocStatusText() }}</p>

                <template v-if="institutionDetails.management_doc_status === 'clear_required'">
                  <p>2. 学校出台的与数据管理相关文件共{{ getTotalManagementDocs() }}份。</p>

                  <div v-if="institutionDetails.management_doc_analysis" class="llm-analysis">
                    <p>3. 大模型文件质量分析：</p>
                    <div class="analysis-content">{{ institutionDetails.management_doc_analysis }}</div>
                  </div>
                </template>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">数据实践指导类文件</span>
              <div class="info-value">
                <p>1. {{ getPracticeDocStatusText() }}</p>

                <template v-if="institutionDetails.practice_doc_status === 'published'">
                  <p>2. 学校出台的与数据实践指导相关文件共{{ getTotalPracticeDocs() }}份。</p>

                  <div v-if="institutionDetails.practice_doc_analysis" class="llm-analysis">
                    <p>3. 大模型文件质量分析：</p>
                    <div class="analysis-content">{{ institutionDetails.practice_doc_analysis }}</div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <p style="text-indent: 2em;"><strong>评估建议：</strong>{{ reportData.suggestions?.institution || '暂无建议' }}</p>
        </div>

        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据制度维度下设三个二级指标：</p>
          <ul>
            <li>
              <strong>B1 数据组织机构</strong>：
              <ul>
                <li>B11 数据领导/工作小组：根据学校数据领导/工作小组设立情况计分</li>
                <li>B12 数据组织运行情况：根据学校近3年数据相关会议或活动开展次数计分。</li>
              </ul>
            </li>

            <li>
              <strong>B2 数据人员配备</strong>：
              <ul>
                <li>B21 数据专职/兼职管理人员：根据学校是否配备数据管理人员、专职/兼职人员数量、职责明确情况综合计分。</li>
                <li>B22 数据人员进修与培训情况：根据数据相关人员是否参与数据相关培训或进修、参与培训或进修次数、获得相关认证或考核证书数量综合计分。</li>
              </ul>
            </li>

            <li>
              <strong>B3 数据管理文件</strong>：
              <ul>
                <li>
                  B31 数据管理制度类文件：根据学校是否在相关制度或规范文件中作出明确要求、出台与数据管理相关文件数量、大模型分析文件质量结果综合计分。
                </li>
                <li>
                  B32 数据实践指导类文件：根据学校是否发布数据应用指南、操作说明或工作手册、出台与数据实践指导相关文件数量、大模型分析文件质量结果综合计分。
                </li>
              </ul>
            </li>
          </ul>

          <p class="rule-note">
            注：观测点计分完成后，对每个观测点分值进行归一化处理，转化为相同分值区间后参与加权计算。
          </p>
        </div>
      </section>

      <!-- 第四部分：学校数据行为分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><TrendCharts /></el-icon>
          学校数据行为分析
        </h2>

        <!-- 计分规则说明 -->


        <p class="section-summary">
          学校数据行为得分为{{ formatScore(dimensionScores.behavior) }}。
          其中，数据行为监测得分{{ formatScore(secondaryScores.C1) }}，
          数据应用成效得分{{ formatScore(secondaryScores.C2) }}。
          具体情况如下：
        </p>

        <!-- 数据行为监测 -->
        <!-- 数据行为监测 -->
        <div class="behavior-card">
          <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
            <span class="card-title">数据行为监测：{{ formatScore(secondaryScores.C1) }}</span>
          </div>

          <div class="card-content">
            <div class="behavior-monitor-grid">
              <div class="info-item">
                <span class="info-label">教师数据行为</span>
                <div class="info-value">
                  <p>1. 教师每周使用数字化设备开展教学的人均频次为{{ behaviorDetails.teacher_device_use_freq ?? 0 }}次。</p>
                  <p>2. 教师每周使用数据相关平台的人均频次为{{ behaviorDetails.teacher_platform_use_freq ?? 0 }}次。</p>
                  <p>3. 教师常态化开展的数据行为共{{ getTeacherBehaviorCount() }}项。</p>
                </div>
              </div>

              <div class="info-item">
                <span class="info-label">学生数据行为</span>
                <div class="info-value">
                  <p>1. 学生数字化学习设备配备情况为：{{ getStudentDeviceProvisionText() }}。</p>
                  <p>2. 学生平台账号开通情况为：{{ getStudentAccountStatusText() }}。</p>
                  <p>3. 学生日常学习生活中常态化实现的数据行为共{{ getStudentBehaviorCount() }}项。</p>
                </div>
              </div>
            </div>

            <div ref="behaviorBarChart" class="chart-box behavior-chart" style="height: 280px;"></div>
          </div>
        </div>

        <!-- 数据应用成效 -->
        <div class="behavior-card behavior-effect-card">
          <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
            <span class="card-title">数据应用成效：{{ formatScore(secondaryScores.C2) }}</span>
          </div>

          <div class="card-content behavior-effect-content">
            <div class="effect-left">
              <div class="effect-info-card">
                <div class="effect-icon">
                  <el-icon><Trophy /></el-icon>
                </div>
                <div class="effect-text">
                  <h4>数据应用特色成果</h4>
                  <p>
                    学校公开发表数据相关论文{{ behaviorDetails.published_paper_count || 0 }}篇，
                    出版相关著作{{ behaviorDetails.published_book_count || 0 }}部，
                    入选典型案例{{ getTotalCases() }}个，
                    获得数据应用相关奖励或荣誉{{ getTotalAwards() }}个。
                  </p>
                </div>
              </div>

              <div class="effect-divider"></div>

              <div class="effect-info-card">
                <div class="effect-icon">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <div class="effect-text">
                  <h4>数据应用社会影响</h4>
                  <p>
                    学校获得媒体宣传报道{{ getTotalMedia() }}次，
                    参与数据应用相关经验交流{{ getTotalConference() }}次，
                    通过公众号发布相关经验分享或创新实践{{ behaviorDetails.public_account_post_count || 0 }}次，
                    接待其他学校参观学习{{ behaviorDetails.visit_count || 0 }}次。
                  </p>
                </div>
              </div>
            </div>

            <div class="effect-right">
              <div class="effect-title-row">
                <div class="effect-icon">
                  <el-icon><StarFilled /></el-icon>
                </div>
                <h4>教师对数据应用效果的主观评价</h4>
              </div>

              <p class="effect-desc" style="text-indent: 2em;">
                &nbsp;&nbsp;该指标来自教师问卷中的数据应用效果评价题项。
              </p>

              <div class="effect-circle-wrap">
                <div ref="teacherEffectCircle" class="circle-chart effect-circle-chart"></div>
              </div>

              <div class="effect-participant">
                教师参评人数：{{ reportData.participant_counts?.teacher || 0 }}人
              </div>
            </div>
          </div>
</div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <p style="text-indent: 2em;"><strong>评估建议：</strong>{{ reportData.suggestions?.behavior || '暂无建议' }}</p>
        </div>

        <div class="scoring-rules">
        <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
        <p>数据行为维度下设两个二级指标：</p>
        <ul>
          <li>
            <strong>C1 数据行为监测</strong>：
            <ul>
              <li>
                C11 教师数据行为：由教师数字化设备使用频次、教师数据相关平台使用频次、教师常态化数据行为数量综合计分。
              </li>
              <li>
                C12 学生数据行为：由学生数字化学习设备配备情况、学生平台账号开通情况、学生常态化数据行为数量综合计分。
              </li>
            </ul>
          </li>

          <li>
            <strong>C2 数据应用成效</strong>：
            <ul>
              <li>C21 数据应用特色成果：包含论文、著作、典型案例、荣誉奖励等，按数量及级别计分。</li>
              <li>C22 数据应用社会影响：包含媒体报道、会议交流、公众号发布、参观学习等，按次数及级别计分。</li>
              <li>C23 应用效果主观评价：基于教师问卷，评估教师对学校数据应用效果的主观评价。</li>
            </ul>
          </li>
        </ul>
        <p class="rule-note">
          注：观测点计分完成后，对每个观测点分值进行归一化处理，转化为相同分值区间后参与加权计算。
        </p>
      </div>
      </section>

      <!-- 第五部分：学校数据资产分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Files /></el-icon>
          学校数据资产分析
        </h2>
        <p class="section-summary">
          学校数据资产得分为{{ formatScore(dimensionScores.asset) }}。
          其中，数据资产意识得分{{ formatScore(secondaryScores.D1) }}，
          数据资产积累得分{{ formatScore(secondaryScores.D2) }}。
          具体情况如下：
        </p>

        <!-- 数据资产意识 -->
        <div class="asset-card">
          <div class="card-header asset-card-header">
            <span class="card-title">数据资产意识：{{ formatScore(secondaryScores.D1) }}</span>

            <span class="card-subtitle">
              教师参评人数：{{ reportData.participant_counts?.teacher || 0 }}人
            </span>
          </div>

          <div class="card-content">
            <p class="asset-desc">
              数据资产意识指标来自教师问卷中的数据资产意识评价题项，主要反映教师对数据资产价值、应用和治理的认知水平。
            </p>

            <div ref="assetAwarenessRadar" class="chart-box asset-awareness-chart" style="height: 320px;"></div>
          </div>
        </div>

        <!-- 数据资产积累 -->
        <!-- 数据资产积累 -->
        <div class="asset-card">
        <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
          <span class="card-title">数据资产积累：{{ formatScore(secondaryScores.D2) }}</span>
        </div>

        <div class="card-content">
          <div class="asset-status-grid">
            <div class="info-item">
              <span class="info-label">数据资产统筹管理情况</span>
              <div class="info-value">
                <p>学校{{ assetDetails.has_unified_data_management ? '已对校内数据资产进行统一管理或统筹管理' : '暂未对校内数据资产进行统一管理或统筹管理' }}。</p>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">数据资源统计查询情况</span>
              <div class="info-value">
                <p>
                  <template v-if="assetDetails.has_unified_data_management === false">
                    由于学校暂未对校内数据资产进行统一管理，本报告不再展开统计各类数据资源总量。
                  </template>
                  <template v-else>
                    学校{{ assetDetails.can_query_data_assets ? '能够通过相关平台或系统对校内主要数据资源进行统计查询' : '暂不能通过相关平台或系统对校内主要数据资源进行统计查询' }}。
                  </template>
                </p>
              </div>
            </div>
          </div>

          <template v-if="assetDetails.has_unified_data_management && assetDetails.can_query_data_assets">
            <div class="asset-volume-table">
              <div class="asset-volume-row header">
                <span>数据类型</span>
                <span>统计方式</span>
                <span>数据量</span>
              </div>

              <div class="asset-volume-row">
                <span>教育教学数据</span>
                <span>{{ getDataStatMethodText(assetDetails.teaching_data_stat_method) }}</span>
                <span>{{ formatDataVolume(assetDetails.teaching_data_volume) }}</span>
              </div>

              <div class="asset-volume-row">
                <span>师生管理数据</span>
                <span>{{ getDataStatMethodText(assetDetails.teacher_student_data_stat_method) }}</span>
                <span>{{ formatDataVolume(assetDetails.teacher_student_data_volume) }}</span>
              </div>

              <div class="asset-volume-row">
                <span>数字资源数据</span>
                <span>{{ getDataStatMethodText(assetDetails.digital_resource_data_stat_method) }}</span>
                <span>{{ formatDataVolume(assetDetails.digital_resource_data_volume) }}</span>
              </div>

              <div class="asset-volume-row">
                <span>校园管理与行政数据</span>
                <span>{{ getDataStatMethodText(assetDetails.campus_admin_data_stat_method) }}</span>
                <span>{{ formatDataVolume(assetDetails.campus_admin_data_volume) }}</span>
              </div>

              <div class="asset-volume-row">
                <span>其他类型数据</span>
                <span>补充统计</span>
                <span>{{ formatDataVolume(assetDetails.other_type_data_volume) }}</span>
              </div>
            </div>
          </template>

          <div class="asset-progress-section">
            <div class="progress-card">
              <div class="progress-header">
                <span class="progress-title">数据资产总量</span>
              </div>
              <div class="progress-value">{{ formatDataVolume(getTotalDataVolume()) }}</div>
              <div class="progress-label">教育教学、师生管理、数字资源、校园管理与行政及其他数据总量</div>
              <el-progress
                :percentage="getVolumePercentage(getTotalDataVolume(), 9000)"
                :stroke-width="12"
                :show-text="false"
                color="#67c23a"
              />
              <div class="progress-range">
                <span>0 GB</span>
                <span>9000 GB</span>
              </div>
            </div>

            <div class="progress-card">
              <div class="progress-header">
                <span class="progress-title">人均数据资产量</span>
              </div>
              <div class="progress-value red">{{ getPerCapitaVolume() }} GB</div>
              <div class="progress-label">按学校教师人数和学生人数平均计算</div>
              <el-progress
                :percentage="getVolumePercentage(Number(getPerCapitaVolume()), 40)"
                :stroke-width="12"
                :show-text="false"
                color="#f56c6c"
              />
              <div class="progress-range">
                <span>0 GB</span>
                <span>40 GB</span>
              </div>
            </div>
          </div>
        </div>
      </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <p style="text-indent: 2em;"><strong>评估建议：</strong>{{ reportData.suggestions?.asset || '暂无建议' }}</p>
        </div>

        <!-- 计分规则说明 -->
        <div class="scoring-rules">
        <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
        <p>数据资产维度下设两个二级指标：</p>

        <ul>
          <li>
            <strong>D1 数据资产意识</strong>：<br/>
            包含D11数据资产价值意识、D12数据资产应用意识、D13数据资产治理意识等3个观测点，基于教师问卷中的《数据资产意识调查量表》，由教师对各题项的认同程度综合计分。
          </li>

          <li>
            <strong>D2 数据资产积累</strong>：
            <ul>
              <li>
                D21 数据资产总量：根据学校数据资产统一管理情况、数据资产累积总量综合计分。若学校无法统计数据资产总量，为避免影响测评结果，此次测评将在此项赋予学校一个基准分值。
              </li>
              <li>
                D22 人均数据资产量：根据学校数据资产总量与师生总人数之比计分。
              </li>
            </ul>
          </li>
        </ul>

        <p class="rule-note">
          注：观测点计分完成后，对每个观测点分值进行归一化处理，转化为相同分值区间后参与加权计算。
        </p>
      </div>
      </section>

      <!-- 第六部分：学校数据技术分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Setting /></el-icon>
          学校数据技术分析
        </h2>

        

        <p class="section-summary">
          学校数据技术得分为{{ formatScore(dimensionScores.technology) }}。
          其中，数据基础设施得分{{ formatScore(secondaryScores.E1) }}，
          数据安全水平得分{{ formatScore(secondaryScores.E2) }}。
          具体情况如下：
        </p>

        <!-- 数据基础设施 -->
        <!-- 数据基础设施 -->
        <div class="tech-card">
          <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
            <span class="card-title">数据基础设施：{{ formatScore(secondaryScores.E1) }}</span>
          </div>

          <div class="card-content technology-grid">
            <div class="info-item">
              <span class="info-label">数据硬件设施</span>
              <div class="info-value">
                <p>1. {{ getDataCenterText() }}。</p>
                <p>
                  2. 数字终端配备生机比为：{{ getStudentRatioText() }}；
                  师机比为：{{ getTeacherRatioText() }}。
                </p>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">数据系统平台</span>
              <div class="info-value">
                <p>
                  学校{{ technologyDetails.has_data_platform ? '已建设' : '暂未建设' }}数据治理平台，
                  用于数据集中归集、统一管理或共享调用。
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据安保水平 -->
        <!-- 数据安全水平 -->
        <div class="tech-card">
          <div class="card-header" style="display: flex; justify-content: center; align-items: center;">
            <span class="card-title">数据安全水平：{{ formatScore(secondaryScores.E2) }}</span>
          </div>

          <div class="card-content technology-grid">
            <div class="info-item">
              <span class="info-label">数据安全合规与认证</span>
              <div class="info-value">
                <p>1. 学校平台建设管理模式为：{{ getPlatformBuildModeText() }}。</p>

                <template v-if="technologyDetails.platform_build_mode === 'self_built' || technologyDetails.platform_build_mode === 'mixed'">
                  <p>2. 学校{{ technologyDetails.security_certified_count || 0 }}类平台通过网络安全等级保护测评。</p>
                  <p>3. 学校部署的各类平台通过网络安全等级保护测评的比例为：{{ getSecurityRatioText() }}。</p>
                </template>

                <template v-else-if="technologyDetails.platform_build_mode === 'external'">
                  <p>2. 学校完全接入外部平台，系统根据计分规则对数据安全合规与认证情况进行赋分。</p>
                </template>

                <template v-else>
                  <p>2. 学校平台建设管理模式暂未填写。</p>
                </template>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">数据风险事件记录</span>
              <div class="info-value">
                <p>
                  2023年至2025年，学校{{ technologyDetails.has_security_incident ? '发生过' : '未发生' }}数据风险事件。
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <p style="text-indent: 2em;"><strong>评估建议：</strong>{{ reportData.suggestions?.technology || '暂无建议' }}</p>
        </div>

        <!-- 计分规则说明 -->
        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据技术维度下设两个二级指标：</p>

          <ul>
            <li>
              <strong>E1 数据基础设施</strong>：
              <ul>
                <li>
                  E11 数据硬件设施：根据学校是否设立独立数据中心、数据中心是否达到B级要求、数字终端配备师机比、数字终端配备生机比综合计分。
                </li>
                <li>
                  E12 数据系统平台：根据学校是否建设数据治理平台计分。
                </li>
              </ul>
            </li>

            <li>
              <strong>E2 数据安全水平</strong>：
              <ul>
                <li>
                  E21 数据安全合规与认证：根据学校部署的各类业务管理、教学平台建设模式，以及相关平台通过网络安全等级保护测评的数量和比例综合计分。
                </li>
                <li>
                  E22 数据风险事件记录：根据2023年至2025年间学校是否发生数据风险事件计分。
                </li>
              </ul>
            </li>
          </ul>

          <p class="rule-note">
            注：观测点计分完成后，对每个观测点分值进行归一化处理，转化为相同分值区间后参与加权计算。
          </p>
        </div>

      </section>

      <!-- 报告结尾 -->
      <div class="report-footer">
        <p class="footer-note">-本报告由中小学校数据文化成熟度评估监测系统自动生成-</p>
      </div>
    </div>
    <div v-else class="loading-container">
  <el-empty description="暂无报告数据，可能是由于评估尚未完成或计算未结束" />
  <el-button @click="goBack">返回上一页</el-button>
</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getReportDataDetail  } from '@/api/assessment'
import { getSchoolInfo } from '@/api/school'
import { getAssessmentData } from '@/utils/assessments'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import html2canvas from 'html2canvas'
import { jsPDF }from 'jspdf'
import {
  ArrowLeft,
  Download,
  Loading,
  DataAnalysis,
  Reading,
  Document,
  TrendCharts,
  Files,
  Setting,
  Trophy,
  UserFilled,
  StarFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(true)
const downloading = ref(false)
const reportData = ref({})
const reportContainer = ref(null)
const reportContent = ref(null)

// 图表引用
const overviewChart = ref(null)
const teacherRadarChart = ref(null)
const studentRadarChart = ref(null)
const literacyComparisonChart = ref(null)
const behaviorBarChart = ref(null)
const teacherEffectRadar = ref(null)
const studentEffectRadar = ref(null)
const assetAwarenessRadar = ref(null)

const studentEffectCircle = ref(null)
const teacherEffectCircle = ref(null)

// 图表实例
let chartInstances = []

// 计算属性
const dimensionScores = computed(() => reportData.value.dimension_scores || {})
const secondaryScores = computed(() => reportData.value.secondary_scores || {})
const observationScores = computed(() => reportData.value.observation_scores || {})
const institutionDetails = computed(() => reportData.value?.institution || {})
const behaviorDetails = computed(() => reportData.value?.behavior || {})
const assetDetails = computed(() => reportData.value?.asset || {})
const technologyDetails = computed(() => reportData.value?.technology || {})

const dimensionList = computed(() => [
  { name: '数据素养', score: dimensionScores.value.literacy },
  { name: '数据制度', score: dimensionScores.value.institution },
  { name: '数据行为', score: dimensionScores.value.behavior },
  { name: '数据资产', score: dimensionScores.value.asset },
  { name: '数据技术', score: dimensionScores.value.technology }
])

// 生命周期
onMounted(async () => {
  const assessmentId = route.params.id

  if (!assessmentId) {
    ElMessage.error('缺少评估ID')
    router.back()
    return
  }

  await loadReportData(assessmentId)

  if (route.query.download === '1') {
    setTimeout(() => {
      downloadPDF()
    }, 1500)
  }
})

onUnmounted(() => {
  // 销毁所有图表实例
  chartInstances.forEach(chart => chart?.dispose())
})

// 方法
const toNum = (v, def = 0) => {
  const n = parseFloat(v)
  return Number.isFinite(n) ? n : def
}



const loadReportData = async (assessmentId) => {
  loading.value = true
  try {
    const res = await getAssessmentData(assessmentId)
    const raw = res.data || res 
    const toF = (v) => parseFloat(v || 0)

    // 1. 尝试从不同位置获取分数数据（兼容性处理）
    // 后端 AssessmentSerializer 通常把分名字定为 literacy_score 等
    const info = raw.assessment || {}

    const processedData = {
      // --- A. 基础档案 ---
      school_name: raw.school_name || "学校名称",
      school_type: raw.school_type_display || raw.school_type || '未填写',
      area_display: raw.province ? `${raw.province}${raw.city}${raw.district}` : '未填写',
      founding_year: raw.founding_year || '未填写',
      teacher_count: raw.teacher_count || 0,
      student_count: raw.student_count || 0,

      // --- B. 评估概况 ---
      report_date: raw.report_date || info.updated_at,
      maturity_level: raw.scores?.maturity_level_display || info.maturity_level_display || "未知",
      total_score: 视觉处理(toF(raw.total_score || raw.scores?.total_score || info.total_score)),
      
      // --- C. 维度得分 (修正这里的路径) ---
      // 这里的 key 需要对应你后端 AssessmentSerializer 里的真实字段名
      dimension_scores: {
        literacy: toF(raw.dimension_scores?.literacy || info.literacy_score),
        institution: toF(raw.dimension_scores?.institution || info.institution_score),
        behavior: toF(raw.dimension_scores?.behavior || info.behavior_score),
        asset: toF(raw.dimension_scores?.asset || info.asset_score),
        technology: toF(raw.dimension_scores?.technology || info.technology_score)
      },

      // --- D. 二级指标得分 (增加可选链防止崩掉) ---
      secondary_scores: raw.secondary_scores || {},
      observation_scores: raw.observation_scores || {},
      participant_counts: raw.participant_counts || { teacher: 0, student: 0 },

      // --- E. 其他详情 (使用可选链) ---
      institution: raw.institution_details || raw.institution || {},
      behavior: raw.behavior_details || raw.behavior || {},
      asset: raw.asset_details || raw.asset || {},
      technology: raw.technology_details || raw.technology || {},
      observation_scores: raw.observation_scores || {},
      suggestions: raw.suggestions || { overall: "正在分析中..." },
      participant_counts: raw.participant_counts || { teacher: 0, student: 0},
      average_scores: raw.average_scores || { literacy: 3.0, institution: 3.0, behavior: 3.0, asset: 3.0, technology: 3.0 }
    }

    reportData.value = processedData
    loading.value = false
    await nextTick()
    initAllCharts()

  } catch (error) {
    console.error('数据加工失败:', error)
    ElMessage.error('报告数据解析失败')
    loading.value = false
  }
}

// 内部数值格式化辅助
function 视觉处理(num) {
  return parseFloat(num.toFixed(2))
}

const formatScore = (score) => {
  const n = Number(score)
  return Number.isFinite(n) ? `${n.toFixed(2)}分` : '暂无得分'
}

const initAllCharts = () => {
  console.log('开始初始化图表...')
  // 确保先销毁旧实例
  chartInstances.forEach(chart => chart?.dispose())
  chartInstances = []
  
  setTimeout(() => {
    initOverviewChart()
    initLiteracyRadarCharts()
    initLiteracyComparisonChart()
    initBehaviorBarChart()
    initBehaviorRadarCharts()
    initAssetAwarenessRadar()
    initSubjectiveCharts()
    console.log('图表初始化完成')
  }, 100)
}

const initSubjectiveCharts = () => {
  const getCircleOption = (score, color) => {
    const safeScore = Math.max(0, Math.min(5, Number(score) || 0))
    const displayScore = safeScore.toFixed(1)

    return {
      series: [{
        type: 'pie',
        radius: ['55%', '75%'],
        center: ['50%', '50%'],
        silent: true,
        label: {
          show: true,
          position: 'center',
          formatter: () => `{val|${displayScore}}{unit|分}`,
          rich: {
            val: { fontSize: 26, fontWeight: 'bold', color },
            unit: { fontSize: 14, color, padding: [0, 0, -5, 2] }
          }
        },
        data: [
          {
            value: safeScore,
            itemStyle: { color, borderRadius: 10 }
          },
          {
            value: Math.max(0, 5 - safeScore),
            itemStyle: { color: '#ebf1fa' }
          }
        ]
      }]
    }
  }

  if (teacherEffectCircle.value) {
    const chart = echarts.init(teacherEffectCircle.value, null, { renderer: 'svg' })
    chartInstances.push(chart)

    chart.setOption(
      getCircleOption(
        observationScores.value['C23'] || observationScores.value['C23_teacher'] || 0,
        '#409eff'
      )
    )
  }
}

// 概况柱状图
const initOverviewChart = () => {
  if (!overviewChart.value) {
    console.warn('找不到概况图表容器')
    return
  }
  try {
    const chart = echarts.init(overviewChart.value, null,{ renderer: 'svg' })
    chartInstances.push(chart)

    const dimensions = ['数据素养', '数据制度', '数据行为', '数据资产', '数据技术']
  const scores = [
      (dimensionScores.value.literacy || 0).toFixed(2),
      (dimensionScores.value.institution || 0).toFixed(2),
      (dimensionScores.value.behavior || 0).toFixed(2),
      (dimensionScores.value.asset || 0).toFixed(2),
      (dimensionScores.value.technology || 0).toFixed(2)
    ]
    // 从后端获取平均分，如果没有则使用默认值60
    const avgScoresData = reportData.value.average_scores || {}
    const avgScores = [
      (avgScoresData.literacy ?? 3.0).toFixed(2),
      (avgScoresData.institution ?? 3.0).toFixed(2),
      (avgScoresData.behavior ?? 3.0).toFixed(2),
      (avgScoresData.asset ?? 3.0).toFixed(2),
      (avgScoresData.technology ?? 3.0).toFixed(2),
    ]

    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['真实得分', '平均得分'], top: 40 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
      xAxis: { type: 'category', data: dimensions },
      yAxis: { type: 'value', max: 5 },
      series: [
        {
          name: '真实得分',
          type: 'bar',
          data: scores,
          itemStyle: { color: '#409eff' },
          label: { 
            show: true, 
            position: 'top',
            formatter: (params) => params.value
          }
        },
        {
          name: '平均得分',
          type: 'bar',
          data: avgScores,
          itemStyle: { color: '#e6a23c' },
          label: { 
            show: true, 
            position: 'top',
            formatter: (params) => params.value
          }
        }
      ]
    })
  } catch (e) {
    console.error('概况图表初始化失败:', e)
  }
}

// 数据素养雷达图
// 数据素养雷达图
const initLiteracyRadarCharts = () => {
  const indicators = [
    { name: '数据意识与思维', max: 5 },
    { name: '数据知识与技能', max: 5 },
    { name: '数据评价与交流', max: 5 },
    { name: '数据应用与创新', max: 5 },
    { name: '数据伦理与隐私', max: 5 }
  ]

  const getCommonOptions = (title, color, scores) => {
    return {
      title: {
        text: title,
        left: 'center',
        top: 5,
        textStyle: { fontSize: 14, fontWeight: 'bold' }
      },
      radar: {
        indicator: indicators,
        radius: '60%',
        center: ['50%', '55%'],
        axisName: { color: '#666', fontSize: 10 }
      },
      series: [{
        type: 'radar',
        data: [{
          value: scores,
          name: title,
          areaStyle: {
            color,
            opacity: 0.3
          },
          label: {
            show: true,
            formatter: (params) => {
              return params.value ? parseFloat(params.value).toFixed(2) : '0.00'
            },
            fontSize: 11,
            color: '#000'
          }
        }],
        itemStyle: { color }
      }]
    }
  }

  // 教师雷达图：A11-A15
  if (teacherRadarChart.value) {
    try {
      const chart = echarts.init(teacherRadarChart.value, null, { renderer: 'svg' })
      chartInstances.push(chart)

      chart.setOption(getCommonOptions('教师数据素养', '#409eff', [
        observationScores.value['A11'] || 0,
        observationScores.value['A12'] || 0,
        observationScores.value['A13'] || 0,
        observationScores.value['A14'] || 0,
        observationScores.value['A15'] || 0
      ]))
    } catch (e) {
      console.error('教师雷达图初始化失败:', e)
    }
  }

  // 学生雷达图：仍然读取 A31-A35 观测点
  if (studentRadarChart.value) {
    try {
      const chart = echarts.init(studentRadarChart.value, null, { renderer: 'svg' })
      chartInstances.push(chart)

      chart.setOption(getCommonOptions('学生数据素养', '#909399', [
        observationScores.value['A31'] || 0,
        observationScores.value['A32'] || 0,
        observationScores.value['A33'] || 0,
        observationScores.value['A34'] || 0,
        observationScores.value['A35'] || 0
      ]))
    } catch (e) {
      console.error('学生雷达图初始化失败:', e)
    }
  }
}

// 数据素养综合对比柱状图
// 数据素养综合对比柱状图
const initLiteracyComparisonChart = () => {
  if (!literacyComparisonChart.value) return

  try {
    const chart = echarts.init(literacyComparisonChart.value, null, { renderer: 'svg' })
    chartInstances.push(chart)

    const categories = [
      '数据意识与思维',
      '数据知识与技能',
      '数据评价与交流',
      '数据应用与创新',
      '数据伦理与隐私'
    ]

    const commonLabel = {
      show: true,
      position: 'top',
      distance: 5,
      formatter: (params) => params.value ? parseFloat(params.value).toFixed(2) : '0.00'
    }

    chart.setOption({
      tooltip: {
        trigger: 'axis',
        valueFormatter: (value) => value ? parseFloat(value).toFixed(2) : '0.00'
      },
      legend: { data: ['教师', '学生'], top: 40 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
      xAxis: { type: 'category', data: categories },
      yAxis: { type: 'value', max: 5, name: '分数(分)' },
      series: [
        {
          name: '教师',
          type: 'bar',
          label: commonLabel,
          data: [
            observationScores.value['A11'] || 0,
            observationScores.value['A12'] || 0,
            observationScores.value['A13'] || 0,
            observationScores.value['A14'] || 0,
            observationScores.value['A15'] || 0
          ],
          itemStyle: { color: '#409eff' }
        },
        {
          name: '学生',
          type: 'bar',
          label: commonLabel,
          data: [
            observationScores.value['A31'] || 0,
            observationScores.value['A32'] || 0,
            observationScores.value['A33'] || 0,
            observationScores.value['A34'] || 0,
            observationScores.value['A35'] || 0
          ],
          itemStyle: { color: '#909399' }
        }
      ]
    })
  } catch (e) {
    console.error('数据素养对比图初始化失败:', e)
  }
}

// 数据行为横向柱状图
// 数据行为监测柱状图
const initBehaviorBarChart = () => {
  if (!behaviorBarChart.value) return

  try {
    const chart = echarts.init(behaviorBarChart.value, null, { renderer: 'svg' })
    chartInstances.push(chart)

    const c11 = Number(observationScores.value['C11'] || 0)
    const c12 = Number(observationScores.value['C12'] || 0)

    chart.setOption({
      title: { text: '数据行为监测得分', left: 'center', top: 5 },
      tooltip: {
        trigger: 'axis',
        valueFormatter: (value) => `${Number(value || 0).toFixed(2)}分`
      },
      grid: { left: '20%', right: '12%', bottom: '12%', top: 55 },
      xAxis: {
        type: 'value',
        max: 5,
        name: '得分',
        axisLabel: {
          fontSize: 14,
          color: '#333'
        }
      },
      yAxis: {
        type: 'category',
        data: ['学生数据行为', '教师数据行为'],
        axisLabel: {
          fontSize: 14,
          color: '#333'
        }
      },
      series: [{
        type: 'bar',
        data: [
          { value: c12, itemStyle: { color: '#67c23a' } },
          { value: c11, itemStyle: { color: '#409eff' } }
        ],
        label: {
          show: true,
          position: 'right',
          fontSize: 14,
          formatter: (params) => `${Number(params.value || 0).toFixed(2)}分`
        }
      }]
    })
  } catch (e) {
    console.error('数据行为柱状图初始化失败:', e)
  }
}

// 数据行为效果雷达图
const initBehaviorRadarCharts = () => {
  const indicators = [
    { name: '数据意识与思维', max: 5 },
    { name: '数据知识与技能', max: 5 },
    { name: '数据评价与交流', max: 5 },
    { name: '数据应用与创新', max: 5 },
    { name: '数据伦理与隐私', max: 5 }
  ]

  const getRadarOption = (title, color, scores) => {
    return {
      title: { 
        text: title, 
        left: 'center', 
        top: 0, 
        textStyle: { fontSize: 20, fontWeight: 'bold' } 
      },
      radar: { 
        indicator: indicators, 
        radius: '55%', 
        center: ['50%', '60%'],
        axisName: { color: '#333', fontSize: 11, fontWeight: 'bold' }
      },
      series: [{
        type: 'radar',
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2.5 },
        data: [{
          value: scores,
          name: title,
          // 纯数字标注配置，去掉所有背景和边框
          label: {
            show: true,
            distance: 8, // 稍微拉开距离，防止压在点上
            formatter: (params) => {
              return params.value ? parseFloat(params.value).toFixed(2) : '0.00';
            },
            fontSize: 12,
            fontWeight: 'bold',
            color: '#000', // 纯黑字体
            backgroundColor: 'transparent' // 确保背景透明
          },
          areaStyle: { color: color, opacity: 0.3 }
        }],
        itemStyle: { color: color }
      }]
    }
  }

  if (teacherEffectRadar.value) {
    try {
      const chart = echarts.init(teacherEffectRadar.value , null, { renderer: 'svg' })
      chartInstances.push(chart)
      chart.setOption({
        radar: { 
          indicator: indicators, 
          radius: '55%', 
          center: ['50%', '55%'],
          axisName: { color: '#666', fontSize: 10 }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              observationScores.value['A11'] || 0,
              observationScores.value['A12'] || 0,
              observationScores.value['A13'] || 0,
              observationScores.value['A14'] || 0,
              observationScores.value['A15'] || 0
            ],
            name: '教师数据素养',
            areaStyle: { color: 'rgba(64, 158, 255, 0.3)' }
          }],
          itemStyle: { color: '#409eff' }
        }]
      })
      const scores = [
        parseFloat(observationScores.value['A11'] || 0),
        parseFloat(observationScores.value['A12'] || 0),
        parseFloat(observationScores.value['A13'] || 0),
        parseFloat(observationScores.value['A14'] || 0),
        parseFloat(observationScores.value['A15'] || 0)
      ]
      chart.setOption(getRadarOption('教师数据素养', '#409eff', scores))
    } catch (e) {
      console.error('教师行为雷达图初始化失败:', e)
    }
  }

  if (studentEffectRadar.value) {
    try {
      const chart = echarts.init(studentEffectRadar.value , null, { renderer: 'svg' })
      chartInstances.push(chart)
      chart.setOption({
        radar: { 
          indicator: indicators, 
          radius: '55%', 
          center: ['50%', '55%'],
          axisName: { color: '#666', fontSize: 10 }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              observationScores.value['A31'] || 0,
              observationScores.value['A32'] || 0,
              observationScores.value['A33'] || 0,
              observationScores.value['A34'] || 0,
              observationScores.value['A35'] || 0
            ],
            name: '学生数据素养',
            areaStyle: { color: 'rgba(144, 147, 153, 0.3)' }
          }],
          itemStyle: { color: '#909399' }
        }]
      })
      const scores = [
        parseFloat(observationScores.value['A31'] || 0),
        parseFloat(observationScores.value['A32'] || 0),
        parseFloat(observationScores.value['A33'] || 0),
        parseFloat(observationScores.value['A34'] || 0),
        parseFloat(observationScores.value['A35'] || 0)
      ]
      chart.setOption(getRadarOption('学生数据素养', '#909399', scores))
    } catch (e) {
      console.error('学生行为雷达图初始化失败:', e)
    }
  }
}

const schoolTypeLabel = (v) => {
  const map = {
    primary: '小学',
    junior: '初中',
    senior: '高中',
    nine_year: '九年一贯制',
    twelve_year: '十二年一贯制',
  }

  return map[v] || v || '未填写'
}

// 数据资产意识雷达图
const initAssetAwarenessRadar = () => {
  if (!assetAwarenessRadar.value) return
  try {
    const chart = echarts.init(assetAwarenessRadar.value , null, { renderer: 'svg' })
    chartInstances.push(chart)

    chart.setOption({
      radar: {
        indicator: [
          { name: '数据资产价值意识', max: 5 },
          { name: '数据资产应用意识', max: 5 },
          { name: '数据资产治理意识', max: 5 }
        ],
        radius: '65%',         // 稍微放大一点
        center: ['50%', '65%'], // 中心点下移，给顶部数字留空间
        axisName: { 
          color: '#333',       
          fontSize: 14,        // 放大：指标名称（如：价值意识）
          fontWeight: 'bold'
        }
      },
      series: [{
        type: 'radar',
        symbol: 'circle',
        symbolSize: 10,        // 放大：观测点圆点
        lineStyle: { width: 3 },
        data: [{
          value: [
            parseFloat(observationScores.value['D11'] || 0),
            parseFloat(observationScores.value['D12'] || 0),
            parseFloat(observationScores.value['D13'] || 0)
          ],
          name: '资产意识',
          // 核心配置：这里负责显示顶点的数值
          label: {
            show: true,        // 开启数值显示
            position: 'inside',   // 显示在点上方
            distance: 12,      // 距离点的距离，防止重合
            formatter: (params) => params.value ? params.value.toFixed(2) : '0.00',
            color: '#000'      // 黑色字体
          },
          areaStyle: { color: '#409eff', opacity: 0.3 }
        }],
        itemStyle: { color: '#409eff' }
      }]
    })
  } catch (e) {
    console.error('资产雷达图初始化失败:', e)
  }
}

// 辅助方法
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

const getPerformanceText = (score) => {
  if (score >= 4.5) return '表现优秀'
  if (score >= 3.5) return '表现均衡'
  return '有待提升'
}

const getLevelNumber = (level) => {
  const map = { '初始级': '第1级', '成长级': '第2级', '成熟级': '第3级', '引领级': '第4级' }
  return map[level] || ''
}

const getTotalManagementDocs = () => {
  const d = institutionDetails.value
  return d.management_doc_count || 0
}

const getTotalPracticeDocs = () => {
  const d = institutionDetails.value
  return d.practice_doc_count || 0
}

const getLeadershipGroupText = () => {
  const type = institutionDetails.value.leadership_group_type

  if (type === 'standard') {
    return '已设置规范管理小组'
  }

  if (type === 'basic') {
    return '已设置基础管理小组'
  }

  if (type === 'none') {
    return '未设置相关小组'
  }

  return '未填写'
}

const getTotalCertificates = () => {
  const d = institutionDetails.value
  return (
    (d.national_cert_count || 0) +
    (d.provincial_cert_count || 0) +
    (d.city_cert_count || 0)
  )
}

const getManagementDocStatusText = () => {
  const status = institutionDetails.value.management_doc_status

  if (status === 'clear_required') {
    return '学校已在相关制度或规范文件中，对数据的采集、使用、存储与共享等环节作出明确规定。'
  }

  if (status === 'follow_policy') {
    return '学校暂未在校内制度中作出明确要求，但遵循国家或区域相关文件执行。'
  }

  if (status === 'self_awareness') {
    return '学校暂未在校内制度中作出明确要求，当前主要依靠师生自主意识开展数据管理相关工作。'
  }

  return '学校数据管理制度类文件情况未填写。'
}

const getPracticeDocStatusText = () => {
  const status = institutionDetails.value.practice_doc_status

  if (status === 'published') {
    return '学校已发布指导师生使用数据的相关指南、操作说明或工作手册。'
  }

  if (status === 'internal_training') {
    return '学校暂未发布相关指南或操作手册，但通过内部培训对师生数据实践进行指导。'
  }

  if (status === 'self_practice') {
    return '学校暂未发布相关指南或操作手册，当前主要依靠师生自主实践开展数据应用。'
  }

  return '学校数据实践指导类文件情况未填写。'
}

const getTotalCases = () => {
  const d = behaviorDetails.value
  return (d.case_national_count || 0) + (d.case_provincial_count || 0) + (d.case_city_count || 0)
}

const getTotalAwards = () => {
  const d = behaviorDetails.value
  return (d.award_national_count || 0) + (d.award_provincial_count || 0) + (d.award_city_count || 0)
}

const getTotalMedia = () => {
  const d = behaviorDetails.value
  return (d.media_national_count || 0) + (d.media_provincial_count || 0) + (d.media_city_count || 0)
}

const getTotalConference = () => {
  const d = behaviorDetails.value
  return (d.conference_national_count || 0) + (d.conference_provincial_count || 0) + (d.conference_city_count || 0)
}

const getSelectedCount = (value) => {
  if (Array.isArray(value)) {
    return value.filter(Boolean).length
  }

  if (value && typeof value === 'object') {
    return Object.values(value).filter(Boolean).length
  }

  return 0
}

const getTeacherBehaviorCount = () => {
  return getSelectedCount(behaviorDetails.value.teacher_data_behavior_items)
}

const getStudentBehaviorCount = () => {
  return getSelectedCount(behaviorDetails.value.student_data_behavior_items)
}

const getStudentDeviceProvisionText = () => {
  const value = behaviorDetails.value.student_device_provision

  if (value === 'none') {
    return '未配备数字化学习设备'
  }

  if (value === 'computer_room') {
    return '仅建有计算机机房，供班级轮流上课使用'
  }

  if (value === 'computer_room_and_terminal') {
    return '建有计算机机房，并为学生配备其他数字终端'
  }

  return '未填写'
}

const getStudentAccountStatusText = () => {
  const value = behaviorDetails.value.student_account_status

  if (value === 'none') {
    return '未为学生开通账号'
  }

  if (value === 'partial') {
    return '部分学生开通账号'
  }

  if (value === 'all') {
    return '全校学生均开通账号'
  }

  return '未填写'
}

const formatDataVolume = (volume) => {
  const n = Number(volume)

  if (!Number.isFinite(n)) {
    return '0.00 GB'
  }

  return `${n.toFixed(2)} GB`
}

const getTotalDataVolume = () => {
  const d = assetDetails.value || {}

  return [
    d.teaching_data_volume,
    d.teacher_student_data_volume,
    d.digital_resource_data_volume,
    d.campus_admin_data_volume,
    d.other_type_data_volume
  ].reduce((sum, value) => {
    const n = Number(value)
    return sum + (Number.isFinite(n) ? n : 0)
  }, 0)
}

const getDataStatMethodText = (method) => {
  if (method === 'unable') {
    return '无法统计'
  }

  if (method === 'estimated') {
    return '可部分估算'
  }

  if (method === 'system_query') {
    return '可系统查询'
  }

  return '未填写'
}

const getPerCapitaVolume = () => {
  const total = getTotalDataVolume()
  const people = Number(reportData.value.student_count || 0) + Number(reportData.value.teacher_count || 0)

  if (!people) {
    return '0.00'
  }

  return (total / people).toFixed(2)
}

const getVolumePercentage = (value, max) => {
  const v = Number(value)
  const m = Number(max)

  if (!Number.isFinite(v) || !Number.isFinite(m) || m <= 0) {
    return 0
  }

  return Math.min(100, (v / m) * 100)
}

const getPlatformBuildModeText = () => {
  const mode = technologyDetails.value.platform_build_mode

  if (mode === 'self_built') {
    return '完全自建平台'
  }

  if (mode === 'external') {
    return '完全接入外部平台'
  }

  if (mode === 'mixed') {
    return '接入外部和自建平台并行'
  }

  return '未填写'
}

const getDataCenterText = () => {
  const details = technologyDetails.value

  if (details.has_independent_data_center === true) {
    const standard = details.data_center_standard

    if (standard === 'fully_compliant') {
      return '学校建有独立数据中心，且相关指标完全达到B级要求'
    }

    if (standard === 'partially_compliant') {
      return '学校建有独立数据中心，相关指标部分达到B级要求'
    }

    if (standard === 'not_compliant') {
      return '学校建有独立数据中心，但相关指标未达到B级要求'
    }

    return '学校建有独立数据中心，但B级要求达成情况未填写'
  }

  if (details.has_independent_data_center === false) {
    return '学校未设立独立数据中心'
  }

  return '学校数据中心建设情况未填写'
}

const getSecurityRatioText = () => {
  const ratio = technologyDetails.value.security_certified_ratio

  if (ratio === 'zero') {
    return '认定比例 = 0'
  }

  if (ratio === 'low') {
    return '0＜认定比例≤40%'
  }

  if (ratio === 'medium') {
    return '40%＜认定比例≤80%'
  }

  if (ratio === 'high') {
    return '认定比例＞80%'
  }

  return '未填写'
}

const goBack = () => {
  router.back()
}

// PDF下载 - 单页完整显示，不分页
const downloadPDF = async () => {
  if (!reportContent.value) return
  
  downloading.value = true
  ElMessage.info('正在生成PDF，请稍候...')

  try {
    const element = reportContent.value
    
    // 整体截图
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
      windowWidth: element.scrollWidth,
      height: element.scrollHeight,
      scrollY: -window.scrollY
    })

    const imgData = canvas.toDataURL('image/png', 1.0)
    
    // A4宽度 210mm，根据内容高度动态计算PDF高度
    const pdfWidth = 210
    const imgWidth = canvas.width
    const imgHeight = canvas.height
    const ratio = pdfWidth / imgWidth
    const pdfHeight = imgHeight * ratio
    
    // 创建自定义尺寸的PDF（宽度A4，高度根据内容）
    const pdf = new jsPDF('p', 'mm', [pdfWidth, pdfHeight])
    
    pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)

    pdf.save(`${reportData.value.school_name || '学校'}_数据文化成熟度评估报告.pdf`)
    ElMessage.success('PDF下载成功')
  } catch (error) {
    console.error('生成PDF失败:', error)
    ElMessage.error('生成PDF失败，请重试')
  } finally {
    downloading.value = false
  }
}

// 获取生机比描述文字
const getStudentRatioText = () => {
  const val = technologyDetails.value.student_device_ratio
  if (!val) return '未填写'
  
  // 这里的 Key (low/medium/high) 需要与你后端 ChoiceField 定义的完全一致
  const map = {
    'low': '小于 6:1',
    'medium': '介于 6:1 与 15:1 之间',
    'high': '大于等于 15:1'
  }
  return map[val] || val
}

// 获取师机比描述文字
const getTeacherRatioText = () => {
  const val = technologyDetails.value.teacher_device_ratio
  if (!val) return '未填写'
  
  const map = {
    'low': '小于 1:1',
    'medium': '介于 1:1 与 4:1 之间',
    'high': '大于等于 4:1'
  }
  return map[val] || val
}
</script>

<style scoped>
.report-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.report-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: #909399;
}

.loading-icon {
  font-size: 48px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.report-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

/* 主观评价卡片容器 */
.subjective-eval-cards {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  background-color: #f0f7ff; /* 浅蓝色背景底 */
  padding: 30px 20px;
  border-radius: 12px;
}

.eval-card {
  flex: 1;
  background: #fff;
  border-radius: 10px;
  padding: 20px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border: 1px solid #e4e7ed;
}

/* 上方的字放大点 */
.eval-top-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

/* 中间的图容器（稍微调小一点） */
.circle-chart {
  width: 100%;
  height: 180px; /* 控制高度即可控制图的大小 */
}

/* 下方的字放大点 */
.eval-bottom-info {
  font-size: 15px;
  color: #606266;
  margin-top: 10px;
}

/* 报告标题 */
.report-title-section {
  text-align: center;
  padding: 40px 0;
  border-bottom: 2px solid #409eff;
  margin-bottom: 30px;
}

.main-title {
  font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  color: #303133;
  margin: 0 0 16px 0;
  font-size: 30px;
  font-weight: 700 !important;
}

.report-date {
  color: #909399;
  font-size: 14px;
}

/* 报告说明 */
.report-intro {
  background: #ecf5ff;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 40px;
  line-height: 1.8;
}

.report-intro p {
  margin: 0 0 16px 0;
  color: #606266;
}

.report-intro ol {
  margin: 0;
  padding-left: 20px;
}

.report-intro li {
  margin-bottom: 8px;
  color: #606266;
}

/* 章节样式 */
.report-section {
  margin-bottom: 50px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  color: #303133;
  padding-bottom: 12px;
  border-bottom: 2px solid #409eff;
  margin-bottom: 20px;
  display: flex; justify-content: center; align-items: center; gap: 10px; text-align: center;
}

.section-title .el-icon {
  color: #409eff;
}

.section-summary {
  text-indent: 2em;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 24px;
  font-size:18px;
}

/* 概况得分卡片 */
.overview-scores {
  display: flex;
  gap: 24px;
  margin-bottom: 30px;
}

.score-card {
  flex: 1;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.score-card.total {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
}

.score-card.level {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: #fff;
}

.score-card .label {
  display: block;
  margin-bottom: 8px;
  opacity: 0.9;
  font-size: 22px;
  font-weight: bold;
}

.score-card .value {
  font-size: 28px;
  font-weight: bold;
}

/* 概况图表区域 */
.overview-chart-container {
  display: flex;
  gap: 24px;
  margin-bottom: 30px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.overview-left {
  width: 200px;
  background: #f5f7fa;
  padding: 16px;
}

.dimension-list {
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
}

.dimension-header {
  background: #409eff;
  color: #fff;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 400;
  font-size: 10px;
}

.total-score-badge {
  background: #e6a23c;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.level-badge {
  background: #67c23a;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.dimension-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.dimension-item:last-child {
  border-bottom: none;
}

.dim-name {
  color: #606266;
}

.dim-score {
  color: #303133;
  font-weight: 500;
}

.overview-right {
  flex: 1;
  padding: 16px;
}

/* AI建议 */
.ai-suggestion {
  background: #fdf6ec;
  padding: 20px;
  border-radius: 8px;
  margin: 24px 0;
  border-left: 4px solid #e6a23c;
}

.ai-suggestion h4 {
  margin: 0 0 12px 0;
  color: #e6a23c;
}

.ai-suggestion p {
  margin: 0;
  color: #606266;
  line-height: 1.8;
}

.evaluation-note {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-top: 20px;
}

.evaluation-note h4 {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 14px;
}

.evaluation-note p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

/* 数据素养得分卡片 */
.literacy-scores {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.literacy-score-card {
  flex: 1;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
}

.literacy-score-card.teacher {
  border-bottom: 4px solid #409eff;
  background: #f0f9ff;
}

.literacy-score-card.student {
  border-bottom: 4px solid #909399;
  background: #f5f7fa;
}

.literacy-score-card .score {
  display: block;
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.literacy-score-card.teacher .score { color: #409eff; }
.literacy-score-card.student .score { color: #909399; }

.literacy-score-card .label {
  color: #606266;
  font-size: 18px;
}

.participant-info {
  font-size: 20px;
  display: flex;
  justify-content: center;
  gap: 40px;
  color: #606266;
  margin-bottom: 24px;
}

/* 雷达图区域 */
.literacy-radar-section,
.literacy-comparison-section {
  margin: 30px 0;
}

.literacy-radar-section h4,
.literacy-comparison-section h4 {
  color: #606266;
  margin-bottom: 16px;

  text-align: center;         /* 核心：文字居中 */
  margin: 20px 0;             /* 建议：增加上下边距，让排版更好看 */
  font-size: 18px;            /* 之前你提到的增大字体 */
  font-weight: bold;  
}

.literacy-radar-section h4 {
  text-align: center;         /* 核心：文字居中 */
  margin: 20px 0;             /* 建议：增加上下边距，让排版更好看 */
  font-size: 18px;            /* 之前你提到的增大字体 */
  font-weight: bold;          /* 加粗 */
}
.radar-charts-row {
  display: flex;
  gap: 16px;
}

.radar-chart-item {
  flex: 1;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 10px;
}

/* 制度卡片 */
.institution-card,
.behavior-card,
.asset-card,
.tech-card {
  background: #ecf5ff;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  background: #409eff;
  color: #fff;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 500;
  font-size: 20px !important;
  font-weight: bold;
}

.card-subtitle {
  font-size: 13px;
  opacity: 0.9;
}

.card-content {
  padding: 20px;
}

.info-item {
  margin-bottom: 16px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  display: block;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  font-weight: bold;
}

.info-value {
  color: #606266;
  line-height: 1.8;
}

.info-value p {
  margin: 4px 0;
}

/* 大模型分析结果样式 */
.llm-analysis {
  margin-top: 8px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.llm-analysis p {
  color: #409eff;
  font-weight: 500;
  margin-bottom: 8px;
}

.analysis-content {
  color: #606266;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 计分规则说明 */
.scoring-rules {
  background-color: #f0f9eb;
  border-left: 5px solid #67c23a;
  padding: 16px;
  margin-bottom: 24px;
  border-radius: 4px;
}

.scoring-rules h4 {
  color: #67c23a;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.scoring-rules p {
  color: #606266;
  margin: 0 0 8px 0;
  font-size: 14px;
  line-height: 1.6;
}

.scoring-rules ul {
  margin: 8px 0 12px 20px;
  padding: 0;
  color: #606266;
  font-size: 14px;
}

.scoring-rules li {
  margin-bottom: 6px;
  line-height: 1.6;
}

.scoring-rules .rule-note {
  font-size: 12px;
  color: #909399;
  font-style: italic;
  margin-top: 8px;
}

/* 行为统计 */
.login-stats {
  margin-bottom: 16px;
}

.login-stats p {
  margin: 8px 0;
  color: #606266;
}

.achievement-section {
  margin-bottom: 20px;
}

.achievement-section h2 {
  color: #409eff;
  margin: 0 0 8px 0;
}

.achievement-section p {
  margin: 0;
  color: #606266;
}

.behavior-radar-row {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

/* 学校基础信息卡片样式 */
.school-basic-card {
  margin: 20px auto 40px;
  background-color: #f5f7fa; /* 浅蓝色背景 */
  border: 1px solid #e4e7ed; 
  padding: 30px 20px;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.basic-info-grid {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.grid-label {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  font-weight: 500;
}

.grid-value {
  font-size: 14px;
  color: #909399;
  /* 沿用中英文双字体要求 */
  font-family: "Times New Roman", "Microsoft YaHei", sans-serif;
}

/* 给项之间加个细微的分隔线（可选，增加精致感） */
.grid-item:not(:last-child) {
  border-right: 1px solid #e4eaf2;
}

/* 资产进度条 */
.staff-info {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 24px;
  color: #606266;
}

.asset-progress-section {
  display: flex;
  gap: 24px;
}

.progress-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.progress-header {
  margin-bottom: 12px;
}

.progress-title {
  color: #909399;
  font-size: 13px;
}

.progress-value {
  font-size: 28px;
  font-weight: bold;
  color: #67c23a;
  margin-bottom: 8px;
}

.progress-value.red {
  color: #f56c6c;
}

.progress-label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 12px;
}

.progress-range {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

/* 报告结尾 */
.report-footer {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  border-top: 1px solid #e4e7ed;
  margin-top: 40px;
}

.footer-note {
  font-size: 12px;
  margin-top: 8px;
}

/* 图表容器 */
.chart-box {
  width: 100%;
}

/* 分页符（PDF打印用） */
.page-break {
  page-break-before: always;
}

.literacy-scores.two-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: 20px;
}

.radar-charts-row.two-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 24px;
}

/* 数据素养雷达图区域居中 */
.literacy-radar-section {
  text-align: center;
}

.radar-charts-row.two-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(320px, 420px));
  justify-content: center;
  align-items: center;
  gap: 32px;
  width: 100%;
  margin: 0 auto;
}

.radar-chart-item {
  display: flex;
  justify-content: center;
  align-items: center;
}

.radar-chart-item .chart-box {
  width: 420px;
  max-width: 100%;
  margin: 0 auto;
}

/* 数据素养柱状图居中 */
.literacy-comparison-section {
  text-align: center;
}

.literacy-comparison-section .chart-box {
  width: 760px;
  max-width: 100%;
  margin: 0 auto;
}

/* 两张得分卡片也居中 */
.literacy-scores.two-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 320px));
  justify-content: center;
  gap: 24px;
  margin: 20px auto;
}

.institution-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 40px;
  align-items: flex-start;
}

.institution-grid .info-item {
  margin-bottom: 0;
}

.institution-grid .info-value p {
  margin: 0 0 8px 0;
  line-height: 1.7;
  text-align: justify;
}

.behavior-monitor-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 40px;
  align-items: flex-start;
}

.behavior-monitor-grid .info-item {
  margin-bottom: 0;
}

.behavior-monitor-grid .info-value p {
  margin: 0 0 8px 0;
  line-height: 1.7;
  text-align: justify;
}

.behavior-chart {
  width: 760px;
  max-width: 100%;
  margin: 24px auto 0;
}

.subjective-eval-cards.single {
  display: flex;
  justify-content: center;
}

.subjective-eval-cards.single .eval-card {
  max-width: 320px;
}

.asset-card-header {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  padding: 12px 20px;
}

.asset-card-header .card-subtitle {
  position: absolute;
  right: 20px;
  font-size: 13px;
  opacity: 0.9;
}

.asset-desc {
  margin: 0 0 14px 0;
  line-height: 1.8;
  color: #606266;
  text-align: center;
}

.asset-awareness-chart {
  width: 520px;
  max-width: 100%;
  margin: 0 auto;
}

.asset-status-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 36px;
  margin-bottom: 24px;
}

.asset-status-grid .info-item {
  margin-bottom: 0;
}

.asset-status-grid .info-value p {
  margin: 0;
  line-height: 1.8;
  text-align: justify;
}

.asset-volume-table {
  width: 100%;
  margin: 20px 0 28px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.asset-volume-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
}

.asset-volume-row:last-child {
  border-bottom: none;
}

.asset-volume-row span {
  padding: 12px 16px;
  line-height: 1.6;
  color: #606266;
}

.asset-volume-row.header {
  background: #f5f7fa;
  font-weight: 600;
}

.asset-volume-row.header span {
  color: #303133;
}

.technology-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 40px;
  align-items: flex-start;
}

.technology-grid .info-item {
  margin-bottom: 0;
}

.technology-grid .info-value p {
  margin: 0 0 8px 0;
  line-height: 1.7;
  text-align: justify;
}

/* 数据应用成效新版卡片布局 */
.behavior-effect-content {
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  gap: 28px;
  padding: 28px;
  background: #eaf4ff;
}

.effect-left,
.effect-right {
  background: linear-gradient(180deg, #f7fbff 0%, #eef7ff 100%);
  border-radius: 12px;
  padding: 26px;
  box-sizing: border-box;
}

.effect-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 22px;
}

.effect-info-card {
  display: grid;
  grid-template-columns: 54px 1fr;
  gap: 16px;
  align-items: flex-start;
}

.effect-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(180deg, #4da3ff 0%, #2f8df5 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.28);
}

.effect-icon :deep(.el-icon) {
  font-size: 26px;
  color: #ffffff;
}

.effect-text h4,
.effect-title-row h4 {
  margin: 0 0 12px 0;
  font-size: 17px;
  font-weight: 700;
  color: #303133;
}

.effect-text p,
.effect-desc {
  margin: 0;
  color: #606266;
  font-size: 15px;
  line-height: 1.8;
  text-align: justify;
}

.effect-divider {
  height: 1px;
  background: #dcecff;
  margin-left: 60px;
}

.effect-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.effect-title-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 10px;
}

.effect-desc {
  width: 100%;
  margin-bottom: 18px;
}

.effect-circle-wrap {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.effect-circle-chart {
  width: 260px;
  height: 220px;
}

.effect-participant {
  margin-top: 10px;
  padding: 10px 20px;
  background: #ffffff;
  border-radius: 8px;
  color: #606266;
  font-size: 15px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.08);
}

@media (max-width: 768px) {
  .technology-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .asset-card-header {
    flex-direction: column;
    gap: 6px;
  }

  .asset-card-header .card-subtitle {
    position: static;
  }

  .asset-status-grid {
    grid-template-columns: 1fr;
  }

  .asset-volume-row {
    grid-template-columns: 1fr;
  }

  .asset-volume-row span {
    border-bottom: 1px solid #ebeef5;
  }

  .asset-volume-row span:last-child {
    border-bottom: none;
  }
}

@media (max-width: 768px) {
  .behavior-monitor-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .behavior-chart {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .institution-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .radar-charts-row.two-columns,
  .literacy-scores.two-columns {
    grid-template-columns: 1fr;
  }

  .radar-chart-item .chart-box,
  .literacy-comparison-section .chart-box {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .literacy-scores.two-columns,
  .radar-charts-row.two-columns {
    grid-template-columns: 1fr;
  }
}

/* 打印时隐藏操作栏 */
@media print {
  .no-print {
    display: none !important;
  }
  
  .report-content {
    padding: 0;
  }
}
</style>
