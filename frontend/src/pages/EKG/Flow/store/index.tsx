import { proxy } from '@umijs/max';

const EKGChildFlowState = proxy({
  /**
   * 当前画布数据
   */
  currentGraphData: {
    nodes: [],
    edges: [],
    nodeHeaderStatus: false,
    nodeHeaderStatusInfo: {},
  },
} as {
  currentGraphData: {
    nodes: any[];
    edges: any[];
    nodeHeaderStatus?: boolean;
    nodeHeaderStatusInfo?: { [key: string]: any };
  };
});

export { EKGChildFlowState };
