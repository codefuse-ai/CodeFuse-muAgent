// export const startNode = {
//   logo: 'https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*onSLQLtYSzkAAAAAAAAAAAAADprcAQ/original',
//   name: '开始',
//   type: 'startNode',
// };
export const taskNode = {
  logo: 'https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*yAbSSbagshMAAAAAAAAAAAAADprcAQ/original',
  name: '任务执行',
  type: 'opsgptkg_task',
  isVerification: false,
  attributes: {
    executetype: 'onlyTool',
    accesscriteria: '',
    description: '',
  },
};
export const chooseNode = {
  logo: 'https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*kq5pRbKCVdEAAAAAAAAAAAAADprcAQ/original',
  name: '条件分支',
  type: 'opsgptkg_phenomenon',
  isVerification: false,
  attributes: {
    description: '',
  },
};
export const endNode = {
  logo: 'https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*5reDQ6Z-3vIAAAAAAAAAAAAADprcAQ/original',
  name: '结论',
  type: 'opsgptkg_analysis',
  isVerification: false,
  attributes: {
    dsltemplate: '',
    summaryswitch: false,
    accesscriteria: '',
    description: '',
  },
};
export const ChildNodeTemplate = {
  label: '内容生成',
  list: [taskNode, chooseNode, endNode],
};
