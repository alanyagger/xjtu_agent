<template>
  <section class="page-layout">
    <!-- 头部（引入公共头部组件） -->
    <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
    </header>
    
    <!-- 主体内容（登录注册表单） -->
    <main class="page-layout-content">
      <section class="starter-content">
        <div class="page-layout-row">
          <div class="auth-container">
            <!-- 背景装饰 -->
            <div class="auth-decoration"></div>
            
            <!-- 主内容区 -->
            <div class="auth-content">
              <!-- 品牌标识 -->
              <div class="auth-brand">
                <h1 class="brand-title">交小荣AI助手</h1>
                <p class="brand-slogan">智能教务，一键触达</p>
              </div>
              
              <!-- 表单卡片 -->
              <div class="auth-card">
                <!-- 选项卡切换 -->
                <div class="auth-tabs">
                  <button 
                    class="auth-tab" 
                    :class="{ 'active': activeTab === 'login' }"
                    @click="activeTab = 'login'"
                  >
                    登录
                  </button>
                  <button 
                    class="auth-tab" 
                    :class="{ 'active': activeTab === 'register' }"
                    @click="activeTab = 'register'"
                  >
                    注册
                  </button>
                </div>
                
                <!-- 表单内容 -->
                <div class="auth-form-container">
                  <!-- 登录表单 -->
                  <div 
                    class="auth-form" 
                    v-show="activeTab === 'login'"
                    :class="{ 'slide-in': activeTab === 'login' }"
                  >
                    <el-form 
                      ref="loginFormRef" 
                      :model="loginForm" 
                      :rules="loginRules" 
                      label-position="top"
                      class="form"
                    >
                      <el-form-item label="学号" prop="username">
                        <el-input 
                          v-model="loginForm.username" 
                          placeholder="请输入学号"
                        >
                          <template #prefix>
                            <font-awesome-icon :icon="faUser" class="input-icon" />
                          </template>
                        </el-input>
                      </el-form-item>
                      
                      <el-form-item label="密码" prop="password">
                        <el-input 
                          v-model="loginForm.password" 
                          type="password" 
                          placeholder="请输入密码"
                        >
                          <template #prefix>
                            <font-awesome-icon :icon="faLock" class="input-icon" />
                          </template>
                        </el-input>
                      </el-form-item>
                      
                      <el-form-item class="form-actions">
                        <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
                        <a href="#" class="forgot-password">忘记密码?</a>
                      </el-form-item>
                      
                      <el-form-item>
                        <el-button 
                          type="primary" 
                          :loading="loginLoading" 
                          @click="handleLogin"
                          class="submit-btn"
                        >
                          登录
                        </el-button>
                      </el-form-item>
                    </el-form>
                    
                    <div class="social-login">
                      <p class="divider"><span>其他登录方式</span></p>
                      <div class="social-buttons">
                        <el-button 
                          type="text" 
                          class="social-btn" 
                          @click="handleSocialLogin('weibo')"
                          aria-label="微博登录"
                        >
                          <font-awesome-icon :icon="faWeibo" />
                        </el-button>
                        <el-button 
                          type="text" 
                          class="social-btn" 
                          @click="handleSocialLogin('wechat')"
                          aria-label="微信登录"
                        >
                          <font-awesome-icon :icon="faWeixin" />
                        </el-button>
                        <el-button 
                          type="text" 
                          class="social-btn" 
                          @click="handleSocialLogin('qq')"
                          aria-label="QQ登录"
                        >
                          <font-awesome-icon :icon="faQq" />
                        </el-button>
                        <el-button 
                          type="text" 
                          class="social-btn" 
                          @click="handleSocialLogin('github')"
                          aria-label="Github登录"
                        >
                          <font-awesome-icon :icon="faGithub" />
                        </el-button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 注册表单 -->
                  <div 
                    class="auth-form" 
                    v-show="activeTab === 'register'"
                    :class="{ 'slide-in': activeTab === 'register' }"
                  >
                    <el-form 
                      ref="registerFormRef" 
                      :model="registerForm" 
                      :rules="registerRules" 
                      label-position="top"
                      class="form"
                    >
                      <el-form-item label="学号" prop="username">
                        <el-input 
                          v-model="registerForm.username" 
                          placeholder="请输入学号"
                        >
                          <template #prefix>
                            <font-awesome-icon :icon="faUser" class="input-icon" />
                          </template>
                        </el-input>
                      </el-form-item>
                      
                      <el-form-item label="邮箱" prop="email">
                        <el-input 
                          v-model="registerForm.email" 
                          placeholder="请输入邮箱"
                        >
                          <template #prefix>
                            <font-awesome-icon :icon="faMail" class="input-icon" />
                          </template>
                        </el-input>
                      </el-form-item>
                      
                      <el-form-item label="密码" prop="password">
                        <el-input 
                          v-model="registerForm.password" 
                          type="password" 
                          placeholder="请输入密码"
                        >
                          <template #prefix>
                            <font-awesome-icon :icon="faLock" class="input-icon" />
                          </template>
                        </el-input>
                      </el-form-item>
                      
                      <el-form-item label="确认密码" prop="confirmPassword">
                        <el-input 
                          v-model="registerForm.confirmPassword" 
                          type="password" 
                          placeholder="请再次输入密码"
                        >
                          <template #prefix>
                            <font-awesome-icon :icon="faLock" class="input-icon" />
                          </template>
                        </el-input>
                      </el-form-item>
                      
                      <el-form-item class="form-actions">
                        <el-checkbox v-model="registerForm.agree">我已阅读并同意<a href="#" class="terms-link">用户协议</a>和<a href="#" class="terms-link">隐私政策</a></el-checkbox>
                      </el-form-item>
                      
                      <el-form-item>
                        <el-button 
                          type="primary" 
                          :loading="registerLoading" 
                          @click="handleRegister"
                          class="submit-btn"
                        >
                          注册
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </section>
</template>

<script setup lang="ts">
import HeaderView from "@/components/HeaderView.vue";
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
// 正确导入FontAwesome图标（注意区分solid和brands分类）
import { faUser, faLock, faMailBulk as faMail } from '@fortawesome/free-solid-svg-icons';
import { faWeibo, faWeixin, faGithub } from '@fortawesome/free-brands-svg-icons';
import { faQq } from '@fortawesome/free-brands-svg-icons'; // QQ图标在brands分类
import { userApi } from '@/api/user'; 
const router = useRouter();

// 导出图标供模板使用
const icons = {
  faUser,
  faLock,
  faMail,
  faWeibo,
  faWeixin,
  faQq,
  faGithub
};

// 表单状态
const activeTab = ref('login');
const loginLoading = ref(false);
const registerLoading = ref(false);

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  remember: false
});

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agree: false
});

// 表单验证规则
const loginRules = reactive({
  username: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^\d+$/, message: '学号必须为数字', trigger: 'blur' } // 新增学号格式验证
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
});

const registerRules = reactive({
  username: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^\d+$/, message: '学号必须为数字', trigger: 'blur' },
    { min: 8, message: '学号长度至少为8位', trigger: 'blur' } // 更严格的学号验证
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d).+$/, message: '密码必须包含字母和数字', trigger: 'blur' } // 增强密码安全性
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (rule: any, value: string, callback: any) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      }, trigger: 'blur' }
  ],
  agree: [
    { required: true, message: '请阅读并同意用户协议', trigger: 'change' }
  ]
});

// 表单引用
const loginFormRef = ref();
const registerFormRef = ref();

// 登录处理
const handleLogin = () => {
  (loginFormRef.value as any)?.validate(async (valid: boolean) => {
    if (valid) {
      loginLoading.value = true;
      try {
        // 调用登录接口（注意：后端/token需要form-data，axios会自动处理）
        const res = await userApi.login({
          username: loginForm.username,
          password: loginForm.password,
        });
        // 存Token到localStorage
        localStorage.setItem('token', res.access_token);
        localStorage.setItem('username', loginForm.username);
        ElMessage.success('登录成功');
        router.push('/LaiChat'); // 跳转到聊天页
      } catch (error) {
        console.error('登录失败', error);
      } finally {
        loginLoading.value = false;
      }
    }
  });
}

// 注册处理
const handleRegister = () => {
  (registerFormRef.value as any)?.validate(async (valid: boolean) => {
    if (valid) {
      registerLoading.value = true;
      try {
        await userApi.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
        });
        ElMessage.success('注册成功，请登录');
        activeTab.value = 'login'; // 切回登录页
      } catch (error:any) {
        const errorDetail = error.response?.data?.detail;
        if(errorDetail?.field === 'username') {
          ElMessage.error('学号已被注册');
        } 
        else if(errorDetail?.field === 'email') {
          ElMessage.error('邮箱已被注册');
        }
        else{
          ElMessage.error('注册失败，请稍后再试');
        }
      } finally {
        registerLoading.value = false;
      }
    }
  });
};

// 社交登录
const handleSocialLogin = (type: string) => {
  ElMessage.info(`正在使用${type}账号登录...`);
  // 实际项目中实现社交登录逻辑
};
</script>

<style lang="scss" scoped>
// 继承公共布局样式
.page-layout {
  display: flex;
  flex-direction: column;
  background: #eee;

  .page-layout-header {
    display: flex;
    justify-content: center;
    min-width: 760px;
    height: 66px;
    background: #fff;
    border-bottom: 1px solid #eee;
    box-shadow: 0 2px 8px 0 rgba(2, 24, 42, 0.1);
  }

  .page-layout-row {
    width: 1440px;
    display: flex;
    background: #fff;
    flex-direction: column;
  }

  .page-layout-content {
    flex: 1;
  }

  .starter-content {
    height: calc(100vh - 66px);
    display: flex;
    justify-content: center;
  }
}

// 登录注册页面样式
.auth-container {
  width: 100%;
  min-height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf2 100%);
  
  // 背景装饰
  .auth-decoration {
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #acc3db 0%, #165dff 100%);
    border-radius: 50%;
    transform: scale(1.5);
    z-index: 0;
    box-shadow: 0 0 50px rgba(64, 158, 255, 0.3);
    animation: float 8s ease-in-out infinite; // 背景浮动动画
  }
  
  // 主内容区
  .auth-content {
    width: 100%;
    max-width: 1200px;
    padding: 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 1;
    
    // 品牌标识
    .auth-brand {
      text-align: center;
      margin-bottom: 40px;
      
      .brand-title {
        font-size: 28px;
        font-weight: 600;
        color: #fff;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
      }
      
      .brand-slogan {
        font-size: 16px;
        color: #606266;
        opacity: 0.8;
      }
    }
    
    // 表单卡片
    .auth-card {
      width: 100%;
      max-width: 400px;
      background-color: #fff;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
      overflow: hidden;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
      }
      
      // 选项卡
      .auth-tabs {
        display: flex;
        border-bottom: 1px solid #ebeef5;
        
        .auth-tab {
          flex: 1;
          padding: 18px 0;
          font-size: 16px;
          font-weight: 500;
          color: #606266;
          background-color: transparent;
          border: none;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            color: #409eff;
          }
          
          &.active {
            color: #165dff;
            font-weight: 600;
            border-bottom: 2px solid #165dff;
          }
        }
      }
      
      // 表单容器
      .auth-form-container {
        padding: 30px 40px;
        
        // 输入框图标
        .input-icon {
          color: #c0c4cc;
          margin-right: 8px;
          font-size: 16px;
        }
        
        // 表单
        .auth-form {
          opacity: 0;
          transform: translateX(30px);
          transition: all 0.4s ease;
          height: 0;
          overflow: hidden;
          
          &.slide-in {
            opacity: 1;
            transform: translateX(0);
            height: auto;
          }
          
          // 表单操作区
          .form-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
          }
          
          .forgot-password {
            position: absolute;
            right: 0; 
            transform: translateX(0);
            color: #409eff;
            font-size: 14px;
            text-decoration: none;
            transition: color 0.2s;
            
            &:hover {
              color: #165dff;
              text-decoration: underline;
            }
          }
          
          // 提交按钮
          .submit-btn {
            width: 100%;
            height: 44px;
            font-size: 16px;
            transition: all 0.3s ease;
            
            &:hover:not(:disabled) {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
            }
            
            &:active:not(:disabled) {
              transform: translateY(0);
            }
          }
        }
        
        // 社交登录
        .social-login {
          margin-top: 30px;
          
          .divider {
            position: relative;
            text-align: center;
            margin-bottom: 20px;
            
            span {
              background-color: #fff;
              padding: 0 10px;
              color: #909399;
              font-size: 14px;
              position: relative;
              z-index: 1;
            }
            
            &::before {
              content: '';
              position: absolute;
              top: 50%;
              left: 0;
              width: 100%;
              height: 1px;
              background-color: #ebeef5;
              z-index: 0;
            }
          }
          
          .social-buttons {
            display: flex;
            justify-content: center;
            
            .social-btn {
              width: 45px;
              height: 45px;
              border-radius: 50%;
              margin: 0 10px;
              display: flex;
              align-items: center;
              justify-content: center;
              transition: all 0.2s ease;
              font-size: 20px; // 图标大小
              
              &:hover {
                transform: scale(1.15);
                background-color: #f5f7fa;
              }
              
              // 社交图标颜色
              &:nth-child(1) { color: #e6162d; } // 微博红
              &:nth-child(2) { color: #07c160; } // 微信绿
              &:nth-child(3) { color: #1da1f2; } // QQ蓝
              &:nth-child(4) { color: #333; }    // Github灰
            }
          }
        }
        
        // 条款链接
        .terms-link {
          color: #409eff;
          text-decoration: none;
          transition: color 0.2s;
          
          &:hover {
            color: #165dff;
            text-decoration: underline;
          }
        }
      }
    }
  }
}

// 背景浮动动画
@keyframes float {
  0%, 100% { transform: scale(1.5) translate(0, 0); }
  50% { transform: scale(1.55) translate(10px, 10px); }
}

// 响应式设计
@media (max-width: 768px) {
  .page-layout {
    .page-layout-header {
      min-width: 100%;
    }
    
    .page-layout-row {
      width: 100%;
    }
  }

  .auth-container {
    .auth-content {
      padding: 20px;
      
      .auth-brand {
        .brand-title {
          font-size: 24px;
        }
        
        .brand-slogan {
          font-size: 14px;
        }
      }
      
      .auth-card {
        max-width: 320px;
      }
    }
  }
}
</style>