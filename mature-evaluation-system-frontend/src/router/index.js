import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/apply',
      name: 'apply',
      component: () => import('@/views/Apply.vue')
    },
    {
      path: '/apply/success/:id',
      name: 'apply-success',
      component: () => import('@/views/ApplySuccess.vue')
    },
    {
      path: '/apply/status/:id',
      name: 'apply-status',
      component: () => import('@/views/ApplyStatus.vue')
    },
    {
      path: '/apply/check',
      name: 'apply-check',
      component: () => import('@/views/ApplyCheck.vue')
    },
    // 内容页面路由
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/About.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/culture',
      name: 'culture',
      component: () => import('@/views/Culture.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/guide',
      name: 'guide',
      component: () => import('@/views/Guide.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/news',
      name: 'news',
      component: () => import('@/views/News.vue'),
      meta: { requiresAuth: true }
    },
    // 学校用户路由
    {
      path: '/school/basic-info',
      name: 'SchoolBasicInfo',
      component: () => import('@/views/school/SchoolBasicInfo.vue'),
      meta: { title: '基本信息采集', requiresAuth: true }
    },
    {
      path: '/school/dashboard',
      name: 'school-dashboard',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/assessment',
      name: 'school-assessment',
      component: () => import('@/views/school/AssessmentIndex.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/assessment/:id/literacy',
      name: 'school-data-literacy',
      component: () => import('@/views/school/DataLiteracy.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/assessment/literacy',
      name: 'school-data-literacy-auto',
      component: () => import('@/views/school/DataLiteracy.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/assessment/:id/institution',
      name: 'school-data-institution',
      component: () => import('@/views/school/DataInstitution.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/assessment/:id/behavior',
      name: 'school-data-behavior',
      component: () => import('@/views/school/DataBehavior.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/assessment/:id/asset',
      name: 'school-data-asset',
      component: () => import('@/views/school/DataAsset.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/assessment/:id/technology',
      name: 'school-data-technology',
      component: () => import('@/views/school/DataTechnology.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    {
      path: '/school/report/:id',
      name: 'school-report',
      component: () => import('@/views/school/ReportView.vue'),
      meta: { requiresAuth: true, role: 'school' }
    },
    // 公开问卷填写页面（无需登录）
    {
      path: '/survey/:surveyType/:uuid',
      name: 'survey-fill',
      component: () => import('@/views/SurveyFill.vue')
    },
    {
      path: '/school/overview',
      name: 'school-overview',
      component: () => import('@/views/school/AssessmentOverview.vue'),
      meta: { title: '评估概览', requiresAuth: true }
    },
    // 管理员路由
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      redirect: '/admin/dashboard',
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/Dashboard.vue'),
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: 'applications',
          name: 'admin-applications',
          component: () => import('@/views/admin/Applications.vue'),
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: 'schools',
          name: 'admin-schools',
          component: () => import('@/views/admin/Schools.vue'),
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: 'reports',
          name: 'admin-reports',
          component: () => import('@/views/admin/Reports.vue'),
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: 'school-type-reports',
          name: 'admin-school-type-reports',
          component: () => import('@/views/admin/SchoolTypeReport.vue'),
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: 'news',
          name: 'admin-news',
          component: () => import('@/views/admin/NewsManage.vue'),
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: '/admin/region-report-detail',
          name: 'AdminRegionReportDetail',
          component: () => import('@/views/admin/AdminRegionReportDetail.vue'),
          meta: {
            requiresAuth: true,
            roles: ['admin']
          }
        },
        {
          path: '/admin/region-admin/create',
          name: 'AdminCreateRegionAdmin',
          component: () => import('@/views/admin/AdminCreateRegionAdmin.vue'),
          meta: {
            requiresAuth: true,
            roles: ['admin']
          }
        },
      ]
    },
    {
      path: '/region-admin',
      component: () => import('@/views/region-admin/RegionAdminLayout.vue'),
      redirect: '/region-admin/overview',
      meta: { requiresAuth: true, roles: ['region_admin'] },
      children: [
    {
      path: 'overview',
      name: 'RegionAdminOverview',
      component: () => import('@/views/region-admin/Overview.vue'),
      meta: { requiresAuth: true, roles: ['region_admin'] }
    },
    {
      path: 'schools',
      name: 'RegionAdminSchools',
      component: () => import('@/views/region-admin/Schools.vue'),
      meta: { requiresAuth: true, roles: ['region_admin'] }
    },
    {
      path: 'schools/create',
      name: 'RegionAdminSchoolCreate',
      component: () => import('@/views/region-admin/SchoolCreate.vue'),
      meta: { requiresAuth: true, roles: ['region_admin'] }
    },
    {
      path: 'assessments',
      name: 'RegionAdminAssessments',
      component: () => import('@/views/region-admin/Assessments.vue'),
      meta: { requiresAuth: true, roles: ['region_admin'] }
    },
    {
      path: 'assessments/:id',
      name: 'RegionAdminAssessmentDetail',
      component: () => import('@/views/region-admin/AssessmentDetail.vue'),
      meta: { requiresAuth: true, roles: ['region_admin'] }
    },
    {
      path: '/region-admin/school-count',
      component: () => import('@/views/region-admin/SchoolCount.vue'),
      meta: { requiresAuth: true, roles: ['region_admin'] }
    },
    {
      path: "region-report",
      component: () => import("@/views/region-admin/RegionReport.vue"),
      meta: { requiresAuth: true, roles: ['region_admin'] }
    },
  ]
},

  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  
  // 需要认证的路由
  if (to.meta.requiresAuth) {
    if (!token) {
      next('/login')
      return
    }
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (to.path === '/login' && token) {
    next('/home')
    return
  }
  
  next()
})

export default router
