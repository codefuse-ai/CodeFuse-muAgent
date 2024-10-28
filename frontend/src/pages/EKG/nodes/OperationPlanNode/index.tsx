import { EKGFlowState } from '@/pages/EKG/store';
import { calculateDotPosition } from '@/pages/EKG/utils';
import { useSearchAncestor } from '@/pages/EKG/utils/nodeAction';
import { useParams, useSnapshot } from '@umijs/max';
import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import { Flex, Menu, Popconfirm, Spin, Tooltip } from 'antd';
import { debounce } from 'lodash';
import React from 'react';
import { Handle, Position } from 'reactflow';
import { StartNodeWrapper } from './style';

interface IProps {
  id: string;
  data: {
    name: string;
    enable: boolean;
    description: string;
    copyNode: (nodeId: string) => void;
    deleteNode: (nodeId: string) => void;
    attributes: any;
  };
  xPos: number;
  yPos: number;
}

const OperationPlanNode: React.FC<IProps> = (props) => {
  const { id, data } = props;
  const { deleteNode, attributes } = data;
  const [isShowMenu, setIsShowMenu] = useState<boolean>(false);
  const menuRef = useRef<any>(null);
  // 图谱数据
  const flowSnap = useSnapshot(EKGFlowState);
  const { connectStartParams, currentGraphData, nodeActionList } = flowSnap;
  const { spaceId } = useParams();
  const { searchAncestor, loading } = useSearchAncestor({
    teamId: spaceId as string,
    nodeId: id,
    nodeType: 'opsgptkg_schedule',
  });
  const debouncedHandleSearch = useCallback(debounce(searchAncestor, 600), []);

  /**
   * 连接桩是否展示
   */
  const isShowHandle = (handleId: string) => {
    // 当前桩点是否被连接
    const connectFlag = currentGraphData?.edges?.some((item) => {
      return item.target === id && item.targetHandle === handleId;
    });
    // 展示全部
    // 正在进行连接的桩点
    // edges中已经连接过的桩点
    console.log(
      'connectStartParams',
      connectStartParams,
      connectStartParams?.nodeId,
      connectStartParams?.handleId === handleId,
      connectFlag,
    );
    return (
      connectStartParams?.nodeId ||
      connectStartParams?.handleId === handleId ||
      connectFlag
    );
  };

  /* 
  是否命中搜索展示扩散动画
  */
  const isMatchSearch = () => {
    if (nodeActionList?.type === 'search') {
      if (nodeActionList?.data?.nodes?.length > 0) {
        // 匹配到指定节点
        if (
          nodeActionList?.data?.nodes?.some(
            (item: NEXA_API.GNode) => item.id === id,
          )
        ) {
          if (attributes?.enable) {
            return 'greenContainer container';
          }
          return 'greyContainer container';
        }
      }
      return 'container';
    }
  };
  /*
 是否命中搜索展示
 是否选中当前节点
 高亮节点暗淡其他未命中节点
 */
  const isNodeHighlight = () => {
    // 匹配选中节点以及链路
    if (
      !nodeActionList?.data?.nodes?.some(
        (item: NEXA_API.GNode) => item.id === id,
      ) &&
      (nodeActionList?.type === 'search' || nodeActionList?.type === 'select')
    ) {
      // 暗淡非标无操作节点
      return attributes?.enable ? '#B4DAA8' : '#C4C7CE';
    }
    return attributes?.enable ? '#5dbb30' : '#000a1a78';
  };
  /**
   * 渲染连接桩
   * @returns
   */
  const renderConnectHandle = () => {
    // 指定连接桩数量的数组
    const handleArr = Array.from({ length: 4 });
    // const flowSnap = useSnapshot(EKGFlowState);
    return handleArr.map((_item, index) => {
      const { x, y } = calculateDotPosition({
        index,
        radius: 12,
        handleCount: 4,
        // handleRadius: currentHoverHandle ? 8 : 2,
      });
      return (
        <Tooltip key={index} title="可点击添加节点/拖动连接节点">
          <Handle
            className="node-circle-handle-dot"
            type={id === 'node-1' ? 'source' : 'target'}
            // type="source"
            position={Position.Left}
            style={{
              transform: `translate(${x}px, ${y}px)`,
              opacity: isShowHandle(`${index}`) ? 1 : 0,
              pointerEvents: 'none',
              cursor: 'not-allowed',
            }}
            id={`${index}`}
          />
          {/* </div> */}
        </Tooltip>
      );
    });
  };

  const items: any[] = [
    // {
    //   key: 'copy',
    //   label: <div onClick={() => copyNode(id)}>创建副本</div>,
    // },
    {
      key: 'delete',
      label: (
        <Popconfirm
          onConfirm={(e) => {
            e?.stopPropagation();
            deleteNode(id);
          }}
          onCancel={(e) => e.stopPropagation()}
          title="确定要删除当前节点吗？"
        >
          <div className="delete" onClick={(e) => e.stopPropagation()}>
            <div>删除</div>
            <div className="tag">backspace</div>
          </div>
        </Popconfirm>
      ),
    },
  ];

  // 点击菜单外区域隐藏菜单
  const handleClickOutside = (e) => {
    // 判断点击事件是否在菜单中
    if (menuRef.current && !menuRef.current.contains(e.target)) {
      setIsShowMenu(false);
    }
  };

  /**
   * 右键自定义菜单
   */
  const customMenu = () => {
    return (
      <div
        style={{ position: 'absolute', top: '12px', left: '12px', zIndex: 100 }}
        ref={menuRef}
      >
        <Menu items={items} selectable={false} />
      </div>
    );
  };

  useEffect(() => {
    window.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);
  console.log(attributes?.enable, 'attributes?.enable');
  return (
    <StartNodeWrapper>
      <div
        onClick={() => {
          EKGFlowState.nodeDetailData.data = {
            id: id,
            type: 'operationPlanNode',
            enable: attributes?.enable,
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
                  type: 'opsgptkg_schedule',
                },
              ],
            },
          };
          debouncedHandleSearch();
        }}
        className={isMatchSearch()}
      >
        <Flex
          className="node-circle"
          style={{ background: isNodeHighlight() }}
          justify={'center'}
          align="center"
          onContextMenu={(e) => {
            e.preventDefault();
            setIsShowMenu(true);
          }}
        >
          <Spin spinning={loading} size="small">
            {/* 渲染连接桩 */}
            {renderConnectHandle()}
            {/* 右键自定义菜单 */}
            {isShowMenu && customMenu()}
          </Spin>
        </Flex>
      </div>
      <div className="node-title">{attributes?.name}</div>
    </StartNodeWrapper>
  );
};

export default OperationPlanNode;
