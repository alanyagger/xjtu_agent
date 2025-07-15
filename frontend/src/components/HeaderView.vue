<script lang="ts" setup>
import { useRouter, useRoute } from "vue-router";
import { ChatDotRound, User, ArrowDown } from "@element-plus/icons-vue";
import { ref } from "vue";
import { ElMessage } from "element-plus";

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
const handleLogin = (command?: string) => {
  if (!isLoggedIn.value) {
    // 处理登录逻辑
    router.push("/login"); // 假设登录路由为/login
  }
};
</script>

<template>
  <header class="page-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo区域 - 替换为交小荣logo.svg -->
        <div class="logo-container" @click="logoImgClickHandle">
          <el-image
            src="/logo.png"  
            class="logo-image"
            fit="contain"
            alt="交小荣Logo"
          />
          <!-- 移除原有文字，仅保留logo图片 -->
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
          

        </div>
      </div>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.page-header {
  background-color: rgba($color: #ffffff, $alpha: 0.5);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 12px 0; /* 稍微调整内边距以适应logo尺寸 */
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
  
  // Logo区域 - 调整样式以适应svg logo
  .logo-container {
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: transform 0.2s ease;
    
    &:hover {
      transform: scale(1.02);
    }
    
    .logo-image {
      height: 44px; /* 适当调整logo高度 */
      width: auto;
      // 移除右侧margin，因为不再有文字
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
    .nav-container .nav-item {
      padding: 8px 20px;
    }
  }
}
</style>