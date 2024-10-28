/**
 * 知识图谱-开始节点
 */
export const startNode = {
  name: '开始',
  type: 'startNode',
};

/**
 * 知识图谱-场景意图节点
 */
export const sceneNode = {
  name: '场景意图',
  label: '场景意图',
  type: 'opsgptkg_intent',
  attributes: {
    name: '场景意图',
    description: '',
  },
};

/**
 * 知识图谱-操作计划节点
 */
export const operationPlanNode = {
  name: '操作计划',
  type: 'opsgptkg_schedule',
  attributes: {
    name: '操作计划',
    description: '操作计划',
    enable: true,
  },
};
