<script lang="ts" setup>
import { useRouter, useRoute } from "vue-router";
import { ChatDotRound, User } from "@element-plus/icons-vue";
import { ref } from "vue";

const router = useRouter();
const route = useRoute();
const isLoggedIn = ref(false); // 示例登录状态

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

// 登录/登出处理
const handleLogin = () => {
  if (isLoggedIn.value) {
    // 处理登出逻辑
    isLoggedIn.value = false;
    ElMessage.success("已成功登出");
  } else {
    // 处理登录逻辑
    router.push("/login"); // 假设登录路由为/login
  }
};
</script>

<template>
  <header class="page-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo区域 -->
        <div class="logo-container" @click="logoImgClickHandle">
          <el-image
            src="https://5b0988e595225.cdn.sohucs.com/images/20190916/577ec8cdff7840918d9d1b03048c7dfd.jpeg"
            class="logo-image"
            fit="contain"
            alt="学校Logo"
          />
          <span class="logo-text">交小荣</span>
        </div>
        
        <!-- 导航区域 -->
        <nav class="nav-container">
          <span 
            class="nav-item" 
            @click="navClickHandle"
            :class="{ 'active': isActive('/aiChat') }"
          >
            <el-icon class="nav-icon">
              <ChatDotRound />
            </el-icon>
            <span>AI学生教务助手</span>
          </span>
        </nav>
        
        <!-- 登录按钮 -->
        <div class="login-container">
          <el-button
            v-if="!isLoggedIn"
            type="primary"
            @click="handleLogin"
            class="login-btn"
          >
            <el-icon><User /></el-icon>
            <span>登录</span>
          </el-button>
          
          <el-dropdown v-else @command="handleLogin">
            <el-button type="text" class="user-btn">
              <el-avatar size="small" icon="User" />
              <span class="user-name">用户名</span>
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
  padding: 15px 0;
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
  
  // Logo区域
  .logo-container {
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: transform 0.2s ease;
    
    &:hover {
      transform: scale(1.02);
    }
    
    .logo-image {
      height: 40px;
      width: auto;
      margin-right: 10px;
    }
    
    .logo-text {
      font-size: 20px;
      font-weight: 600;
      color: #333;
      display: none; // 默认隐藏，在大屏幕显示
    }
  }
  
  // 导航区域
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
  
  // 登录区域
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
      }
    }
  }
}

// 响应式设计
@media (min-width: 768px) {
  .page-header {
    .logo-container .logo-text {
      display: inline-block;
    }
    
    .nav-container .nav-item {
      padding: 8px 20px;
    }
  }
}
</style>