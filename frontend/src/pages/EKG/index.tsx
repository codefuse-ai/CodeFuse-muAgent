import { getGraphByTeam, updateGraph } from '@/services/nexa/EkgProdController';
import { MinusOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams, useRequest, useSnapshot } from '@umijs/max';
import { Button, Input, message, Modal } from 'antd';
import { isEqual, throttle } from 'lodash';
import React, { useCallback, useContext, useEffect, useState } from 'react';
import ReactFlow, {
  addEdge,
  Background,
  ConnectionLineType,
  Controls,
  Panel,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { CommonContext, CommonContextType } from './Common';
import EKGHeader from './components/EKGHeader';
import NodeDetailModal from './components/NodeDetailModal';
import SearchNode from './components/SearchNode';
import type { IConnectParam, ITemplate } from './flow';
import OperationPlanNode from './nodes/OperationPlanNode';
import SceneNode from './nodes/SceneNode';
import StartNode from './nodes/StartNode';
import { EKGFlowState } from './store';
import { EKGFlowContainer } from './style';
import {
  calculateNewNodePosition,
  convertGraphDataToServerData,
  convertServerDataToGraphData,
  createWorkflowRandom,
  forceLayout,
} from './utils';

const nodeTypes = {
  startNode: StartNode,
  opsgptkg_intent: SceneNode,
  opsgptkg_schedule: OperationPlanNode,
};

const EKGFlow = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const { setShowChat } = useContext(CommonContext) as CommonContextType;
  // const [zoomLevel, setZoomLevel] = useState(nodes?.length > 2 ? 100 : 70);
  const [zoomLevel, setZoomLevel] = useState(70);

  const { spaceId } = useParams();
  // 旧的图谱数据
  const [oldGraph, setOldGraph] = useState<any>({
    nodes: [],
    edges: [],
  });
  // 记录保存的时间进行头部展示
  const [saveTime, setSaveTime] = useState<string>('');

  const reactFlowInstance = useReactFlow();
  const MIN_ZOOM = 0.2;
  const MAX_ZOOM = 1;

  /**
   * 连接处理
   */
  const onConnect = useCallback(
    (connection: any) => {
      const { source, target, sourceHandle, targetHandle } = connection;
      // 开始节点不能直接连接操作计划节点
      const sourceType = nodes.find((item: any) => item.id === source)?.type;
      const targetType = nodes.find((item: any) => item.id === target)?.type;
      // 相同节点不能连接多次
      const flagEdge = edges?.some(
        (item) => item?.source === source && item?.target === target,
      );
      // 自身节点不能连接自身
      const isSameNode = source === target;
      if (
        (sourceType === 'startNode' && targetType === 'opsgptkg_schedule') ||
        flagEdge ||
        isSameNode
      ) {
        return;
      }
      const newConnection = {
        ...connection,
        type: 'straight',
        id: `${source}_${sourceHandle}_${target}_${targetHandle}`,
      };
      setEdges((oldEdges) => addEdge(newConnection, oldEdges));
    },
    [edges, nodes],
  );

  /**
   * 运行
   */
  const onRun = () => {
    // TODO：打开对话框
    setShowChat(true);
  };
  /**
   * 发布
   */
  const onRelease = () => {};

  /**
   * 开始连线时的回调
   */
  const onConnectStart = (_event: any, params: any) => {
    EKGFlowState.connectStartParams = params;
  };

  /**
   * 结束连线时的回调
   */
  const onConnectEnd = () => {
    EKGFlowState.connectStartParams = undefined;
  };

  /**
   * 桩点连接对应目标的索引
   * @param handleIndex 桩点索引
   * @param nodeType 节点类型
   * @returns 对应的索引
   */
  const getTargetHandleIndex = (handleIndex: number, nodeType?: string) => {
    // 开始节点有8个桩点，顺时针从3点钟方向开始
    // 对应场景意图的4个桩点，0对应2（左桩点），1、2、3对应3（上桩点）4对应0（右桩点）5、6、7对应1（下桩点）
    if (nodeType === 'startNode') {
      switch (handleIndex) {
        case 0:
          return 2;
        case 1:
        case 2:
        case 3:
          return 3;
        case 4:
          return 0;
        default:
          return 1;
      }
    }
    // 其他节点为4个节点，顺时针从3点钟方向开始
    // 连接时反方向一一对应
    switch (handleIndex) {
      case 0:
        return 2;
      case 1:
        return 3;
      case 2:
        return 0;
      case 3:
        return 1;
    }
  };
  console.log(nodes, edges, 'nodes');

  /*
  删除节点
  删除节点时关闭节点详情面板
  */
  const deleteNode = (nodeId: string) => {
    EKGFlowState.nodeDetailOpen = false;
    EKGFlowState.nodeDetailData = {};
    setNodes((nodes) => {
      return nodes.filter((item) => item.id !== nodeId);
    });
    setEdges((edges) => {
      return edges.filter(
        (item) =>
          !item.source.includes(nodeId) && !item.target.includes(nodeId),
      );
    });
  };
  /**
   * 操作计划节点监听删除事件弹出二次确认
   */
  const onShouldNodesChange = (changes: any) => {
    if (changes[0].type === 'remove') {
      setEdges(edges);
      const node = nodes.find((i) => i.id === changes[0].id);
      if (node && node.type === 'opsgptkg_schedule') {
        Modal.confirm({
          title: `确认删除${node.data.attributes.name}节点？`,
          onOk() {
            deleteNode(changes[0].id);
          },
        });
      } else {
        deleteNode(changes[0].id);
      }
    } else {
      onNodesChange(changes);
    }
  };
  // 复制节点
  const copyNode = (nodeId: string) => {
    setNodes((nodes: any[]) => {
      let newNodes;
      nodes.forEach((node) => {
        if (node.id === nodeId) {
          let attributes = {};
          if (node.type === 'opsgptkg_schedule') {
            attributes = {
              name: `${node.data.attributes.name}_copy`,
              description: node.data.attributes.description,
              enable: node.data.attributes?.enable,
            };
          } else {
            attributes = {
              name: `${node.data.attributes.name}_copy`,
              description: node.data.attributes.description,
            };
          }
          newNodes = {
            ...node,
            selected: false,
            id: createWorkflowRandom(),
            data: {
              ...node.data,
              attributes: attributes,
            },
            position: {
              x: node.position.x - 30,
              y: node.position.y + 30,
            },
          };
        }
      });
      return [...nodes, newNodes];
    });
  };

  // 图上节点使用的方法
  const extraNodeFn = {
    setNodes,
    deleteNode,
    copyNode,
  };

  /**
   * 处理服务端返回的边不存在桩点的情况
   * @param data
   */
  const handleEdgesPoint = (serverEdges: any[]) => {
    // 如果果服务端数据没有sourceHandle和targetHandle，则进行默认值设置
    const formatEdges = serverEdges?.map((item: any) => {
      if (!item?.attributes?.sourceHandle && !item?.attributes?.targetHandle) {
        return {
          ...item,
          attributes: {
            ...item.attributes,
            sourceHandle: '0',
            targetHandle: '2',
          },
        };
      }
      return item;
    });
    return formatEdges;
  };

  /**
   * 更新图谱
   */
  const handleUpdateGraph = useRequest(updateGraph, {
    manual: true,
    formatResult: (res) => res,
    onSuccess: (res, params) => {
      if (res?.success) {
        const date = new Date();
        setSaveTime(date?.toLocaleTimeString());
        // 更新图谱后将返回的数据作为oldGraph
        if (res?.data) {
          // 找出根节点id
          const startNodeId = params[0]?.newGraph?.nodes?.find(
            (item) => item?.attributes?.isTeamRoot,
          )?.id;
          const { nodes, edges } = res?.data;
          // 如果果服务端数据没有sourceHandle和targetHandle，则进行默认值设置
          const formatEdges = handleEdgesPoint(edges);
          console.log(res?.data, formatEdges, 'formatEdges');
          // update里的起始节点可能没返回isTeamRoot，这里手动添加，避免新旧数据对比时出现问题
          if (startNodeId) {
            const formatNodes = nodes?.map((item) => {
              if (item?.id === startNodeId) {
                return {
                  ...item,
                  attributes: {
                    ...item.attributes,
                    isTeamRoot: true,
                  },
                };
              } else {
                return item;
              }
            });
            setOldGraph({ nodes: formatNodes, edges: formatEdges });
          } else {
            // 存储一份旧图谱数据
            setOldGraph({ nodes, edges: formatEdges });
          }
        }
      } else {
        message.error(res?.errorMessage);
      }
    },
  });

  /**
   * 保存前参数处理
   */
  const handleSaveBeforeParams = (
    newGraphData: { nodes: any[]; edges: any[] },
    oldGraphData: { nodes: any[]; edges: any[] },
  ) => {
    const newGraph = convertGraphDataToServerData(newGraphData, oldGraphData);
    // 根节点id
    const rootNodeId = newGraph?.nodes?.filter(
      (item) => item?.attributes?.isTeamRoot,
    )[0]?.id;
    const params = {
      teamId: spaceId,
      rootNodeId: rootNodeId,
      oldGraph: oldGraphData,
      newGraph,
    };
    return { params, newGraph };
  };

  /**
   * 保存
   */
  const onSave = async () => {
    const { params } = handleSaveBeforeParams({ nodes, edges }, oldGraph);
    console.log(params, 'server - params');
    handleUpdateGraph?.run(params);
  };

  /**
   * 添加节点
   * @param template 节点数据
   * @param position 位置
   * @param sourceConnectParam 来源节点数据，不传不进行连接
   */
  const addNode = async (
    template: ITemplate,
    sourceConnectParam: IConnectParam,
  ) => {
    const {
      sourceHandleIndex,
      nodeId: sourceNodeId,
      type,
      position,
    } = sourceConnectParam;
    const { currentGraphData, oldGraphData } = EKGFlowState;
    // 来源节点的连接桩索引
    const handleCount = type === 'startNode' ? 8 : 4;
    // 判断是否在同一方向是否已经添加过节点，如果添加过，根据已添加过的节点，延长连线间距
    const currentDirectionNodeCount = currentGraphData?.edges?.filter(
      (item) =>
        item?.source === sourceNodeId &&
        item?.sourceHandle === `${sourceHandleIndex}`,
    )?.length;
    // 节点距离间隔
    const interval = 128 + currentDirectionNodeCount * 64;
    // 根据来源节点坐标计算新节点的位置
    const newPosition = calculateNewNodePosition({
      index: sourceHandleIndex,
      handleCount,
      interval,
      position,
    });
    // 节点id
    const newNodeId = createWorkflowRandom();
    const newNode = {
      id: newNodeId,
      position: newPosition,
      data: {
        ...template,
        addNode,
        setEdges,
        ...extraNodeFn,
      },
      ...template,
    };
    let newNodes: any[] = [];
    let newEdges: any[] = [];
    // 目标节点的连接桩索引
    const targetHandleIndex = getTargetHandleIndex(sourceHandleIndex, type);
    // 新的连接线
    const newEdge = {
      id: `${sourceNodeId}_${sourceHandleIndex}_${newNodeId}_${targetHandleIndex}`,
      source: sourceNodeId,
      sourceHandle: sourceHandleIndex?.toString(),
      target: newNodeId,
      targetHandle: targetHandleIndex?.toString(),
      type: 'straight',
    };
    newNodes = [...currentGraphData?.nodes, newNode];
    newEdges = [...currentGraphData?.edges, newEdge];
    // 先进行保存，避免添加节点后进入子flow没有数据
    const { params } = handleSaveBeforeParams(
      { nodes: newNodes, edges: newEdges },
      oldGraphData,
    );
    console.log(params, 'server - add params');
    console.log(newNodes, 'newNodes');
    console.log(newEdges, 'newEdges');
    const result = await handleUpdateGraph?.run(params);
    // 更新成功后将旧的图谱数据更新为当前进行保存的图谱数据
    if (result?.success) {
      // 保存成功之后更新nodes和edges，进行回显
      setNodes(newNodes);
      setEdges(newEdges);
    }
  };

  /**
   * 获取图谱信息
   */
  const queryGraphDetail = useRequest(getGraphByTeam, {
    manual: true,
    formatResult: (res) => res,
    onSuccess: (res) => {
      if (res?.success) {
        const { nodes, edges } = res?.data || {};
        // 如果果服务端数据没有sourceHandle和targetHandle，则进行默认值设置
        const formatEdges = handleEdgesPoint(edges);
        // 存储一份旧图谱数据
        setOldGraph({ nodes, edges: formatEdges });
        // 将服务端数据进行转换
        const { nodes: newNodes, edges: newEdges } =
          convertServerDataToGraphData(
            { nodes, edges: formatEdges },
            {
              // 图上的一些方法
              ...extraNodeFn,
              addNode,
            },
          );
        console.log(newNodes, newEdges, 'newNodes');
        // 力导布局处理
        forceLayout({ forceEdges: newEdges, forceNodes: newNodes, setNodes });
        setEdges(newEdges);
      } else {
        message.error(res?.errorMessage);
      }
    },
  });

  /**
   * 自动保存操作
   */
  const throttleAutoSave = useCallback(
    throttle(
      async (newGraphData, oldGraphData) => {
        const { params, newGraph } = handleSaveBeforeParams(
          newGraphData,
          oldGraphData,
        );
        console.log(params, 'params - diff');
        console.log(isEqual(newGraph, oldGraphData), 'isEqual - diff');
        // 和上次保存值对比，有变化才进行保存
        if (!isEqual(newGraph, oldGraphData)) {
          handleUpdateGraph?.run(params);
        }
      },
      5000,
      {
        leading: false,
      },
    ),
    [],
  );

  useEffect(() => {
    queryGraphDetail?.run({ teamId: spaceId });
    return () => {
      // 组件卸载时，恢复默认值
      EKGFlowState.currentGraphData = {
        nodes: [],
        edges: [],
      };
      EKGFlowState.oldGraphData = {
        nodes: [],
        edges: [],
      };
      EKGFlowState.nodeDetailOpen = false;
      EKGFlowState.nodeDetailData = {};
      EKGFlowState.knowledgeData = {};
    };
  }, []);

  useEffect(() => {
    EKGFlowState.currentGraphData = {
      nodes,
      edges,
    };
    if (nodes?.length > 0) {
      // 自动保存
      throttleAutoSave({ nodes, edges }, oldGraph);
    }
    console.log(nodes, 'nodes');
    console.log(edges, 'edges');
  }, [JSON.stringify(nodes), JSON.stringify(edges)]);

  useEffect(() => {
    EKGFlowState.oldGraphData = oldGraph;
  }, [oldGraph]);

  const handleZoomOut = () => {
    let newZoomLevel = zoomLevel - 10;
    if (newZoomLevel < MIN_ZOOM * 100) {
      newZoomLevel = MIN_ZOOM * 100;
    }
    setZoomLevel(newZoomLevel);
    reactFlowInstance.zoomTo(newZoomLevel / 100, { duration: 300 });
  };

  const handleZoomIn = () => {
    let newZoomLevel = zoomLevel + 10;
    if (newZoomLevel > MAX_ZOOM * 100) {
      newZoomLevel = MAX_ZOOM * 100;
    }
    setZoomLevel(newZoomLevel);
    reactFlowInstance.zoomTo(newZoomLevel / 100, { duration: 300 });
  };
  const handleFitView = () => {
    reactFlowInstance.fitView();
  };

  return (
    <EKGFlowContainer>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onShouldNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        connectionLineType={ConnectionLineType.Straight}
        onConnectStart={onConnectStart}
        onConnectEnd={onConnectEnd}
      >
        <Background style={{ background: '#e9edf4', zIndex: 1 }} />
        <Panel
          style={{
            width: 'calc(100% - 32px)',
            margin: '16px',
          }}
        >
          <EKGHeader
            onRun={onRun}
            onRelease={onRelease}
            onSave={onSave}
            saveTime={saveTime}
            saveLoading={handleUpdateGraph?.loading}
          />
        </Panel>
        {useSnapshot(EKGFlowState)?.nodeDetailOpen && (
          <Panel
            style={{
              position: 'absolute',
              right: 16,
              top: 88,
            }}
          >
            <NodeDetailModal setNodes={setNodes} />
          </Panel>
        )}
        <Controls
          showZoom={false}
          showFitView={false}
          showInteractive={false}
          className="custom-controls"
          position="bottom-right"
        >
          <div className="zoom-containers">
            <Button
              className="no-border"
              style={{ width: '24px', height: '24px', marginLeft: '8px' }}
              onClick={handleZoomOut}
              icon={<MinusOutlined style={{ color: '#525964' }} />}
            />
            <Input
              className="no-border"
              style={{
                margin: '0 4px',
                width: 60,
                textAlign: 'center',
                fontSize: '14px',
                color: '#1c2533',
              }}
              value={`${zoomLevel}%`}
              readOnly
            />
            <Button
              className="no-border"
              style={{ width: '24px', height: '24px', marginRight: '8px' }}
              onClick={handleZoomIn}
              icon={<PlusOutlined style={{ color: '#525964' }} />}
            />
            <div className="dividing-line"></div>
            <Button
              className="no-border"
              style={{ marginLeft: '8px', width: '24px', height: '24px' }}
              onClick={handleFitView}
              icon={
                <svg
                  viewBox="0 0 1024 1024"
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                >
                  <path
                    d="M594.5 306c68.483 0 124 55.517 124 124v164c0 68.483-55.517 124-124 124h-164c-68.483 0-124-55.517-124-124V430c0-68.483 55.517-124 124-124h164z m0 72h-164c-28.719 0-52 23.281-52 52v164c0 28.719 23.281 52 52 52h164c28.719 0 52-23.281 52-52V430c0-28.719-23.281-52-52-52zM388 111.567c19.882 0 36 16.117 36 36 0 19.882-16.118 36-36 36H236c-28.719 0-52 23.28-52 52v152c0 19.882-16.118 36-36 36s-36-16.118-36-36v-152c0-68.484 55.517-124 124-124h152zM388 911.567c19.882 0 36-16.118 36-36 0-19.883-16.118-36-36-36H236c-28.719 0-52-23.282-52-52v-152c0-19.883-16.118-36-36-36s-36 16.117-36 36v152c0 68.483 55.517 124 124 124h152zM638 911.567c-19.882 0-36-16.118-36-36 0-19.883 16.118-36 36-36h152c28.719 0 52-23.282 52-52v-152c0-19.883 16.118-36 36-36s36 16.117 36 36v152c0 68.483-55.517 124-124 124H638zM638 111.567c-19.882 0-36 16.117-36 36 0 19.882 16.118 36 36 36h152c28.719 0 52 23.28 52 52v152c0 19.882 16.118 36 36 36s36-16.118 36-36v-152c0-68.484-55.517-124-124-124H638z"
                    fill="#525964"
                  ></path>
                </svg>
              }
            />
          </div>
        </Controls>
      </ReactFlow>
      <Panel
        style={{
          position: 'absolute',
          left: 16,
          top: 88,
        }}
      >
        <SearchNode />
      </Panel>
    </EKGFlowContainer>
  );
};

const Flow = (props: any) => {
  return (
    <ReactFlowProvider>
      <EKGFlow {...props} />
    </ReactFlowProvider>
  );
};
export default React.memo(Flow);
