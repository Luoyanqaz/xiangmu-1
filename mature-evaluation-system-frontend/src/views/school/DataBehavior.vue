<template>
  <div class="data-behavior-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据行为评价</span>
            <el-tag v-if="isReadonly" type="info" style="margin-left: 10px">只读模式</el-tag>
          </div>
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="!isReadonly">
            保存
          </el-button>
        </div>
      </template>

      <el-alert
        v-if="isReadonly"
        :title="readonlyTip"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-alert
        v-else
        title="评价说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        为全面评价您所在学校"数据行为"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        label-position="top"
        class="behavior-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据行为监测 -->
              <!-- 1. 数据行为监测 -->
      <div class="section-title">1. 数据行为监测</div>

      <!-- C11 教师数据行为 -->
      <div class="subsection-title">（1）教师数据行为</div>

      <el-form-item>
        <template #label>
          <div class="label-with-hint">
            <span>学校教师每周使用多媒体一体机、智能黑板、希沃白板等数字化设备开展教学的人均频次？</span>
            <el-popover placement="top-start" :width="380" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写说明</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">
                  请填写学校教师每周使用多媒体一体机、智能黑板、希沃白板等数字化设备开展教学的人均次数，仅填写整数。
                </p>
                <p class="hint-example">
                  <em>示例：若教师平均每周使用数字化设备开展教学 12 次，则填写「12」。</em>
                </p>
              </div>
            </el-popover>
          </div>
        </template>

        <div class="inline-inputs">
          <span>教师人均使用</span>
          <el-input-number
            v-model="formData.teacher_device_use_freq"
            :min="0"
            :controls="false"
          />
          <span>次</span>
        </div>
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="label-with-hint">
            <span>学校教师每周使用数据相关平台获取教学资源、分析学情、管理学生等的人均频次？</span>
            <el-popover placement="top-start" :width="420" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写说明</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">
                  数据相关平台包括国家智慧教育平台、地方智慧教育平台、教学平台、教务系统、校园一卡通等各类服务平台。
                </p>
                <p class="hint-example">
                  <em>示例：若教师平均每周登录平台获取资源、分析学情或管理学生 8 次，则填写「8」。</em>
                </p>
              </div>
            </el-popover>
          </div>
        </template>

        <div class="inline-inputs">
          <span>教师人均使用</span>
          <el-input-number
            v-model="formData.teacher_platform_use_freq"
            :min="0"
            :controls="false"
          />
          <span>次</span>
        </div>
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="label-with-hint">
            <span>学校教师日常教学中已常态化开展的数据行为有哪些？</span>
            <el-popover placement="top-start" :width="420" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写说明</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">
                  请根据学校教师日常教学中已经常态化开展的数据行为进行勾选，可多选。
                </p>
                <p class="hint-example">
                  <em>系统将根据勾选数量进行计分。若选择“其他”，请在下方补充说明。</em>
                </p>
              </div>
            </el-popover>
          </div>
        </template>

        <el-checkbox-group
          v-model="formData.teacher_data_behavior_items"
          class="behavior-checkbox-group"
        >
          <el-checkbox label="score_analysis">
            利用学生考试成绩、测评数据开展班级学情研判、短板归因与学情总结分析
          </el-checkbox>

          <el-checkbox label="teaching_interaction_analysis">
            依托课堂授课行为数据、教学互动数据，反思并优化课堂教学流程与授课策略
          </el-checkbox>

          <el-checkbox label="homework_analysis">
            借助作业批阅数据、习题错题统计数据，精准定位学生知识薄弱点，实施分层教学设计
          </el-checkbox>

          <el-checkbox label="class_management">
            运用学生出勤、课堂参与、日常行为表现等记录数据，优化班级管理与个性化育人方式
          </el-checkbox>

          <el-checkbox label="teaching_quality_meeting">
            参加年级、学科组教学质量会，依据成绩、学情等数据分析结果，调整教学进度与教学重难点
          </el-checkbox>

          <el-checkbox label="personal_reflection">
            主动运用平台统计报表、教学相关数据，开展个人教学复盘反思与专业成长总结
          </el-checkbox>

          <el-checkbox label="self_diagnosis">
            依托智能教室、录播教室设备与教学留存数据，开展个人磨课、说课和教学自我诊断
          </el-checkbox>

          <el-checkbox label="other">
            其他
          </el-checkbox>
        </el-checkbox-group>

        <el-input
          v-if="formData.teacher_data_behavior_items.includes('other')"
          v-model="formData.teacher_data_behavior_other"
          type="textarea"
          :rows="2"
          placeholder="请自行补充"
          style="margin-top: 10px"
        />

        <div class="form-tip">
          说明：上述数据相关平台包括国家智慧教育平台、地方（省、市、区县级）智慧教育平台、教学平台、教务系统、校园一卡通等各类服务平台。
        </div>
      </el-form-item>

      <!-- C12 学生数据行为 -->
      <div class="subsection-title">（2）学生数据行为</div>
      <el-form-item>
      <template #label>
        <div class="label-with-hint">
          <span>学校是否为学生提供数字化设备用于学习（如多媒体一体机、电脑、平板等）？</span>
          <el-popover placement="top-start" :width="420" trigger="hover" popper-class="custom-hint-popper">
            <template #reference>
              <span class="hint-tag">填写说明</span>
            </template>
            <div class="hint-body">
              <p class="hint-text">
                数字化学习设备包括多媒体一体机、学生机房计算机、学生平板、移动学习终端等。
              </p>
            </div>
          </el-popover>
        </div>
      </template>

      <el-radio-group v-model="formData.student_device_provision" class="vertical-radio-group">
        <el-radio label="none">未配备数字化学习设备</el-radio>
        <el-radio label="computer_room">仅建有计算机机房，供班级轮流上课使用</el-radio>
        <el-radio label="computer_room_and_terminal">建有计算机机房，又为学生配备其他数字终端</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item>
      <template #label>
        <div class="label-with-hint">
          <span>学校是否为学生开通个人账号，可登录数据相关平台，开展线上学习、习题作答、学业数据查询等活动？</span>
          <el-popover placement="top-start" :width="450" trigger="hover" popper-class="custom-hint-popper">
            <template #reference>
              <span class="hint-tag">填写说明</span>
            </template>
            <div class="hint-body">
              <p class="hint-text">
                说明：若学生无法独立开通个人账号，由家长协助注册、绑定并可正常使用相关平台开展学习与学业查询，同样视为已配备账号，纳入计分范围。
              </p>
            </div>
          </el-popover>
        </div>
      </template>

      <el-radio-group v-model="formData.student_account_status" class="vertical-radio-group">
        <el-radio label="none">未为学生开通账号</el-radio>
        <el-radio label="partial">部分学生开通账号</el-radio>
        <el-radio label="all">全校学生均开通账号</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item>
      <template #label>
        <div class="label-with-hint">
          <span>学生日常学习生活中已常态化实现的数据行为有哪些？</span>
          <el-popover placement="top-start" :width="420" trigger="hover" popper-class="custom-hint-popper">
            <template #reference>
              <span class="hint-tag">填写说明</span>
            </template>
            <div class="hint-body">
              <p class="hint-text">
                说明：上述数据相关平台包括国家智慧教育平台、地方（省、市、区县级）智慧教育平台、教学平台、教务系统、校园一卡通等各类服务平台。
              </p>
            </div>
          </el-popover>
        </div>
      </template>

      <el-checkbox-group
        v-model="formData.student_data_behavior_items"
        class="behavior-checkbox-group"
      >
        <el-checkbox label="class_interaction">
          应用多媒体设备参与课堂互动、答题反馈、成果展示等学习活动
        </el-checkbox>

        <el-checkbox label="online_research">
          利用学校机房电脑、平板自主查阅资料、线上研学等学习活动
        </el-checkbox>

        <el-checkbox label="online_practice">
          依托相关平台完成线上答题、课后练习、自主测评等活动
        </el-checkbox>

        <el-checkbox label="learning_report">
          通过个人平台账号查询学情报告、学习成长档案等数据信息
        </el-checkbox>

        <el-checkbox label="it_course">
          通过信息技术课程或其他课程应用数字化设备提升数据应用能力
        </el-checkbox>

        <el-checkbox label="other">
          其他
        </el-checkbox>
      </el-checkbox-group>

      <el-input
        v-if="formData.student_data_behavior_items.includes('other')"
        v-model="formData.student_data_behavior_other"
        type="textarea"
        :rows="2"
        placeholder="请自行补充"
        style="margin-top: 10px"
      />

              <div class="form-tip">
          说明：上述数据相关平台包括国家智慧教育平台、地方（省、市、区县级）智慧教育平台、教学平台、教务系统、校园一卡通等各类服务平台。
        </div>

    </el-form-item>

        <!-- 2. 数据应用成效 -->
        <div class="section-title">2. 数据应用成效</div>
        
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>2023年至2025年，学校公开发表的与数据赋能教学、管理、评价和教研等相关的成果（如论文、著作等）？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校以单位名义公开发表 / 出版的、主题围绕数据应用相关的论文和著作数量。</p>
                  <p class="hint-example"><em>示例：学校2023年至2025年发表《中小学教育数据应用实践》论文 2 篇，2024 年出版《校园数据治理》著作 1 部，则已发表论文填写「2」，已出版著作填写「1」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <div class="inline-inputs">
            <span>已发表论文</span>
            <el-input-number v-model="formData.published_paper_count" :min="0" :controls="false" />
            <span>篇</span>
            <span style="margin-left: 30px">已出版著作</span>
            <el-input-number v-model="formData.published_book_count" :min="0" :controls="false" />
            <span>部</span>
          </div>
        </el-form-item>

        <!-- 3. 典型案例 -->
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>2023年至2025年，学校利用数据赋能教育教学和校园管理的典型做法或优秀实践入选各级优秀或典型案例、课例的情况？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校数据应用相关成果入选对应级别教育信息化 / 数字化转型优秀或典型案例的数量。</p>
                  <p class="hint-example"><em>示例：学校 2023 年数据应用成果入选国家级典型案例 1 个、省级优秀案例 2 个、市级典型案例 3 个，则国家级填写「1」，省级填写「2」，市级及以下填写「3」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.case_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.case_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.case_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <!-- 4. 荣誉奖励 -->
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>2023年至2025年，学校利用数据赋能教育教学和校园管理的典型做法或优秀实践受到市级及以上荣誉奖励的情况？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校数据应用相关成果获得对应级别官方颁发的荣誉奖励数量。</p>
                  <p class="hint-example"><em>示例：学校 2024 年数据应用成果获国家级教学成果奖 1 项、省级教育创新奖 2 项、市级数字化建设奖 1 项，则国家级填写「1」，省级填写「2」，市级及以下填写「1」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.award_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.award_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.award_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
          <div class="form-tip">
            说明：以上<strong>三个填报题项</strong>的应用成果可包括依托信息化、数字化等形成的数据相关研究成果、获评典型案例、媒体宣传报道及经验交流分享等。
          </div>
        </el-form-item>

        <!-- 5. 媒体宣传 -->
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>2023年至2025年，学校利用数据赋能教育教学和校园管理的典型做法或优秀实践被官方媒体宣传报道的情况？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校数据应用相关成果被对应级别官方媒体（电视台、党报、政府官网等）宣传报道的次数。</p>
                  <p class="hint-example"><em>示例：学校 2023 年数据应用成果被央视报道 1 次、省级教育厅官网报道 2 次、市级教育局公众号报道 3 次，则国家级填写「1」，省级填写「2」，市级及以下填写「3」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.media_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.media_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.media_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <!-- 6. 会议交流 -->
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>2023年至2025年，学校在教育信息化/数字化转型/智慧校园建设会议、活动上作交流发言或经验分享的情况？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校代表在对应级别教育信息化/数字化转型会议、活动中就数据应用相关主题交流发言或分享经验的次数。</p>
                  <p class="hint-example"><em>示例：学校2023年至2025年在国家级数字化转型论坛发言 1 次、2023 年在省级教育信息化会议分享经验 2 次、2024 年在市级交流活动发言 1 次，则国家级填写「1」，省级填写「2」，市级及以下填写「1」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.conference_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.conference_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.conference_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <!-- 7. 公众号发布 -->
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>2023年至2025年，学校通过公众号发布与数据应用相关的教育教学和校园管理的经验分享或创新实践的情况？</span>
              <el-popover placement="top-start" :width="380" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">
                    请填写学校通过新媒体账号（如微信公众号、视频号等）发布数据应用、数字化教学、智慧校园建设、数据赋能管理等相关经验或创新实践的次数。
                  </p>
                  <p class="hint-example">
                    <em>示例：学校公众号在2023年至2025年期间发布了3篇与数据赋能教学或智慧校园建设相关的推文，则填写「3」。</em>
                  </p>
                </div>
              </el-popover>
            </div>
          </template>

          <div class="inline-inputs">
            <span>公众号发布</span>
            <el-input-number
              v-model="formData.public_account_post_count"
              :min="0"
              :controls="false"
            />
            <span>篇</span>
          </div>
        </el-form-item>

        <!-- 8. 参观学习 -->
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>2023年至2025年，其他学校到本校参观学习数据赋能教育教学和校园管理经验的情况？</span>
              <el-popover placement="top-start" :width="300" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">请填写2023年至2025年期间，其他学校到本校参观学习数据赋能教育教学、校园管理或智慧校园建设经验的总次数。单次多所学校来访可计为1次。</p>
                  <p class="hint-example"><em>示例：2023年至2025年有3所学校分批来访学习（计3次），2023 有1批5所学校集体来访（计1次），则其他学校参观学习填写「4」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <div class="inline-inputs">
            <span>其他学校参观学习</span>
            <el-input-number v-model="formData.visit_count" :min="0" :controls="false" />
            <span>次</span>
          </div>
          <div class="form-tip">
            说明：以上<strong>四个填报题项</strong>的应用成果可包括依托信息化、数字化等形成的数据相关研究成果、获评典型案例、媒体宣传报道及经验交流分享等。
          </div>
        </el-form-item>

        <!-- 3. 学生/管理者/教师对数据应用效果的主观评价 -->
        <div class="section-title">教师对数据应用效果的主观评价</div>
        
        <el-alert
          type="success"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <p>该维度将通过问卷调查的方式，了解教师对学校数据应用效果的主观评价。为便于数据采集，问卷（<strong>中小学校数据应用效果调查问卷</strong>）已全部整合到"数据素养评价"板块。</p>
        </el-alert>
      </el-form>
    </el-card>
  </div>
  <!-- 底部页脚 -->
    <footer class="footer">
  <div class="footer-bar">
    <div class="footer-inner">
      <!-- 左侧：LOGO + 文案 -->
      <div class="footer-left">
        <div class="footer-logo">
          <img src="@/assets/images/ila_logo.png" class="logo-img" alt="ILA" /> 
        </div>

        <div class="footer-text">
          <div class="line">
            Copyright © 2026 版权所有：智能学习与评价江苏省产业技术工程化中心
          </div>
          <div class="line">
            邮箱：2020250606@jsnu.edu.cn　
            地址：江苏省徐州市铜山新区上海路101号
          </div>
        </div>
      </div>

      <!-- 右侧：二维码 -->
      <div class="footer-right">
        <img
          src="@/assets/images/Official_Account1.png"
          alt="官方公众号"
          class="footer-qrcode"
        />
      </div>
    </div>
  </div>
</footer>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const assessmentId = computed(() => route.params.id)

const loading = ref(true)
const saving = ref(false)
const formRef = ref(null)
const isReadonly = ref(false)  // 只读模式
const assessmentInfo = ref(null)

// 表单数据
const formData = ref({
  // C11 教师数据行为
  teacher_device_use_freq: null,
  teacher_platform_use_freq: null,
  teacher_data_behavior_items: [],
  teacher_data_behavior_other: '',

  // C12 学生数据行为
  student_device_provision: '',
  student_account_status: '',
  student_data_behavior_items: [],
  student_data_behavior_other: '',

  teacher_login_freq: null,
  student_login_freq: null,
  manager_login_freq: null,
  visit_count: null,
  published_paper_count: null,
  published_book_count: null,
  case_national_count: null,
  case_provincial_count: null,
  case_city_count: null,
  award_national_count: null,
  award_provincial_count: null,
  award_city_count: null,
  media_national_count: null,
  media_provincial_count: null,
  media_city_count: null,
  conference_national_count: null,
  conference_provincial_count: null,
  conference_city_count: null,

  // C22 新增：公众号发布情况
  public_account_post_count: null
})

const isAssessmentExpired = (assessmentData) => {
  if (assessmentData?.check_survey_quality) return false
  const startTime = assessmentData?.started_at || assessmentData?.created_at

  if (!startTime) return false

  const start = new Date(startTime).getTime()

  if (!Number.isFinite(start)) return false

  const expire = start + 120 * 60 * 60 * 1000

  return Date.now() > expire
}

const isAssessmentReadonly = (assessmentData) => {
  if (!assessmentData) return false

  // 只有整份评估最终提交完成，或超过120小时，才进入只读
  return assessmentData.status === 'completed' || isAssessmentExpired(assessmentData)
}

const readonlyTip = computed(() => {
  if (assessmentInfo.value?.status === 'completed') {
    return '评价已完成，当前为只读模式，无法修改数据'
  }

  if (isAssessmentExpired(assessmentInfo.value)) {
    return '本次评估已超过72小时填报期限，当前为只读模式，无法修改数据'
  }

  return ''
})

// 加载数据
const loadData = async () => {
  loading.value = true

  try {
    const token = localStorage.getItem('access_token')

    // 先获取评估状态
    const assessmentResponse = await fetch(`/api/assessments/${assessmentId.value}/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!assessmentResponse.ok) {
      throw new Error('评估信息加载失败')
    }

    const assessmentData = await assessmentResponse.json()

    assessmentInfo.value = assessmentData
    isReadonly.value = isAssessmentReadonly(assessmentData)

    // 获取数据行为数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/behavior/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('数据行为信息加载失败')
    }

    const data = await response.json()
    Object.assign(formData.value, data)

    // 兼容后端旧数据，防止 checkbox-group 的值为 null 导致 includes 报错
    if (!Array.isArray(formData.value.teacher_data_behavior_items)) {
      formData.value.teacher_data_behavior_items = []
    }

    if (!formData.value.teacher_data_behavior_other) {
      formData.value.teacher_data_behavior_other = ''
    }

    if (!Array.isArray(formData.value.student_data_behavior_items)) {
      formData.value.student_data_behavior_items = []
    }

    if (!formData.value.student_data_behavior_other) {
      formData.value.student_data_behavior_other = ''
    }

    if (!formData.value.student_device_provision) {
      formData.value.student_device_provision = ''
    }

    if (!formData.value.student_account_status) {
      formData.value.student_account_status = ''
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 保存数据
const handleSave = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/assessments/${assessmentId.value}/save_behavior/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(formData.value)
    })
    
    if (response.ok) {
      ElMessage.success('保存成功')
    } else {
      throw new Error('保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 返回评估导航页面
const handleBack = () => {
  router.push('/school/assessment')
}

// 自动保存（只读模式下不自动保存）
let autoSaveTimer = null
const startAutoSave = () => {
  if (isReadonly.value) return
  autoSaveTimer = setInterval(() => {
    if (!isReadonly.value) {
      handleSave()
    }
  }, 120000) // 2分钟自动保存一次
}

onMounted(async () => {
  await loadData()
  startAutoSave()
})

onBeforeUnmount(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})
</script>

<style scoped>
.data-behavior-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.behavior-form {
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 30px 0 20px 0;
  padding-left: 0;
  border-left: none;
}

.inline-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.unit {
  margin-left: 10px;
  color: #606266;
}

:deep(.el-form-item) {
  margin-bottom: 34px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  line-height: 1.6;
  white-space: normal;
  word-break: break-word;
  margin-bottom: 8px;
  color: #303133;
}

:deep(.el-form-item__content) {
  flex-wrap: wrap;
}

:deep(.el-input-number) {
  width: 120px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: center;
}

/* 底部页脚 */
/* ===== Footer（深色条，按截图）===== */
.footer {
  margin-top: auto;
  width: 100%;
}

.footer-bar {
  background: #2f3d4a; /* 深蓝灰色背景 */
  padding: 8px 0;    /* 增加上下内边距，让比例更协调 */
}

.footer-inner {
  /* 核心：必须与 header-content 的宽度和对齐逻辑完全一致 */
  max-width: 99%;
  margin: 0 auto;
  padding: 0 20px;    /* 与 header 保持一致的左右内边距 */
  
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
  /* 彻底删除之前的 margin-left: -200px */
}

.footer-logo .logo-img {
  height: 80px;
  width: auto;
  display: block;
}

.footer-text {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;      /* 标准页脚字号 */
  line-height: 1.8;
  text-align: left;
}

.footer-text .line {
  white-space: nowrap; /* 强制不换行，保持整齐 */
}

.footer-right {
  /* 彻底删除之前的 margin-right: -200px */
  display: flex;
  align-items: center;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.footer-qrcode {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  background: #ffffff;
  padding: 3px;
}

.qr-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

/* 标题与提示并列的布局容器 */
.label-with-hint {
  display: flex;
  align-items: center;
  flex-wrap: wrap; /* 如果标题太长，允许提示换行 */
  gap: 10px;
}

/* 填写提示小标签样式 */
.hint-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 10px;
  font-size: 12px;
  color: #409eff;
  background-color: #ecf5ff;
  border: 1px solid #cfe5ff;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap; /* 强制标签不换行 */
  transition: all 0.2s;
  line-height: 1.2;
}

.hint-tag:hover {
  background-color: #409eff;
  color: #ffffff;
}

/* 弹出框内容样式 */
.hint-body {
  padding: 8px 4px;
}

.hint-text {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  margin-bottom: 10px;
}

.hint-example {
  font-size: 13px;
  line-height: 1.5;
  color: #909399;
}

.hint-example em {
  font-style: italic;
}

.subsection-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 18px 0 16px 0;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.behavior-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  line-height: 1.6;
}

.behavior-checkbox-group :deep(.el-checkbox) {
  height: auto;
  align-items: flex-start;
  white-space: normal;
  margin-right: 0;
}

.behavior-checkbox-group :deep(.el-checkbox__label) {
  white-space: normal;
  line-height: 1.6;
}

.form-tip {
  width: 100%;
  margin-top: 14px;
  margin-bottom: 22px;
  padding: 12px 20px;
  background-color: #fdf6ec;
  border-radius: 0;
  font-size: 14px;
  line-height: 1.8;
  color: #e6a23c;
  box-sizing: border-box;
}

.form-tip p {
  margin: 0;
}

/* 单选题纵向排列，并保证左对齐 */
.vertical-radio-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

/* Element Plus 单选项默认有 margin，需要清掉 */
.vertical-radio-group :deep(.el-radio) {
  width: 100%;
  height: auto;
  margin-right: 0;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}

/* 单选文字左对齐，允许长文本换行 */
.vertical-radio-group :deep(.el-radio__label) {
  white-space: normal;
  line-height: 1.6;
  text-align: left;
}

/* 多选题纵向排列，并保证左对齐 */
.behavior-checkbox-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

/* Element Plus 多选项默认有 margin，需要清掉 */
.behavior-checkbox-group :deep(.el-checkbox) {
  width: 100%;
  height: auto;
  margin-right: 0;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}

/* 多选文字左对齐，允许长文本换行 */
.behavior-checkbox-group :deep(.el-checkbox__label) {
  white-space: normal;
  line-height: 1.6;
  text-align: left;
}
</style>
