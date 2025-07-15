import { createRouter, createWebHistory} from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), //部署应用时的基本 URL。他由base 配置项决定
  routes: [
    /** 路由懒加载的方式 **/
    {
      path: "/aiChat",
      name: "aiChat",
      component: () => import("@/views/AiChatView.vue"),
    },
    {
      path: "/LaiChat",
      name: "LaiChat",
      component: () => import("@/views/LAiChatView.vue"),
    },
    // 主页（暂时未用，若匹配到则跳转）
    {
      path: "/",
      name: "home",
      component: () => import("@/views/Dashboard.vue"),
      meta: {
        title: "主页",
      },
    },
    // 登录
    {
      path: "/login",
      name: "login",
      component: () => import('@/views/Login.vue')
    },
    //日历
    {
      path: "/calendar",
      name: "calendar",
      component: () => import('@/views/CalendarView.vue')
    },
    //主页
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import('@/views/Dashboard.vue')
    }
  ],
});

export default router;
