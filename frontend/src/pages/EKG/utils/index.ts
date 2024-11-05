import type { SimulationNodeDatum } from 'd3-force';
import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
} from 'd3-force';
import { cloneDeep } from 'lodash';
import { customAlphabet } from 'nanoid';
import { XYPosition } from 'reactflow';

interface CustomNode extends SimulationNodeDatum {
  id: string;
  name: string;
}

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

/**
 * 桩点位置计算，顺时针排列，从3点钟方向开始
 * @param index 桩点索引
 * @param radius 节点圆半径
 * @param handleCount 桩点数量
 * @param handleRadius 圆点半径
 * @returns
 */
export const calculateDotPosition = (params: {
  index: number;
  radius: number;
  handleCount: number;
  handleRadius?: number;
}) => {
  const { index, radius = 32, handleCount, handleRadius = 2 } = params;
  // 每个点之间的弧度
  const angle = ((2 * Math.PI) / handleCount) * index;
  // 减去圆点半径的一半以保证圆点中心对齐
  const x = radius * Math.cos(angle) - handleRadius;
  const y = radius * Math.sin(angle) - handleRadius;
  return { x, y };
};

/**
 * 添加新节点时计算新节点的位置
 * @param {Object} params - 参数对象
 * @param {number} params.index - 桩点索引
 * @param {number} params.handleCount - 桩点数量
 * @param {number} params.interval - 新加节点和原节点间隔
 * @param {XYPosition} params.position - 来源节点坐标信息
 * @returns {XYPosition} - 生成点的坐标
 */
export const calculateNewNodePosition = (params: {
  index: number;
  handleCount: number;
  interval?: number;
  position: XYPosition;
}) => {
  const {
    index,
    handleCount,
    interval = 128,
    position = { x: 0, y: 0 },
  } = params;
  // 每个点之间的弧度
  const angle = ((2 * Math.PI) / handleCount) * index;
  // 计算出偏移距离后，加上来源节点坐标，即为新节点坐标
  const offsetDistance = (Math.random() - 0.5) * 30; // 防止某一方向生成点的坐标，被重叠，加一定程度的偏移量
  const x = interval * Math.cos(angle) + position.x + offsetDistance;
  const y = interval * Math.sin(angle) + position.y + offsetDistance;
  return { x, y };
};
// 安全校验json字符串
export function safeJsonStringify(obj, replacer = null, space = 2) {
  const seen = new WeakSet();

  const customStringify = (value) => {
    if (value !== null && typeof value === 'object') {
      if (seen.has(value)) {
        return '[Circular]'; // 遇到循环引用时返回标记字符串
      }
      seen.add(value);
    }
    return value;
  };
  try {
    return JSON.stringify(
      obj,
      (key, value) => {
        const newValue = customStringify(value);
        return replacer ? replacer(key, newValue) : newValue;
      },
      space,
    );
  } catch (error) {
    console.error('Error: Unable to stringify', error);
    return 'undefined';
  }
}
// 安全解析json字符串
export const safeJsonParse = (jsonString: any) => {
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    console.error('Error during parsing:', error);
    // 如果解析出错，可以选择返回一个错误信息或者默认值
    return 'Error: Unable to parse';
  }
};

/**
 * 过滤掉无效的边，避免出现边的source和target找不到对应的节点数据，导致力导布局解析出错
 * @param edges
 * @param nodes
 */
const filterEdges = (edges: any[], nodes: any[]) => {
  const nodesIds = nodes?.map((item) => item.id);
  return edges?.filter((item) => {
    // 边要能找到对应的输入和输出节点，才算有效边
    return nodesIds?.includes(item?.source) && nodesIds?.includes(item?.target);
  });
};

/**
 * 力导布局
 * @param params
 * @returns
 */
export const forceLayout = (params: {
  forceNodes: any[];
  forceEdges: any[];
  setNodes: any;
}) => {
  try {
    const { forceEdges, forceNodes, setNodes } = params;
    // forceLink方法会改变传入的links，这里拷贝下
    const cloneEdges = cloneDeep(forceEdges);
    const newEdges = filterEdges(cloneEdges, forceNodes);
    const simulation = forceSimulation(forceNodes)
      /**
       * charge用于设置电荷力的强度。强度的值可以为正值或者负值：
       * 负值（如 -200）：表示节点之间存在排斥力。值越负，排斥力越强，节点之间的距离越大。
       * 正值（如 200）：表示节点之间存在吸引力。值越正，吸引力越强，节点之间的距离越小。
       */
      .force('charge', forceManyBody().strength(-1000)) // 电荷力模拟的是节点之间的吸引力或排斥力
      // 连线力模拟的是节点之间的弹簧力，主要作用是通过连接节点的边来保持节点之间的距离。这种力可以使节点保持在一定的距离上，不会过于靠近或远离，从而形成更为合理和美观的布局。
      .force(
        'link',
        forceLink(newEdges)
          .id((d) => (d as CustomNode).id)
          .distance(300),
      )
      // 用于防止节点重叠，通过为每个节点设置一个碰撞半径，使节点之间保持一定的距离。
      .force(
        'collision',
        forceCollide().radius(() => 80),
      )
      // 居中展示
      .force(
        'center',
        forceCenter(window.innerWidth / 2, window.innerHeight / 2),
      )
      .on('tick', () => {
        simulation.stop();
        console.log(simulation.nodes(), 'simulation.nodes()');
        setNodes(
          simulation.nodes().map((item) => {
            return {
              ...item,
              position: { x: item.x as number, y: item.y as number },
            };
          }),
        );
      });
    return simulation;
  } catch (error) {
    console.error(`力导布局解析出错了`, (error as Error).message);
  }
};

/**
 * 将画布数据转换为服务端数据
 */
export function convertGraphDataToServerData(
  // 当前画布数据
  graphData: {
    nodes: any[];
    edges: any[];
  },
  // 旧画布数据
  oldGraphData: {
    nodes: any[];
    edges: any[];
  },
) {
  try {
    const { nodes, edges } = graphData;
    // 将画布的节点数据转换为服务端数据
    const serverNodes = nodes?.map((item) => {
      // attributes中的其他数据需要再给后端传过去
      const currentNode = oldGraphData?.nodes?.find(
        (el) => el?.id === item?.id,
      );
      return {
        type: item?.type === 'startNode' ? 'opsgptkg_intent' : item?.type,
        id: item?.id,
        attributes: {
          ...currentNode?.attributes,
          ...item?.data?.attributes,
        },
      };
    });
    // 将画布的边数据转换为服务端数据
    const serverEdges = edges?.map((item) => {
      const {
        source,
        target,
        sourceHandle,
        targetHandle,
        attributes = {},
      } = item || {};
      // 旧的数据中存在相同的边，只更新sourceHandle，targetHandle，
      // attributes中的其他数据需要再给后端传过去，兼容删除边再添加回来缺少后端返回数据的情况
      const edge = oldGraphData?.edges?.find(
        (el) => el?.startId === source && el?.endId === target,
      );
      const newAttributes = edge?.attributes || attributes;
      return {
        startId: source,
        endId: target,
        attributes: {
          ...newAttributes,
          sourceHandle,
          targetHandle,
        },
      };
    });
    return {
      nodes: serverNodes,
      edges: serverEdges,
    };
  } catch (error) {
    console.error(`图谱数据解析为服务端数据出错了`, (error as Error).message);
    return {
      nodes: [],
      edges: [],
    };
  }
}

/**
 * 将服务端数据转换为图谱数据
 * @param baseConfig
 * @param extraFlowFn
 * @returns
 */
export function convertServerDataToGraphData(
  graphData: { nodes: any[]; edges: any[] },
  extraFlowFn: any,
) {
  try {
    const { nodes, edges } = graphData;
    // 将服务端节点数据转换为图谱节点数据
    const graphNodes = nodes?.map(
      (item: {
        attributes: { isTeamRoot: boolean };
        type: string;
        id: string;
      }) => {
        const { attributes, type, id } = item;
        return {
          id,
          // 开始节点在后端看来也属于场景节点，这里判断isTeamRoot为true则为开始根节点
          type: attributes?.isTeamRoot ? 'startNode' : type,
          // 开始节点不允许删除
          deletable: !attributes?.isTeamRoot,
          data: {
            // 图上的一些方法
            ...extraFlowFn,
            // 节点的属性信息
            attributes,
          },
        };
      },
    );
    // 将服务端边数据转换为图谱边数据
    const graphEdges = edges?.map((item) => {
      const { startId, endId, attributes } = item;
      return {
        // 后端不存储该字段，使用节点信息拼接
        id: `${startId}_${attributes?.sourceHandle}_${endId}_${attributes?.targetHandle}`,
        source: startId,
        target: endId,
        sourceHandle: attributes?.sourceHandle,
        targetHandle: attributes?.targetHandle,
        attributes,
        type: 'straight',
      };
    });
    return {
      nodes: graphNodes,
      edges: graphEdges,
    };
  } catch (error) {
    console.error(`服务端数据解析为图谱数据出错了`, (error as Error).message);
    return {
      nodes: [],
      edges: [],
    };
  }
}
