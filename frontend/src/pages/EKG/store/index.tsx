import { proxy } from '@umijs/max';

type NodeDetailProps = {
  type?: 'startNode' | 'operationPlanNode';
  title?: string;
  description?: string;
  [key: string]: any;
  enable?: boolean;
};

type GNodeData = {
  nodes: NEXA_API.GNode[];
};

interface NodeActionListProps {
  type: 'search' | 'select' | '';
  data: GNodeData | NEXA_API.GGraph;
}

interface EKGFlowStateProps {
  currentGraphData: {
    nodes: any[];
    edges: any[];
  };
  oldGraphData: {
    nodes: any[];
    edges: any[];
  };
  connectStartParams?: {
    handleId: string;
    handleType: string;
    nodeId: string;
  };
  nodeDetailOpen: boolean;
  nodeDetailData: NodeDetailProps;
  knowledgeData: NEXA_API.NexaKnowledgeBaseVO;
  nodeActionList: NodeActionListProps;
}

const EKGFlowState = proxy({
  /**
   * 当前画布数据
   */
  currentGraphData: {
    nodes: [],
    edges: [],
  },
  oldGraphData: {
    nodes: [],
    edges: [],
  },
  /**
   * 开始进行连接时，桩点的数据
   */
  connectStartParams: {
    handleId: '',
    handleType: '',
    nodeId: '',
  },
  /**
   * 节点操作面板显隐
   */
  nodeDetailOpen: false,
  /**
   * 节点操作面板数据
   */
  nodeDetailData: {},
  /**
   * 知识库名称、描述等信息
   */
  knowledgeData: {},
  /**
   * 搜索节点数据
   */
  nodeActionList: { type: '', data: {} },
} as EKGFlowStateProps);

export { EKGFlowState, EKGFlowStateProps };
