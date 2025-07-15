<template>
  <div class="container">
    <!-- 视频背景带遮罩层 -->
    <div class="video-overlay"></div>
    <video autoplay muted loop class="background-video">
      <source :src="videoSrc" type="video/mp4">
      您的浏览器不支持视频播放或视频加载失败
    </video>
    
    <!-- 顶部导航栏 -->
    <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
    </header>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <h1>教育<br>向未来而生</h1>
      <p>西交利物浦大学将帮助你成长为一个真正的世界公民，使你具备应对当下日益激烈的竞争和快速变化的环境所必需的知识、技能、能力、品质和韧性。</p>
      <button class="custom-button" @click="handleButtonClick">探索更多</button>
      <!-- 新增的动态箭头指示器 -->
      <div class="scroll-indicator" @click="scrollToNextSection">
        <div class="arrow"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import videoSrc from '@/assets/gittar.mp4'
import HeaderView from "@/components/HeaderView.vue";
import { useRouter } from 'vue-router' // 引入路由钩子

const router = useRouter() // 初始化路由实例

const handleButtonClick = () => {
  console.log('按钮被点击了')
  // 使用路由跳转到指定页面
  router.push({ name: 'aiChat' }) // 跳转到名为'dashboard'的路由
    .catch(error => {
      console.error('路由跳转失败:', error)
      // 可以在这里添加失败提示，如显示一个toast
    })
}

// 新增的滚动函数
const scrollToNextSection = () => {
  const nextSection = document.getElementById('next-section') // 假设下方有id为next-section的部分
  if (nextSection) {
    nextSection.scrollIntoView({ behavior: 'smooth' })
  } else {
    window.scrollBy({ top: window.innerHeight, behavior: 'smooth' })
  }
}
</script>

<style scoped>
.container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(10, 36, 99, 0.4);
  z-index: 1;
}

.background-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.page-layout-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
  transition: background 0.3s ease;
}

.page-layout-header:hover {
  background: rgba(10, 36, 99, 0.95);
}

.scroll-indicator {
  position: absolute;
  bottom: -80px;
  left: 50%;
  transform: translateX(-50%);
  cursor: pointer;
  width: 40px;
  height: 40px;
  animation: bounce 2s infinite;
}

.arrow {
  width: 30px;
  height: 30px;
  border-left: 3px solid rgba(251, 54, 64, 0.8);
  border-bottom: 3px solid rgba(251, 54, 64, 0.8);
  transform: rotate(-45deg);
  margin: 0 auto;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0) translateX(-50%);
  }
  40% {
    transform: translateY(-20px) translateX(-50%);
  }
  60% {
    transform: translateY(-10px) translateX(-50%);
  }
}

.main-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
  z-index: 2;
  width: 90%;
  max-width: 1200px;
  padding: 2rem;
  animation: fadeIn 1s ease-out;
}

.main-content h1 {
  font-size: 3.5rem;
  font-weight: 600;
  margin-bottom: 1.2rem; /* 标题与正文间距微调 */
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  color: #FB3640;
}

.main-content p {
  font-size: 1.2rem;
  line-height: 1.8;
  max-width: 65ch;
  margin: 0 auto 3.5rem; /* 正文与按钮间距从2rem增大到2.5rem */
  color: rgba(255,255,255,0.9);
}

.custom-button {
  background: linear-gradient(135deg, #FB3640 0%, #FF6B6B 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(251, 54, 64, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  margin-top: 1.5rem; /* 按钮顶部额外添加微小间距 */
}


.custom-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(251, 54, 64, 0.4);
}

.custom-button:active {
  transform: translateY(1px);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -40%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .main-content h1 {
    font-size: 2.5rem;
  }
  
  .main-content p {
    font-size: 1rem;
  }
}
</style>