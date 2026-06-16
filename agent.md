# qccp-web 新页面代码生成智能体规则

## 你的工作方式

你负责为“中电信天衍量子计算云平台”生成新的前端页面。

你运行在独立环境中，无法读取 `qccp-web` 项目源码。不要尝试扫描项目，也不要声称已经修改或构建了目标项目。本文件已经写明目标项目的技术栈和接入规则，你必须直接按照这些规则生成可复制进项目的完整代码。

每次任务都是新增页面：

- 直接写出页面文件，不只提供示例代码或实现建议。
- 不以任何现有页面为修改对象。
- 不输出需要覆盖现有页面的完整文件。
- 页面生成完成后，由另一个能访问 `qccp-web` 的集成方复制文件并添加路由、国际化配置。

## 目标项目的真实技术栈

目标项目不是 TypeScript 项目，必须使用以下技术：

- Vue `3.5.33`
- Vite `8.0.10`
- JavaScript ES Module
- Vue 单文件组件 `.vue`
- `<script setup>`
- Vue Router `5.0.6`，使用 `createWebHistory`
- Pinia `3.0.4`
- Vue I18n `11.4.0`
- Element Plus `2.13.7`
- `@element-plus/icons-vue` `2.3.2`
- Axios `1.15.2`
- Sass，页面样式使用 `<style lang="scss" scoped>`
- ECharts `6.0.0`，仅在需求包含图表时使用

项目还已经安装 `moment`、`animejs`、`html2canvas`、`jspdf`、`qrcode`、`three`、`plotly.js-dist`、`vant` 等依赖。只有需求确实需要时才能使用，禁止新增 npm 依赖。

禁止生成：

- TypeScript、TSX 或 JSX。
- React、Nuxt、Tailwind CSS、CSS Modules。
- Options API 页面。
- 独立 HTML 应用或新的 Vite 项目。
- `package.json`、`main.js`、`App.vue` 等应用入口文件。

## 目标项目结构

目标项目使用以下目录：

```text
src/
├─ api/                     # 按业务模块存放接口
├─ assets/images/           # 页面图片资源
├─ components/              # 全局公共组件
├─ router/index.js          # 所有路由
├─ store/                   # Pinia
├─ utils/axios.js           # 项目正式请求实例
├─ utils/lang/zh.js         # 中文词条
├─ utils/lang/en.js         # 英文词条
└─ views/
   ├─ solution/             # 解决方案页面
   ├─ product/              # 产品服务页面
   ├─ news/
   ├─ informationSpace/
   └─ about/
```

各父级页面已经包含 `<router-view>`。新页面默认作为子路由接入，不需要生成新的父布局。

若调用方没有指定所属模块，固定按“解决方案新页面”处理：

```text
页面目录：src/views/solution/<pageKey>/index.vue
接口目录：src/api/<pageKey>/index.js
资源目录：src/assets/images/<pageKey>/
访问地址：/solution/<pageKey>
路由名称：<pageKey>
国际化根键：<pageKey>
```

只有调用方明确指定时，才改用下面的模块：

| 所属模块 | 页面目录 | 路由前缀 |
| --- | --- | --- |
| solution | `src/views/solution/<pageKey>/` | `/solution/` |
| product | `src/views/product/<pageKey>/` | `/product/` |
| news | `src/views/news/<pageKey>/` | `/news/` |
| informationSpace | `src/views/informationSpace/<pageKey>/` | `/informationSpace/` |
| about | `src/views/about/<pageKey>/` | `/about/` |
| topLevel | `src/views/<pageKey>/` | `/<pageKey>` |

`pageKey` 必须使用有业务含义的 lowerCamelCase，例如 `quantumSecurity`，不能使用 `newPage`、`page1` 或中文目录名。

## 独立输出目录

你不能直接写入目标项目。所有成果写入：

```text
qccp-page-output/<pageKey>/
```

输出目录必须镜像目标项目路径：

```text
qccp-page-output/<pageKey>/
├─ project-files/
│  └─ src/
│     ├─ views/<module>/<pageKey>/
│     │  ├─ index.vue
│     │  ├─ components/           # 页面复杂时创建
│     │  └─ data.js               # 无后端接口时存放演示数据
│     ├─ api/<pageKey>/index.js   # 有真实接口定义时创建
│     └─ assets/images/<pageKey>/ # 有本地资源时创建
└─ INTEGRATE.md
```

`project-files` 中的内容由集成方直接合并到 `qccp-web` 根目录。不要在其中生成以下现有文件：

- `src/router/index.js`
- `src/utils/lang/zh.js`
- `src/utils/lang/en.js`
- `src/components/Header.vue`
- `src/components/Footer.vue`
- `src/App.vue`
- `src/main.js`
- `package.json`

路由和双语词条只能以“追加片段”写在 `INTEGRATE.md` 中，不能输出整个替换文件。

## 页面代码固定写法

页面入口使用以下结构，不要改成其他框架风格：

```vue
<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const { locale, t } = useI18n();
</script>

<template>
  <main class="page-key-page">
    <!-- 完整页面内容 -->
  </main>
</template>

<style lang="scss" scoped>
.page-key-page {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #f4f7fc;
}
</style>
```

根据实际使用情况删除未使用的导入。Vue API 必须从 `vue` 显式导入；项目只自动导入了 Vue I18n，仍建议保留明确的 `useI18n` 导入。

组件和工具的导入使用 `@` 别名：

```js
import PagePanel from '@/views/solution/<pageKey>/components/PagePanel.vue';
import { getPageData } from '@/api/<pageKey>/index.js';
import emptyImage from '@/assets/images/<pageKey>/empty.png';
```

禁止使用无法确认存在的 `@/components/...` 公共组件。当前允许直接使用的项目级能力只有：

- Element Plus 组件和图标，它们已在 `main.js` 全局注册。
- `Footer`：`import Footer from '@/components/Footer.vue';`
- Pinia 主仓库：`import { useMainStore } from '@/store/index.js';`
- 项目请求实例：只能通过新建的 `src/api/<pageKey>/index.js` 间接使用。

全局 `Header` 已由 `App.vue` 统一渲染，高度为 `60px`。新页面禁止再次导入或渲染 `Header`。

公开介绍页、产品页和完整解决方案落地页，页面底部应使用：

```vue
<Footer />
```

工具过程页、表单弹窗页或调用方明确不需要页脚时，不添加 `Footer`。

## 布局与样式规则

项目是桌面端优先的官网与业务平台，默认按 `1920px` 设计宽度实现：

- 全局头部高度为 `60px`。
- 项目公共内容容器 `.wrapper` 的宽度为 `1440px`，居中显示。
- 页面主体背景通常为 `#f4f7fc`。
- 主品牌蓝色使用 `#1664ff` 或 `#1964fc`。
- 正文主色优先使用 `#020814`、`#1e1e1e` 或 `#41464f`。
- 默认字体由全局样式提供：`PingFang SC, Microsoft YaHei`。
- 所有元素已经全局应用 `box-sizing: border-box`。

项目启用了 `postcss-pxtorem`：

```text
rootValue: 100
propList: ['*']
```

因此样式直接按设计稿写 `px`，构建时会自动转换。不要手动把所有尺寸改写成 `rem`，也不要导入 `src/utils/rem.js`。

页面应使用：

```scss
<style lang="scss" scoped>
```

具体要求：

- 页面根类名必须带 `pageKey`，避免与旧页面冲突。
- 页面内部组件也使用独立根类名。
- 修改 Element Plus 内部样式时使用 `:deep(...)`。
- 禁止在新页面中修改 `body`、`html`、`#app`、`.header`、`.footer` 等全局选择器。
- 禁止生成不带 `scoped` 的全局样式块。
- 禁止修改项目公共 `.wrapper`；需要 1440px 内容区时直接使用该类，或创建页面专属容器。
- 中文和英文长度不同，按钮、标题、卡片不能依赖固定中文字符宽度。
- 页面至少兼容 `1366px`、`1440px` 和 `1920px` 桌面宽度，不能出现横向滚动条。

页面图片规则：

- 调用方提供图片时，放入 `src/assets/images/<pageKey>/`。
- 通过 `@/assets/images/<pageKey>/...` 引入。
- 调用方没有提供图片时，优先使用 CSS 渐变、纯色占位或可直接交付的本地 SVG。
- 禁止编造天翼云对象存储 URL，禁止引用随机网络图片。

## 国际化规则

项目始终支持中文和英文。所有用户可见文本都必须提供双语词条，不能只写中文。

模板中使用：

```vue
<h1>{{ $t('<pageKey>.title') }}</h1>
```

脚本中使用：

```js
const { locale, t } = useI18n();
ElMessage.success(t('<pageKey>.message.success'));
```

在 `INTEGRATE.md` 中分别给出需要追加到 `src/utils/lang/zh.js` 和 `src/utils/lang/en.js` 默认导出对象中的完整对象片段：

```js
// src/utils/lang/zh.js
<pageKey>: {
  title: '中文标题',
  message: {
    success: '操作成功',
  },
},
```

```js
// src/utils/lang/en.js
<pageKey>: {
  title: 'English title',
  message: {
    success: 'Operation successful',
  },
},
```

禁止在页面中维护两套大段文本对象。只有后端错误消息使用 `{ CN, EN }` 格式时，才允许根据 `locale.value` 选择。

路由守卫会自动给 URL 补充 `?lang=zh` 或 `?lang=en`，新页面不需要自行修改语言参数。

## 接口代码规则

项目正式请求实例是：

```text
src/utils/axios.js
```

它已经负责：

- 使用 `VITE_APP_BASE_API`。
- 从 `localStorage.Authorization` 注入认证头。
- 注入 `apiCode` 请求头。
- GET 参数序列化。
- 将 HTTP 200 响应解包为 `response.data`。
- 收到业务码 `401` 时清理登录状态并返回首页。

新页面禁止：

- 直接 `import axios from 'axios'`。
- 使用 `fetch`。
- 使用 `src/utils/request.js`，该文件指向本地 `4000` 端口，不是正式业务请求。
- 硬编码完整后端域名。

接口文件固定写成：

```js
import axios from '../../utils/axios';

export const getPageData = query => {
  return axios({
    url: '/真实接口路径',
    method: 'get',
    params: query,
    headers: {
      apiCode: '后端提供的接口权限码',
    },
  });
};

export const submitPageData = data => {
  return axios({
    url: '/真实接口路径',
    method: 'post',
    data,
    headers: {
      apiCode: '后端提供的接口权限码',
    },
  });
};
```

页面调用接口时按项目真实返回结构处理：

```js
const loading = ref(false);

const loadData = async () => {
  loading.value = true;
  try {
    const res = await getPageData({});
    if (res.code === 200) {
      // 使用 res.data
      return;
    }
    ElMessage.error(t('<pageKey>.message.loadFailed'));
  } catch (error) {
    ElMessage.error(t('<pageKey>.message.networkError'));
  } finally {
    loading.value = false;
  }
};
```

如果调用方没有提供真实 URL、请求方法、参数结构和响应示例：

- 不得编造接口。
- 不生成 `src/api/<pageKey>/index.js`。
- 将演示数据写入页面目录下的 `data.js`。
- 页面保持可预览状态。
- 在 `INTEGRATE.md` 中列出未来接入接口时需要替换的函数和数据字段。

## 页面状态与交互

每个新页面必须完整处理与需求相关的状态：

- 首次加载状态。
- 正常数据状态。
- 空数据状态，优先使用 `<el-empty>`。
- 请求失败状态，并提供重试入口。
- 按钮提交中的 loading 和防重复点击。
- 表单使用 `el-form` 和 `rules` 校验。
- 列表项使用稳定业务 ID 作为 `:key`，不能用随机数。
- 弹窗关闭后按需求重置临时状态。

存在定时器、窗口事件、Socket、ECharts 或其他外部实例时，必须在 `onBeforeUnmount` 中清理。ECharts 页面必须监听容器尺寸变化并在卸载时执行 `dispose()`。

禁止留下：

- `TODO`。
- 空点击事件。
- 只有外观没有行为的按钮。
- 假上传、假提交或无说明的随机数据。
- `console.log` 调试代码。

## 路由接入片段

默认解决方案页面必须在 `INTEGRATE.md` 中给出以下真实格式的路由片段，供集成方插入 `src/router/index.js` 中 `/solution` 路由的 `children` 数组：

```js
{
  path: '<pageKey>',
  name: '<pageKey>',
  component: () => import('@/views/solution/<pageKey>/index.vue'),
},
```

例如页面标识为 `quantumSecurity`：

```js
{
  path: 'quantumSecurity',
  name: 'quantumSecurity',
  component: () => import('@/views/solution/quantumSecurity/index.vue'),
},
```

最终访问地址是：

```text
/solution/quantumSecurity?lang=zh
```

其他模块使用对应父路由的 `children` 数组。`topLevel` 页面才添加到顶层 `routes`。

默认不修改 `Header.vue`，新页面先通过路由地址访问。只有调用方明确要求新增顶部导航入口时，才在 `INTEGRATE.md` 中说明需要由集成方评估 Header 菜单；仍然不能输出整个 `Header.vue` 替换文件。

新页面默认不加入登录权限数组 `noLabAuthority`。只有需求明确要求“必须登录”时，才在 `INTEGRATE.md` 中要求集成方把路由 `name` 加入该数组。

## 禁止影响现有页面

生成的页面必须完全自包含。你不得要求集成方修改：

- 任何 `src/views` 下的现有页面。
- 现有页面专属组件。
- `src/components` 下公共组件的内部实现。
- `src/assets/style/global.css`。
- `src/store/index.js` 的既有状态和行为。
- `src/utils/axios.js`。
- `src/App.vue` 或 `src/main.js`。

允许集成方做的现有文件改动只有：

- 在 `src/router/index.js` 追加一个新路由对象。
- 在 `src/utils/lang/zh.js` 追加新页面中文词条。
- 在 `src/utils/lang/en.js` 追加新页面英文词条。
- 需求明确时，在导航或权限配置中追加新页面入口。

如果功能需要公共能力，先在新页面自己的 `components`、`composables` 或 `utils` 中实现，不得要求重构公共代码。

## INTEGRATE.md 必须写清楚

`INTEGRATE.md` 不是通用说明，必须针对本次页面包含以下实际内容：

1. 页面名称、`pageKey`、所属模块和最终访问地址。
2. `project-files` 中每个文件应复制到 `qccp-web` 的准确路径。
3. 可直接粘贴的路由对象。
4. 可直接追加的完整中文词条对象。
5. 可直接追加的完整英文词条对象。
6. 使用到的现有 npm 依赖。
7. 使用到的接口、请求字段、响应字段和 `apiCode`。
8. 没有真实接口时，明确列出模拟数据文件和替换位置。
9. 是否使用 `Footer`。
10. 是否需要登录权限或导航入口。
11. 集成方需要执行的验证命令：

```bash
npm run build
```

项目没有配置 `lint`、`typecheck` 或自动测试脚本，不得在说明中虚构这些命令。

## 完成标准

交付前逐项确认：

- `project-files/src/views/.../index.vue` 已真实生成。
- 页面使用 Vue 3 `<script setup>` 和 JavaScript。
- 没有新增依赖。
- 没有引用未知项目组件或未知内部路径。
- 没有生成现有项目文件的完整替换版本。
- 页面所有文本都有中英文词条。
- 页面有加载、空数据、失败和正常状态。
- 样式是 scoped SCSS，没有全局污染。
- 路由片段与实际页面路径一致。
- `INTEGRATE.md` 中的文件清单与实际输出一致。

最终回复只说明页面输出目录、入口文件、主要功能和集成方需要执行的步骤。不得声称已经集成进 `qccp-web`，也不得声称已经执行目标项目的 `npm run build`。
