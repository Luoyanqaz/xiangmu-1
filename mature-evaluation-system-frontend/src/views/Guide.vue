<template>
  <div class="guide-page">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section" @click="goHome">
          <el-icon :size="32" color="#409eff">
            <School />
          </el-icon>
          <h1 class="system-title">中小学校数据文化成熟度评估监测系统</h1>
        </div>
        <nav class="nav-menu">
          <router-link to="/home" class="nav-item">首页</router-link>
          <router-link to="/about" class="nav-item">关于我们</router-link>
          <router-link to="/culture" class="nav-item">数据文化</router-link>
          <router-link to="/guide" class="nav-item">评估说明</router-link>
          <router-link to="/news" class="nav-item">实践动态</router-link>
          <el-dropdown class="user-dropdown">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ schoolName || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </nav>
      </div>
    </header>

    <!-- 主体内容区 -->
    <main class="main-content">
      <div class="content-container">
        <h2 class="page-title">评估说明</h2>
        <div class="title-underline"></div>
        <p class="page-subtitle">科学评估体系引领学校发展</p>
        
        <div class="guide-content">
          <!-- 左侧：评估维度和流程 -->
          <div class="left-section">
            <!-- 评估维度 -->
            <div class="section-block">
              <h3 class="section-title">评估维度</h3>
              <div class="dimension-list">
                <div class="dimension-item">
                  <span class="dimension-icon">A</span>
                  <span class="dimension-name">数据素养</span>
                </div>
                <div class="dimension-item">
                  <span class="dimension-icon">B</span>
                  <span class="dimension-name">数据制度</span>
                </div>
                <div class="dimension-item">
                  <span class="dimension-icon">C</span>
                  <span class="dimension-name">数据行为</span>
                </div>
                <div class="dimension-item">
                  <span class="dimension-icon">D</span>
                  <span class="dimension-name">数据资产</span>
                </div>
                <div class="dimension-item">
                  <span class="dimension-icon">E</span>
                  <span class="dimension-name">数据技术</span>
                </div>
              </div>
            </div>

            <!-- 评估流程 -->
            <div class="section-block">
              <h3 class="section-title">评估流程</h3>
              <div class="process-list">
                <div class="process-item">
                  <span class="process-number">1</span>
                  <span class="process-text">学校注册并提交评估申请</span>
                </div>
                <div class="process-item">
                  <span class="process-number">2</span>
                  <span class="process-text">在线填写评估问卷与数据采集</span>
                </div>
                <div class="process-item">
                  <span class="process-number">3</span>
                  <span class="process-text">系统自动生成评估报告</span>
                </div>
                <div class="process-item">
                  <span class="process-number">4</span>
                  <span class="process-text">获取评价结果与改进建议</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：成熟度等级 -->
          <div class="right-section">
            <div class="maturity-block">
              <h3 class="maturity-title">成熟度等级</h3>
              
              <div class="maturity-level level-5">
                <div class="level-header">
                  <span class="level-name">初始级 [0.0，1.5)分</span>
                </div>
                <p class="level-description">
                  数据文化处于起步阶段，意识薄弱，培训不足，缺乏专门的数据管理团队和制度，应用零散且缺乏系统性，数据安全存在隐患，数据文化尚未形成。
                </p>
              </div>

              <div class="maturity-level level-4">
                <div class="level-header">
                  <span class="level-name">成长级 [1.5，3.0)分</span>
                </div>
                <p class="level-description">
                  数据文化逐步建立，数据意识有所提升，初步开展数据相关培训，数据管理初步规范，数据应用在部分领域开始探索，数据安全得到一定重视，数据文化处于发展阶段。
                </p>
              </div>

              <div class="maturity-level level-3">
                <div class="level-header">
                  <span class="level-name">成熟级 [3.0，4.0)分</span>
                </div>
                <p class="level-description">
                  数据文化高度成熟，数据意识成为师生共识，数据共享机制建立，数据管理高度规范化、自主化，数据安全与隐私保护处于领先水平，数据文化成为学校核心竞争力。
                </p>
              </div>

              <div class="maturity-level level-2">
                <div class="level-header">
                  <span class="level-name">创新级 [4.0，5.0]分</span>
                </div>
                <p class="level-description">
                  数据文化持续演进，数据意识前瞻，师生共创数据应用新场景，数据管理流程规范完整。反哺学校教育实践，形成可持续的数据生态，成为基础教育领域的数据治理典型。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { School, User, Location, Message } from '@element-plus/icons-vue'

const router = useRouter()

const userInfo = ref({
  username: ''
})

const schoolName = ref('')

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    userInfo.value = JSON.parse(storedUser)
    // 获取学校名称
    schoolName.value = userInfo.value.school_name || userInfo.value.username || '用户'
  }
})

const goHome = () => {
  router.push('/home')
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.guide-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 复用Culture.vue的样式 */
.header {
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.system-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-item {
  color: #606266;
  text-decoration: none;
  font-size: 15px;
  transition: color 0.3s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #409eff;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}

.user-info:hover {
  color: #409eff;
}

.main-content {
  flex: 1;
  padding: 60px 40px 80px;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 60px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  text-align: center;
  margin-bottom: 8px;
}

.title-underline {
  width: 60px;
  height: 4px;
  background-color: #ff9800;
  margin: 0 auto 16px;
  border-radius: 2px;
}

.page-subtitle {
  font-size: 16px;
  color: #909399;
  text-align: center;
  margin-bottom: 50px;
}

/* 评估说明内容 */
.guide-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.left-section {
  flex: 0 0 380px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.right-section {
  flex: 1;
  min-width: 0;
}

.section-block {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

/* 评估维度 */
.dimension-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.dimension-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.dimension-name {
  font-size: 15px;
  color: #303133;
}

/* 评估流程 */
.process-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.process-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.process-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.process-text {
  font-size: 15px;
  color: #303133;
  line-height: 1.6;
}

/* 成熟度等级 */
.maturity-block {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 24px;
}

.maturity-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 24px;
}

.maturity-level {
  margin-bottom: 20px;
  padding: 16px;
  border-radius: 8px;
  background-color: white;
  border-left: 4px solid;
}

.maturity-level:last-child {
  margin-bottom: 0;
}

.level-5 {
  border-left-color: #67c23a;
}

.level-4 {
  border-left-color: #409eff;
}

.level-3 {
  border-left-color: #e6a23c;
}

.level-2 {
  border-left-color: #f56c6c;
}

.level-1 {
  border-left-color: #909399;
}

.level-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.level-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.level-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.level-description {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
  margin: 0;
  text-align: justify;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .guide-content {
    flex-direction: column;
  }

  .left-section {
    flex: 1;
    width: 100%;
  }
}

@media (max-width: 768px) {
  .content-container {
    padding: 40px 24px;
  }

  .page-title {
    font-size: 28px;
  }

  .guide-content {
    gap: 24px;
  }
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

.contact-section {
  flex: 1;
}

.contact-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-details p {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.contact-details .el-icon {
  color: #409eff;
}

.qrcode-section {
  flex-shrink: 0;
}

.qrcode {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
