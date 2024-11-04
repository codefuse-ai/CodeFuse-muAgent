import { defineConfig } from '@umijs/max';
const mockSpaceId = 1;

export default defineConfig({
  styledComponents: {},
  valtio: {},
  access: {},
  model: {},
  initialState: {},
  request: {},
  layout: false,
  locale: {
    default: 'zh-CN',
    antd: true,
  },
  // proxy: {
  //   '/api': {
  //     // target: 'https://nexa-api-pre.alipay.com',
  //     // target: 'http://30.230.0.179:8080',
  //     target: 'http://runtime:8080',
  //     // target: 'http://30.98.121.212:8083',
  //     changeOrigin: true,
  //   },
  // },
  routes: [
    {
      path: '/',
      redirect: '/space/default/ekg/default',
    },
    {
      path: `/space/:spaceId/ekg/:ekgId`,
      component: './EKG/Common',
      routes: [
        {
          path: '',
          component: './EKG/index',
        },
        {
          path: 'flow/:flowId',
          component: './EKG/Flow/index',
        },
      ],
    },
  ],
  npmClient: 'pnpm',
});
