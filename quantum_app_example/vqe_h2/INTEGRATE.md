# INTEGRATE.md — VQE H2 分子基态能量计算

## 本地 FastAPI 演示

### 启动命令
```bash
cd /code/cqlib_app/vqe_h2 && python -m app.main
```

### 网络合约
- **模式**: single_origin
- **API 基路径**: /api
- **前端服务**: backend_static (同一进程提供 / 和 /api/*)
- **公开地址**: 见 application_manifest.json 的 network.public_base_url

### API 端点合约

端点详情见 `application_manifest.json` 的 `local_demo.endpoints` 字段。

### 验证命令
```bash
cd /code/cqlib_app/vqe_h2 && python -m app.main --check
```

---

## 天衍云页面 (qccp-web)

### 页面信息
- **页面名称**: VQE H2 分子基态能量计算
- **pageKey**: vqeH2
- **模块**: solution
- **路由**: `/solution/vqe-h2`

### 文件复制目标

| 源文件 | 目标路径 (qccp-web 项目内) |
|--------|---------------------------|
| `qccp_page/project-files/src/views/solution/vqeH2/index.vue` | `src/views/solution/vqeH2/index.vue` |
| `qccp_page/project-files/src/views/solution/vqeH2/components/AlgorithmIntro.vue` | `src/views/solution/vqeH2/components/AlgorithmIntro.vue` |
| `qccp_page/project-files/src/views/solution/vqeH2/components/BaselinePanel.vue` | `src/views/solution/vqeH2/components/BaselinePanel.vue` |
| `qccp_page/project-files/src/views/solution/vqeH2/components/VqePanel.vue` | `src/views/solution/vqeH2/components/VqePanel.vue` |
| `qccp_page/project-files/src/views/solution/vqeH2/components/ComparePanel.vue` | `src/views/solution/vqeH2/components/ComparePanel.vue` |
| `qccp_page/project-files/src/api/vqeH2/index.js` | `src/api/vqeH2/index.js` |

### 路由配置 (追加到 qccp-web 路由)
```js
{
  path: '/solution/vqe-h2',
  name: 'VqeH2',
  component: () => import('@/views/solution/vqeH2/index.vue'),
  meta: { title: 'VQE分子基态能量计算' }
}
```

### 中文 i18n (追加)
见 `qccp_page/locales/zh.json`，命名空间 `vqeH2.*`

### 英文 i18n (追加)
见 `qccp_page/locales/en.json`，命名空间 `vqeH2.*`

### API 集成
页面调用相对路径 API（详情见 `application_manifest.json` 的 `qccp_web.api_paths` 字段）。
需要后端代理或 qccp-web 后端转发配置。

### QCIS 电路展示
页面使用 `QcisGraph` 组件（qccp-web 内置）显示 VQE 优化后的量子电路。当 QCIS 数据为空时，电路区域不渲染。

### 使用的现有 npm 依赖
- vue, vue-router, vue-i18n
- element-plus
- echarts (收敛曲线图)

### 验证命令
```bash
npm run build
```

### 登录权限
本页面不需要登录权限。

### 导航入口
建议在天衍云平台"解决方案"导航下添加入口。

---

## 注意事项
- 前端 API 调用使用相对路径，不硬编码 localhost 或 127.0.0.1
- 本地演示和天衍云页面共用同一套 API 后端
- 所有结果为模拟器结果，非真实硬件
