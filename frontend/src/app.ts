import { createGlobalStyle } from '@umijs/max';
import type { RequestConfig } from '@umijs/max';

// ps: 推master要改成localhost
const API_PREFIX = 'http://localhost:8080';
// const API_PREFIX = 'http://30.183.176.221:8080';

export const request: RequestConfig = {
  requestInterceptors: [
    (url, options) => ({ url: `${API_PREFIX}${url}`, options })
  ]

}
// 全局初始化数据配置，用于 Layout 用户信息和权限初始化
// 更多信息见文档：https://umijs.org/docs/api/runtime-config#getinitialstate
// export async function getInitialState(): Promise<{ name: string }> {
//   return { name: '@umijs/max' };
// }

export const styledComponents = {
  GlobalStyle: createGlobalStyle`
html,
body {
  height: 100%;
  background-color: #eceff6;
  margin: 0;
}
* {
  box-sizing: border-box;
}
  `,
};
