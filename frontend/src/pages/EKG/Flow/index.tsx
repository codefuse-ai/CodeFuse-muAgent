import { getGraphByNode, updateGraph } from '@/services/nexa/EkgProdController';
import { ExclamationCircleFilled } from '@ant-design/icons';
import { history, useParams, useRequest } from '@umijs/max';
import { message, Modal } from 'antd';
import { debounce, isEqual, throttle } from 'lodash';
import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import { createWorkflowRandom } from './utils/random';

import type { XYPosition } from 'reactflow';
import ReactFlow, {
  addEdge,
  Background,
  Panel,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useViewport,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { CommonContext, CommonContextType } from '../Common';
import EKGHeader from '../components/EKGHeader';
import AddNodeList from './components/AddNodeList';
import BranchNode from './nodes/BranchNode';
import EndNode from './nodes/EndNode';
import StartNode from './nodes/StartNode';
import TaskNode from './nodes/TaskNode';
import { EKGChildFlowState } from './store';
import { ChildrenFlowContainer } from './style';
import {
  convertServerDataToGraphData,
  // getLayoutedElements,
  GraphDataToconvertServerData,
} from './utils';
import { FlowModuleTemplateType } from './utils/typeFlow';

const nodeTypes = {
  opsgptkg_schedule: StartNode,
  opsgptkg_task: TaskNode,
  opsgptkg_analysis: EndNode,
  opsgptkg_phenomenon: BranchNode,
};
interface IProps {
  flowType: string;
  id: string;
}
const EKGFlow = (props: IProps) => {
  const { setShowChat } = useContext(CommonContext) as CommonContextType;
  const { flowType } = props;
  const { flowId, spaceId, ekgId } = useParams();
  // 旧的图谱数据
  const [oldGraph, setOldGraph] = useState<any>({
    nodes: [],
    edges: [],
  });
  // 记录保存的时间进行头部展示
  const [saveTime, setSaveTime] = useState<string>('');
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const reactFlowWrapper = useRef(null);
  const { x, y, zoom } = useViewport();

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

  const onChangeNode = useCallback(
    debounce(
      ({ id, value, type }: { id: string; value: any; type: string }) => {
        if (type === 'delete') {
          setEdges((edges) => {
            return edges.filter(
              (item) => !item.source.includes(id) && !item.target.includes(id),
            );
          });
        }
        setNodes((nodes) => {
          // 修改节点名字
          if (type === 'editName') {
            return nodes?.map((node) => {
              if (node.id !== id) return node;
              return {
                ...node,
                data: {
                  ...node.data,
                  attributes: {
                    ...node.data.attributes,
                    name: value,
                  },
                },
              };
            });
            // 删除节点
          } else if (type === 'delete') {
            return nodes.filter((item) => item.id !== id);
          }
        });
      },
      500,
    ),
    [setNodes],
  );
  // 复制节点
  const onCopyNode = useCallback(
    ({
      template,
      position,
    }: {
      template: FlowModuleTemplateType;
      position: XYPosition;
    }) => {
      if (!reactFlowWrapper.current) return;
      setNodes((state) => {
        const foundNode = state.find((node) => node.id === template.id);
        foundNode.selected = false;
        if (!foundNode) {
          return state; // 或者根据需要处理未找到的情况
        }
        const newNode = {
          id: createWorkflowRandom(),
          position: { x: position.x, y: position.y },
          selected: true,
          // focusable: true,
          data: {
            ...foundNode.data,
            attributes: {
              ...foundNode.attributes,
              name: template.name,
            },
          },
          type: template.type,
        };
        // 使用扩展运算符创建并返回新数组
        return [...state, newNode];
      });
    },
    [],
  );
  /**
   * 添加节点
   */
  const onAddNode = useCallback(
    ({
      template,
      position,
    }: {
      template: FlowModuleTemplateType;
      position: XYPosition;
    }) => {
      if (!reactFlowWrapper.current) return;
      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const mouseX = (position.x - reactFlowBounds.left - x) / zoom - 100;
      const mouseY = (position.y - reactFlowBounds.top - y) / zoom;
      const id = createWorkflowRandom();

      setNodes((state) => {
        try {
          const newNode = {
            id,
            position: { x: mouseX, y: mouseY },
            positionAbsolute: {
              x: mouseX,
              y: mouseY,
            },
            data: {
              attributes: { name: template.name, ...template.attributes },
              onChangeNode,
              onCopyNode,
              setNodes,
              type: template.type,
            },
            type: template.type,
          };
          return state?.concat?.(newNode);
        } catch (err) {
          console.log('err>>>', err, state);
        }
      });
    },
    [x, zoom, y],
  );
  /**
   * 更新图谱
   */
  const handleUpdateGraph = useRequest(updateGraph, {
    manual: true,
    formatResult: (res) => res,
    onSuccess: (res) => {
      if (res?.success) {
        const date = new Date();
        setSaveTime(date?.toLocaleTimeString());
        if (res?.data) {
          const { nodes, edges } = res?.data || {};
          // 存储一份旧图谱数据
          setOldGraph({ nodes, edges });
        }
      } else {
        message.error(res?.errorMessage);
      }
    },
  });

  /**
   * 获取图谱信息
   */
  const queryGraphDetail = useRequest(getGraphByNode, {
    manual: true,
    formatResult: (res) => res,
    onSuccess: (res) => {
      if (res?.success) {
        const { nodes, edges } = res?.data || {};
        // 存储一份旧图谱数据
        setOldGraph({ nodes, edges });
        // 将服务端数据进行转换
        const { newNodes, newEdges } = convertServerDataToGraphData(
          { nodes, edges },
          {
            onChangeNode,
            onCopyNode,
            setNodes,
          },
        );
        console.log(newNodes, newEdges, 'newNodes');
        setNodes(newNodes);
        setEdges(newEdges);
      } else {
        message.error(res?.errorMessage);
      }
    },
  });
  /**
   * 自动编排
   */
  // const automaticOrchestration = () => {
  //   const { newNodes } = getLayoutedElements(nodes, edges, {
  //     onChangeNode,
  //     onCopyNode,
  //     setNodes,
  //   });
  //   setNodes(newNodes);
  // };
  /**
   * 保存前参数处理
   */
  const handleSaveBeforeParams = (
    newGraphData: { nodes: any[]; edges: any[] },
    oldGraphData: { nodes: any[]; edges: any[] },
  ) => {
    const { newGraph } = GraphDataToconvertServerData(
      newGraphData,
      oldGraphData,
    );
    const params = {
      teamId: spaceId,
      rootNodeId: flowId,
      oldGraph: oldGraphData,
      newGraph,
    };
    return { params, newGraph };
  };

  /**
   * 保存
   */
  const onSave = () => {
    const { params } = handleSaveBeforeParams({ nodes, edges }, oldGraph);
    console.log(params, 'params');
    // automaticOrchestration();
    if (!params.rootNodeId || !params?.teamId) return;
    return handleUpdateGraph?.run(params);
  };

  /**
   * 自动保存操作
   */
  const throttleAutoSave = useCallback(
    throttle(
      (newGraphData, oldGraphData) => {
        const { params, newGraph } = handleSaveBeforeParams(
          newGraphData,
          oldGraphData,
        );
        console.log(params, 'params - diff');
        console.log(isEqual(newGraph, oldGraphData), 'isEqual -- diff');
        if (!params.rootNodeId || !params?.teamId) return;
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

  /**
   * 退出编辑
   */
  const onExitEditing = async () => {
    // 判断节点是否完成必填项的填写
    const notVerification = nodes?.some(
      (item: any) => !item?.data?.attributes?.description,
    );
    // 过滤出除开始节点的ids
    const filterNodeIds = nodes
      ?.filter((item) => item?.type !== 'opsgptkg_schedule')
      ?.map((item) => item.id);
    const filterEdgeTargetIds = edges?.map((item) => item.target);
    // 判断连线是否完整，看节点的输入桩是否有未被连接的
    const notConnected = filterNodeIds?.some((item) => {
      return !filterEdgeTargetIds?.includes(item);
    });
    // 如果存在未完成的，弹窗提示
    if (notVerification || notConnected) {
      Modal.confirm({
        title: '是否要结束编辑？',
        icon: <ExclamationCircleFilled />,
        content: '有节点尚未完成参数填写，会影响最终回答效果，是否要结束编辑',
        okText: '结束编辑',
        async onOk() {
          const result = await onSave();
          history.push(
            `/space/${spaceId}/ekg/${ekgId}${history.location.search}`,
          );
          return result;
        },
      });
    } else {
      await onSave();
      history.push(`/space/${spaceId}/ekg/${ekgId}${history.location.search}`);
    }
  };

  useEffect(() => {
    // 获取图谱数据
    queryGraphDetail?.run({
      nodeId: props.id || flowId,
      nodeType: 'opsgptkg_schedule',
    });
    return () => {
      EKGChildFlowState.currentGraphData.nodeHeaderStatus = false;
      EKGChildFlowState.currentGraphData.nodeHeaderStatusInfo = {};
    };
  }, []);

  /**
   * 连接处理
   */
  const onConnect = useCallback(
    (connection: any) => {
      const { source, target } = connection;
      const sourceType = nodes?.find((item) => item.id === source)?.type;
      const targetType = nodes?.find((item) => item.id === target)?.type;
      // 增加连接限制
      // 1. 不能重复连接
      if (
        edges?.some((item) => item.source === source && item.target === target)
      ) {
        return;
      }
      // 2. 分支节点不能连接分支节点
      if (
        sourceType === 'opsgptkg_phenomenon' &&
        targetType === 'opsgptkg_phenomenon'
      ) {
        message.info('目前暂不支持条件分支后连接条件分支');
        return;
      }
      const newConnection = {
        ...connection,
        // type: 'straight',
        id: connection.source + connection.target,
      };
      setEdges((oldEdges) => addEdge(newConnection, oldEdges));
    },
    [setEdges, nodes, edges],
  );
  useEffect(() => {
    EKGChildFlowState.currentGraphData = {
      ...EKGChildFlowState.currentGraphData,
      nodes,
      edges,
    };
    console.log(nodes, 'nodes---');
    console.log(edges, 'edges---');
    if (nodes?.length > 0 && flowType !== 'chidren') {
      // 触发自动保存
      throttleAutoSave({ nodes, edges }, oldGraph);
    }
  }, [JSON.stringify(nodes), JSON.stringify(edges)]);
  const defaultViewport =
    flowType !== 'chidren'
      ? {
          zoom: 0.8,
          x: 150,
          y: 100,
        }
      : {
          zoom: 0.01,
          x: 150,
          y: 100,
        };
  const MIN_ZOOM = 0.01;
  const MAX_ZOOM = 1;
  return (
    <ChildrenFlowContainer>
      <div
        className="reactflow-wrapper"
        style={{
          width: flowType !== 'chidren' ? '100%' : 332,
          height: flowType !== 'chidren' ? '100%' : 200,
          background: 'white',
        }}
        ref={reactFlowWrapper}
        id="flowWraper"
      >
        <ReactFlow
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodes={nodes}
          edges={edges}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView={true}
          defaultViewport={defaultViewport}
          minZoom={MIN_ZOOM}
          maxZoom={MAX_ZOOM}
        >
          {flowType !== 'chidren' && (
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
                type="children"
                onExitEditing={onExitEditing}
                saveTime={saveTime}
                saveLoading={handleUpdateGraph?.loading}
                childrenTitle={
                  nodes?.find((item) => item?.type === 'opsgptkg_schedule')
                    ?.data?.attributes?.name
                }
              />
            </Panel>
          )}
          {flowType !== 'chidren' && (
            <Panel
              style={{
                width: '152px',
                background: '#f5f7fa',
                borderRadius: '12px',
                border: '1px solid #ffffffcd',
                maxHeight: '588px',
                padding: 0,
                margin: '88px 0px 0px 16px',
                boxSizing: 'border-box',
              }}
            >
              <div>
                <AddNodeList onAddNode={onAddNode} />
              </div>
            </Panel>
          )}
          <Background
            style={{
              background: '#e9edf4',
              borderRadius: flowType !== 'chidren' ? 0 : 8,
            }}
          />
        </ReactFlow>
      </div>
    </ChildrenFlowContainer>
  );
};

const Flow = (data: any) => {
  return (
    <ReactFlowProvider>
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
        }}
        onDragOver={(e) => {
          e.preventDefault();
        }}
      >
        <EKGFlow {...data} />
      </div>
    </ReactFlowProvider>
  );
};
export default React.memo(Flow);
