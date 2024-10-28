import type { XYPosition } from 'reactflow';

export type ITemplate = {
  type: string;
  name: string;
  attributes?: any;
};

export type IConnectParam = {
  /**
   * 节点id
   */
  nodeId: string;
  /**
   * 来源桩点的索引
   */
  sourceHandleIndex: number;
  /**
   * 节点类型
   */
  type?: string;
  position: XYPosition;
};
