<script lang="ts" setup>
import { useRouter, useRoute } from "vue-router";
import { ChatDotRound,  ArrowDown } from "@element-plus/icons-vue";
import { ref } from "vue";
//import { ElMessage } from "element-plus";

const router = useRouter();
const route = useRoute();

// 添加用户名状态
const username = ref(localStorage.getItem('username') || '');


// 判断当前路由是否激活
const isActive = (path: string) => {
  return route.path === path;
};

// 点击logo 的处理
const logoImgClickHandle = () => {
  window.location.href = "https://www.xjtu.edu.cn/";
};

// 点击导航菜单 的处理
const navClickHandle = () => {
  router.push("/aiChat");
};

// 登出处理
const handleLogin = () => {
    // 处理登录逻辑
    router.push("/login");
};
// 页面加载时检查登录状态
// onMounted(() => {
//   // 如果localStorage中有token但没有用户名，尝试获取用户信息
//   if (localStorage.getItem('token') && !localStorage.getItem('username')) {
//     userApi.getCurrentUser()
//       .then(userRes => {
//         username.value = userRes.username;
//         localStorage.setItem('username', userRes.username);
//       })
//       .catch(error => {
//         console.error('获取用户信息失败', error);
//         // 清除无效token
//         localStorage.removeItem('token');
//       });
//   }
// });
</script>

<template>
  <header class="page-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo区域 -->
        <div class="logo-container" @click="logoImgClickHandle">
          <el-image
            src="/logo.png"  
            class="logo-image"
            fit="contain"
            alt="交小荣Logo"
          />
        </div>
        
        <!-- 导航区域 -->
        <nav class="nav-container">
          <span 
            class="nav-item" 
            :class="{ 'active': isActive('/aiChat') }"
          >
            <el-icon class="nav-icon">
              <ChatDotRound />
            </el-icon>
            <span>AI学生教务助手</span>
          </span>
        </nav>
        
        <!-- 登出按钮 -->
        <div class="login-container">          
          <el-dropdown  @command="handleLogin">
            <el-button type="text" class="user-btn">
              <el-avatar size="small" icon="User" />
              <span class="user-name">{{ username }}，您好</span>
              <el-icon class="el-icon--right">
                <ArrowDown />
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.page-header {
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 12px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .logo-container {
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: transform 0.2s ease;
    
    &:hover {
      transform: scale(1.02);
    }
    
    .logo-image {
      height: 44px;
      width: auto;
    }
  }
  
  .nav-container {
    .nav-item {
      display: flex;
      align-items: center;
      padding: 8px 15px;
      border-radius: 6px;
      transition: all 0.2s ease;
      color: #606266;
      
      &:hover {
        background-color: #f5f7fa;
        color: #409eff;
      }
      
      &.active {
        background-color: #e6f4ff;
        color: #165dff;
      }
      
      .nav-icon {
        margin-right: 8px;
        font-size: 18px;
      }
    }
  }
  
  .login-container {
    .login-btn {
      display: flex;
      align-items: center;
      height: 36px;
      border-radius: 6px;
      transition: all 0.2s ease;
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(64, 158, 255, 0.3);
      }
      
      .el-icon {
        margin-right: 5px;
      }
    }
    
    .user-btn {
      display: flex;
      align-items: center;
      color: #606266;
      
      .user-name {
        margin: 0 5px;
        font-weight: 500;
        color: #165dff;
      }
    }
  }
}

@media (min-width: 768px) {
  .page-header {
    .nav-container .nav-item {
      padding: 8px 20px;
    }
  }
}
</style>
