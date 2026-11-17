<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside class="sidebar" width="210px">
      <div class="logo">
        <el-icon :size="24" color="#fff">
          <School />
        </el-icon>
        <span class="logo-text">中小学校数据文化成熟度监测系统</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#2c5f9e"
        text-color="#ffffff"
        active-text-color="#ffffff"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>区校评估概览</span>
        </el-menu-item>

        <el-menu-item index="/admin/applications">
          <el-icon><Document /></el-icon>
          <span>区校账户申请</span>
        </el-menu-item>
        
        <el-menu-item index="/admin/schools">
          <el-icon><School /></el-icon>
          <span>区校账户管理</span>
        </el-menu-item>
        
        <el-menu-item index="/admin/news">
          <el-icon><Promotion /></el-icon>
          <span>区校评估动态</span>
        </el-menu-item>
        
        <el-menu-item index="/admin/reports">
          <el-icon><DataLine /></el-icon>
          <span>区校评估报告</span>
        </el-menu-item>
        <el-menu-item index="/admin/school-type-reports">
          <el-icon><DataAnalysis /></el-icon>
          <span>学校类型评估报告</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <span class="current-page-title">中小学校数据文化成熟度监测系统管理后台</span>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userInfo?.username || '管理员' }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  School,
  DataAnalysis,
  Document,
  DataLine,
  Setting,
  Bell,
  UserFilled,
  Promotion
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const activeMenu = computed(() => route.path)

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中')
      break
    case 'password':
      ElMessage.info('修改密码功能开发中')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
      break
  }
}

onMounted(() => {
  // 如果没有用户信息，获取当前用户信息
  if (!userInfo.value) {
    // TODO: 调用API获取用户信息
  }
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: #f0f2f5;
}

.sidebar {
  background: #2c5f9e;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  color: white;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  font-size: 16px;
  line-height: 1.2;
}

.sidebar-menu {
  border: none;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 4px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2) !important;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  flex: 1;
}

.current-page-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.notification-badge {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #303133;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.footer {
  height: 48px;
  line-height: 48px;
  text-align: center;
  background: white;
  color: #909399;
  font-size: 14px;
  border-top: 1px solid #e4e7ed;
}
</style>
