<script setup lang="ts">
import HeaderView from "@/components/HeaderView.vue";
</script>

<template>
  <section class="page-layout">
    <!-- 头部 -->
    <header class="page-layout-header">
      <div class="page-layout-row">
        <!-- 引入公共的头部组件 -->
        <HeaderView />
      </div>
    </header>
    <!-- 主体 -->
    <main class="page-layout-content">
      <section class="starter-content">
        <div class="page-layout-row">
          <RouterView />
        </div>
      </section>
    </main>
  </section>
</template>

<style scoped>
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
</style>
