<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <section class="banner-section">
    <div class="banner-inner wrapper">
      <el-tag class="banner-tag" size="small" effect="dark">
        {{ $t('financeQlstm.banner.tag') }}
      </el-tag>
      <h1 class="banner-title">{{ $t('financeQlstm.banner.title') }}</h1>
      <p class="banner-subtitle">{{ $t('financeQlstm.banner.subtitle') }}</p>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.banner-section {
  width: 100%;
  background: linear-gradient(135deg, #1664FF 0%, #4F9DF7 100%);
  padding: 80px 0 60px;
}

.banner-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.banner-tag {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #ffffff;
  font-size: 14px;
  border-radius: 6px;
  padding: 4px 12px;
  margin-bottom: 20px;
}

.banner-title {
  font-size: 40px;
  font-weight: bold;
  color: #ffffff;
  margin: 0 0 16px;
  line-height: 1.3;
}

.banner-subtitle {
  font-size: 20px;
  font-weight: regular;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
  line-height: 1.5;
}
</style>
