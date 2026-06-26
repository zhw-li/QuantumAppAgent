# API Rules

## Request instance

Use the existing project request instance:

```text
src/utils/axios.js
```

It handles:

- `VITE_APP_BASE_API`
- `localStorage.Authorization`
- `apiCode` header
- GET parameter serialization
- HTTP 200 unwrapping to `response.data`
- business code `401` login cleanup and redirect

## Prohibited

- Do not `import axios from 'axios'` in pages.
- Do not use `fetch`.
- Do not use `src/utils/request.js`; it points to local port `4000`.
- Do not hardcode full backend domains.
- Do not invent API URLs, request fields, response fields, `apiCode`, or pagination contracts.

## API file template

Only create this file when the user provides real API details.

```js
import axios from '../../utils/axios';

export const getPageData = query => {
  return axios({
    url: '/real/api/path',
    method: 'get',
    params: query,
    headers: {
      apiCode: 'provided-api-code',
    },
  });
};

export const submitPageData = data => {
  return axios({
    url: '/real/api/path',
    method: 'post',
    data,
    headers: {
      apiCode: 'provided-api-code',
    },
  });
};
```

## Page call pattern

```js
const loading = ref(false);
const loadError = ref(false);

const loadData = async () => {
  loading.value = true;
  loadError.value = false;
  try {
    const res = await getPageData({});
    if (res.code === 200) {
      return;
    }
    loadError.value = true;
    ElMessage.error(t('<pageKey>.message.loadFailed'));
  } catch (error) {
    loadError.value = true;
    ElMessage.error(t('<pageKey>.message.networkError'));
  } finally {
    loading.value = false;
  }
};
```

## No real API

If URL, method, parameters, response example, and apiCode are not provided:

- Do not create `src/api/<pageKey>/index.js`.
- Put demo data in `src/views/<module>/<pageKey>/data.js`.
- Keep the page previewable with local data.
- In `INTEGRATE.md`, list the exact functions and fields that should be replaced when the real API is available.
