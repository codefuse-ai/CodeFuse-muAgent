import { IConnectParam, ITemplate } from '@/pages/EKG/flow';
import { operationPlanNode, sceneNode } from '@/pages/EKG/NodeTemplate';
import type { EKGFlowStateProps } from '@/pages/EKG/store';
import { EKGFlowState } from '@/pages/EKG/store';
import { useSearchAncestor } from '@/pages/EKG/utils/nodeAction';
import { useParams, useSnapshot } from '@umijs/max';
import { Menu, Popconfirm, Popover, Space, Spin, Tooltip } from 'antd';
import { debounce } from 'lodash';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Handle, Position } from 'reactflow';
import { SceneNodeWrapper } from './style';

interface IProps {
  id: string;
  data: {
    addNode: (template: ITemplate, connectParam?: IConnectParam) => void;
    [key: string]: any;
  };
  xPos: number;
  yPos: number;
  activeNode: any;
  setActiveNode: any;
}

const SceneNode: React.FC<IProps> = (props) => {
  const [popoverOpenId, setPopoverOpenId] = useState<string>('');
  const [isShowMenu, setIsShowMenu] = useState<boolean>(false);

  const flowSnap = useSnapshot(EKGFlowState) as EKGFlowStateProps;
  const menuRef = useRef<any>(null);

  const { id, data } = props;
  const { addNode, copyNode, deleteNode, attributes } = data;

  const { currentGraphData, nodeActionList } = flowSnap as any;
  const { spaceId } = useParams();
  const { searchAncestor, loading } = useSearchAncestor({
    teamId: spaceId as string,
    nodeId: id,
    nodeType: 'opsgptkg_intent',
  });

  const debouncedHandleSearch = useCallback(debounce(searchAncestor, 600), []);

  const dotPlace = (dotIndex: number) => {
    switch (dotIndex) {
      case 0:
        return 'Right';
      case 1:
        return 'Bottom';
      case 2:
        return 'Left';
      case 3:
        return 'Top';
      default:
        return 'Bottom';
    }
  };

  const searchOrSelectNode = () => {
    // 正常模式，原色
    if (!nodeActionList?.type) {
      return 'normalNodeClass';
    }
    // 搜索模式，扩散动画
    if (nodeActionList?.type === 'search') {
      if (nodeActionList?.data?.nodes?.length > 0) {
        // 匹配到指定节点
        if (
          nodeActionList?.data?.nodes?.some(
            (item: NEXA_API.GNode) => item.id === id,
          )
        ) {
          return 'searchNodeClass';
        }
        // 暗淡非标无操作节点
        return 'noActionNodeClass';
      }
      // 接口无返回值，暗淡无操作节点
      return 'noActionNodeClass';
    }
    // 选择模式，高亮
    if (
      nodeActionList?.type === 'select' &&
      nodeActionList?.data?.nodes?.length > 0
    ) {
      // 匹配选中节点以及链路
      if (
        nodeActionList?.data?.nodes?.some(
          (item: NEXA_API.GNode) => item.id === id,
        )
      ) {
        return 'selectNodeClass';
      }
      // 暗淡非标无操作节点
      return 'noActionNodeClass';
    }
    return 'normalNodeClass';
  };

  const handleAddNode = (handleIndex: number, nodeType: string) => {
    const connectParam: IConnectParam = {
      nodeId: id,
      sourceHandleIndex: handleIndex,
      type: nodeType,
      position: {
        x: props?.xPos,
        y: props?.yPos,
      },
    };
    addNode(
      nodeType === 'sceneNode' ? sceneNode : operationPlanNode,
      connectParam,
    );
  };

  const renderPopoverContent = (itemIndex: number) => (
    <Menu
      items={[
        {
          key: 'sceneNode',
          label: (
            <Space>
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: '#5272e0',
                }}
              />
              <span>场景意图</span>
            </Space>
          ),
        },
        {
          key: 'operationPlanNode',
          label: (
            <Space>
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: '#5dbb30',
                }}
              />
              <span>操作计划</span>
            </Space>
          ),
        },
      ]}
      selectable={false}
      onClick={({ key }) => {
        setPopoverOpenId('');
        handleAddNode(itemIndex, key);
      }}
    />
  );

  const renderDotShow = (dotIndex: string) => {
    const connectFlag = currentGraphData?.edges?.some(
      (item: any) =>
        (item.targetHandle === dotIndex && item.target === id) ||
        (item.sourceHandle === dotIndex && item.source === id),
    );
    return connectFlag;
  };

  const renderConnectHandle = () => {
    return Array.from({ length: 4 }).map((_item, index: number) => (
      <div key={index?.toString()} className="handleWrapper">
        <Popover
          key={index?.toString()}
          content={renderPopoverContent(index)}
          placement="rightTop"
          trigger="click"
          arrow={false}
          open={popoverOpenId === index?.toString()}
          onOpenChange={(e: boolean) => !e && setPopoverOpenId('')}
        >
          <Tooltip title="可点击添加节点/拖动连接节点">
            <Handle
              className={[
                'handleDot',
                renderDotShow(index?.toString()) ? 'showDot' : '',
              ]
                .filter(Boolean)
                .join(' ')}
              id={index?.toString()}
              type="source"
              position={Position[dotPlace(index)]}
              onClick={(e: any) => {
                e.stopPropagation();
                setPopoverOpenId(index?.toString());
              }}
              style={{
                zIndex: 9999,
              }}
            />
          </Tooltip>
        </Popover>
        <Handle
          className="handleDot"
          id={index?.toString()}
          type="target"
          position={Position[dotPlace(index)]}
          style={{ borderColor: 'red', zIndex: 10 }}
        />
      </div>
    ));
  };

  const renderMenuDisabled = () => {
    if (
      currentGraphData?.edges?.find(
        (edgeItem: any) => edgeItem.sourceHandle?.indexOf(id) > -1,
      )
    ) {
      return true;
    }
    return false;
  };

  const customMenu = () => {
    return (
      <div className="menuWrapper" ref={menuRef}>
        <Menu
          items={[
            {
              key: '创建副本',
              label: (
                <div
                  onClick={() => {
                    copyNode(id);
                    setIsShowMenu(false);
                  }}
                >
                  创建副本
                </div>
              ),
            },
            {
              key: '删除',
              label: (
                <Popconfirm
                  onConfirm={() => {
                    deleteNode(id);
                    setIsShowMenu(false);
                  }}
                  title="确定要删除当前节点吗？"
                >
                  <Space>
                    <span style={{ color: '#ff4d4f' }}>删除</span>
                    <div className="deleteText">delete</div>
                  </Space>
                </Popconfirm>
              ),
            },
          ]}
          selectable={false}
        />
      </div>
    );
  };

  const handleClickOutside = (e: any) => {
    if (menuRef.current && !menuRef.current.contains(e.target)) {
      setIsShowMenu(false);
    }
  };

  useEffect(() => {
    window.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    return () => {
      debouncedHandleSearch.cancel();
    };
  }, [debouncedHandleSearch]);

  return (
    <SceneNodeWrapper>
      <div className={searchOrSelectNode()}>
        {searchOrSelectNode() === 'selectNodeClass' && (
          <div className="selectNodeBg" />
        )}
        <Spin spinning={loading} size="small">
          <div
            className="nodeCircle"
            onContextMenu={(e) => {
              e.preventDefault();
              setIsShowMenu(true);
            }}
            onClick={(e) => {
              if (e.currentTarget === e.target) {
                e.stopPropagation();
                EKGFlowState.nodeDetailData.data = {
                  id: id,
                  type: 'opsgptkg_intent',
                  name: attributes?.name,
                  description: attributes?.description,
                };
                EKGFlowState.nodeDetailOpen = true;
                EKGFlowState.nodeActionList = {
                  type: 'select',
                  data: {
                    nodes: [
                      {
                        id: id,
                        type: 'opsgptkg_intent',
                      },
                    ],
                  },
                };
                debouncedHandleSearch();
              }
            }}
          >
            {renderConnectHandle()}
            {isShowMenu && customMenu()}
          </div>
        </Spin>
      </div>
      <div className="nodeTitle">{data?.attributes?.name}</div>
    </SceneNodeWrapper>
  );
};

export default SceneNode;
