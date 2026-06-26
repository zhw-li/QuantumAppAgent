---
name: qccp-frontend
description: "Guides self-contained Vue 3 page artifacts for the qccp-web TianYan Quantum Computing Cloud Platform frontend and quantum application cloud showcases. Use when creating qccp pages, solution/product/news/about pages, Element Plus Vue SFC pages, bilingual Chinese/English pages, route and i18n integration snippets, or frontend evidence for experiment-pipeline application packaging. Trigger after qccp-ui for visual constraints. Do NOT use for backend/API implementation, cqlib algorithm work, standalone design-only review, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [frontend, qccp, vue, cloud-showcase, application]
---

# qccp-web Frontend Page

Generate a new self-contained page for the CT TianYan Quantum Computing Cloud Platform. The agent usually cannot access the real `qccp-web` repo, so output copyable files under an isolated folder and provide integration snippets.

## When to Use

- User needs a qccp-web compatible Vue 3 SFC page for a quantum application or cloud showcase.
- User needs route snippets, i18n entries, page-local data/API boundary, component structure, or build/integration evidence.
- `experiment-pipeline` Stage 3 needs frontend packaging evidence.

## When NOT to Use

- **Visual token/spec decisions only** -> use `qccp-ui` first.
- **Backend/API/service/deployment implementation** -> use `qccp-service`.
- **Quantum algorithm or report generation** -> use `cqlib-sdk` and algorithm skills.
- **Final staged verification or delivery approval** -> use `experiment-pipeline`.

## Priority rules

1. Read `qccp-ui` before generating or reviewing visual layout, tokens, spacing, radius, typography, or component styling.
2. Follow `agent.md` project facts over generic UI-generation rules when available.
3. Target stack is Vue 3 SFC, JavaScript, `<script setup>`, Element Plus, Vue I18n, scoped SCSS.
4. Do not generate React, TypeScript, JSX/TSX, Nuxt, Tailwind CSS, standalone HTML, or a new Vite project.
5. Do not create or replace app-level files such as `package.json`, `main.js`, `App.vue`, router file, language files, Header, or Footer.
6. Keep Chinese/English switching fully supported. Every visible string must use i18n keys and `INTEGRATE.md` must include complete zh/en entries.
7. Use a vertical top-to-bottom page structure by default: banner/header section, content sections, data/process sections, action/footer section. Avoid left-right split hero layouts unless the request explicitly requires them.

## Output location

Write all generated artifacts to:

```text
qccp-page-output/<pageKey>/
```

Mirror the target project paths inside `project-files`:

```text
qccp-page-output/<pageKey>/
├─ project-files/
│  └─ src/
│     ├─ views/<module>/<pageKey>/
│     │  ├─ index.vue
│     │  ├─ components/
│     │  └─ data.js
│     ├─ api/<pageKey>/index.js
│     └─ assets/images/<pageKey>/
└─ INTEGRATE.md
```

Only create `api/<pageKey>/index.js` when real endpoint details are provided. Otherwise use `data.js`.

## Module defaults

If the user does not specify a module, generate a solution page.

| Module | Page path | Route prefix |
| --- | --- | --- |
| solution | `src/views/solution/<pageKey>/` | `/solution/` |
| product | `src/views/product/<pageKey>/` | `/product/` |
| news | `src/views/news/<pageKey>/` | `/news/` |
| informationSpace | `src/views/informationSpace/<pageKey>/` | `/informationSpace/` |
| about | `src/views/about/<pageKey>/` | `/about/` |
| topLevel | `src/views/<pageKey>/` | `/<pageKey>` |

`pageKey` must be meaningful lowerCamelCase, for example `quantumSecurity`, never `newPage`, `page1`, or Chinese directory names.

## Page file rules

Use this shape and remove unused imports:

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
    <!-- complete page -->
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

Allowed confirmed project-level imports:

```js
import Footer from '@/components/Footer.vue';
import { useMainStore } from '@/store/index.js';
import PagePanel from '@/views/solution/<pageKey>/components/PagePanel.vue';
import { getPageData } from '@/api/<pageKey>/index.js';
```

Do not import unknown shared components. Header is already rendered globally and must not be imported.

## References

Load these only when needed:

- `references/layout-and-style.md`: qccp layout, SCSS, vertical structure, responsive constraints.
- `references/i18n-rules.md`: Chinese/English switching and required i18n snippets.
- `references/api-rules.md`: axios instance and no-fake-interface rules.

## Required states

Implement states relevant to the page:

- loading
- normal data
- empty data using `<el-empty>`
- request failure with retry
- submit loading and duplicate-click prevention
- form validation with `el-form` and `rules`
- cleanup in `onBeforeUnmount` for timers, window listeners, sockets, charts, or 3D scenes

Do not leave TODOs, empty click handlers, fake uploads, fake submits, random network URLs, `console.log`, or visible placeholder text.

## INTEGRATE.md requirements

Include task-specific, copy-pastable content:

1. Page name, `pageKey`, module, final route.
2. Exact copy destinations for every generated file.
3. Route object to append, not the full router file.
4. Complete Chinese i18n object to append.
5. Complete English i18n object to append.
6. Existing npm dependencies used.
7. API URL/method/request/response/apiCode, or state clearly that mock `data.js` is used.
8. Whether `Footer` is used.
9. Whether login permission or nav entry is needed.
10. Verification command: `npm run build`.

Never claim the page has already been integrated into qccp-web.

## Application delivery handoff

For quantum application delivery, frontend work contributes app packaging and verification evidence. In `INTEGRATE.md`, include route path, i18n keys, API/mock boundary, request/response assumptions, and build command so `experiment-pipeline` or backend reviewers can check contract consistency.

Do not decide delivery readiness from this skill. Provide reviewable frontend evidence for the application packaging and verification stages.

## Completion checklist

- [ ] `project-files/src/views/.../index.vue` exists.
- [ ] Vue 3 `<script setup>` uses JavaScript, not TypeScript.
- [ ] All visible text uses i18n keys.
- [ ] zh/en snippets are complete and preserve language switching.
- [ ] No new dependencies.
- [ ] No unknown shared component imports.
- [ ] Styles are scoped SCSS.
- [ ] Layout is mainly top-to-bottom and works at 1366/1440/1920 desktop widths.
- [ ] No generated replacement for existing app-level files.
