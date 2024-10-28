import dagre from 'dagre';
import { cloneDeep } from 'lodash';
import { customAlphabet } from 'nanoid';
/* 
获取高度信息
*/
const getNodeHeight = (node: any) => {
  if (node.type === 'opsgptkg_analysis' && node.data?.accesscriteria) {
    return 576;
  } else if (node.type === 'opsgptkg_analysis' && !node.data?.accesscriteria) {
    return 424;
  } else if (node.type === 'opsgptkg_task' && node.data?.accesscriteria) {
    return 500;
  }
  return 310;
};
/**
 * 随机生成32位节点id
 * @returns {string}
 */
export function createWorkflowRandom() {
  return customAlphabet(
    '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    32,
  )();
}
/*  
  自动布局
  dagre 数据
*/
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));
export const getLayoutedElements = (nodeValue, edges, functions) => {
  const nodes = cloneDeep(nodeValue);
  const minWidth = 550;
  dagreGraph.setGraph({ rankdir: 'LR' });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: node?.width + 100 || minWidth,
      height: node?.height || getNodeHeight(node),
    });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = 'left';
    node.sourcePosition = 'right';
    node.position = {
      x: nodeWithPosition.x - (node?.width + 100 || minWidth) / 2,
      y: nodeWithPosition.y - (node?.height || getNodeHeight(node)) / 2,
    };

    node.data = {
      ...node.data,
      ...functions,
    };
    return node;
  });
  console.log(nodes, 'nodes++++');
  return { newNodes: nodes, newEdges: edges };
};
/* 
服务端数据转画布数据
*/
export const convertServerDataToGraphData = (
  initialData: any,
  functions: any,
) => {
  const newEdges = initialData.edges?.map((i) => {
    return {
      id: i.startId + i.endId,
      source: i.startId,
      target: i.endId,
    };
  });
  const intialNodes = initialData.nodes.map((i) => {
    return {
      ...i,
      data: { attributes: i.attributes },
    };
  });
  console.log(intialNodes, 'intialNodes');
  const { newNodes } = getLayoutedElements(intialNodes, newEdges, functions);
  return { newNodes, newEdges };
};
/* 
画布数据转服务端数据
*/
export const GraphDataToconvertServerData = (
  data: any,
  oldGraphData: { nodes: any[]; edges: any[] },
) => {
  const newNodes = data.nodes.map((i) => {
    // attributes中的其他数据需要再给后端传过去
    const currentNode = oldGraphData?.nodes?.find((el) => el?.id === i?.id);
    const graphNode = {
      id: i.id,
      type: i.type,
      attributes: {
        ...currentNode?.attributes,
        ...i.data.attributes,
      },
    };
    if (i.data?.accesscriteria) {
      graphNode.attributes.accesscriteria = i.data?.attributes?.accesscriteria;
    }
    return graphNode;
  });
  const newEdges = data.edges.map((i) => {
    // 旧的数据中存在相同的边，只更新sourceHandle，targetHandle，
    // attributes中的其他数据需要再给后端传过去，兼容删除边再添加回来缺少后端返回数据的情况
    const edge = oldGraphData?.edges?.find(
      (el) => el?.startId === i?.source && el?.endId === i?.target,
    );
    const newAttributes = edge?.attributes;
    return {
      startId: i.source,
      endId: i.target,
      attributes: newAttributes,
    };
  });
  return {
    newGraph: {
      nodes: newNodes,
      edges: newEdges,
    },
  };
};
