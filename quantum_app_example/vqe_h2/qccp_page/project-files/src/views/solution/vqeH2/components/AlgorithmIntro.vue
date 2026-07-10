<template>
  <div class="algorithm-intro">
    <div class="intro-container">
      <div class="intro-card">
        <h1 class="intro-title">{{ t('vqeH2.algoIntro.title') }}</h1>
        <p class="intro-description">{{ t('vqeH2.algoIntro.description') }}</p>
        <div class="intro-tags">
          <el-tag
            v-for="tag in tags"
            :key="tag.label"
            class="intro-tag"
            size="large"
            effect="plain"
          >
            {{ tag.label }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const tags = computed(() => [
  { label: t('vqeH2.algoIntro.tagVqe') },
  { label: t('vqeH2.algoIntro.tagH2') },
  { label: t('vqeH2.algoIntro.tagSto3g') }
]);
</script>

<style lang="scss" scoped>
.algorithm-intro {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 40px 0 24px;
}

.intro-container {
  width: 100%;
  max-width: 1440px;
  padding: 0 24px;
}

.intro-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 48px 56px;
  border: 1px solid #dce0eb;
}

.intro-title {
  font-size: 40px;
  font-weight: 700;
  color: #020814;
  margin: 0 0 20px;
  line-height: 1.3;
}

.intro-description {
  font-size: 18px;
  font-weight: 400;
  color: #41464f;
  line-height: 1.7;
  margin: 0 0 28px;
}

.intro-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.intro-tag {
  border-radius: 6px;
  font-size: 14px;
  border-color: #1664ff;
  color: #1664ff;
  background: #f3f7ff;
}
</style>
