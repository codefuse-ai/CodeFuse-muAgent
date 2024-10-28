import { createGlobalStyle } from '@umijs/max';
// 运行时配置

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
