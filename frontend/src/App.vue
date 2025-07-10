<script setup lang="ts">
</script>

<template>
  <section class="page-layout">
    <!-- 主体内容区域 -->
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

  .page-layout-content {
    flex: 1;
  }

  .starter-content {
    height: 100vh; /* 高度为100vh */
    display: flex;
    justify-content: center;
  }

  .page-layout-row {
    width: 1440px;
    display: flex;
    background: #fff;
    flex-direction: column;
  }
}
</style>