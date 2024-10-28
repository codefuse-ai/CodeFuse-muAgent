import { IConnectParam, ITemplate } from '@/pages/EKG/flow';
import { sceneNode } from '@/pages/EKG/NodeTemplate';
import { EKGFlowState } from '@/pages/EKG/store';
import { calculateDotPosition } from '@/pages/EKG/utils';
import { useSnapshot } from '@umijs/max';
import { Flex, Tooltip } from 'antd';
import React, { useState } from 'react';
import { Handle, Position } from 'reactflow';
import { StartNodeWrapper } from './style';

interface IProps {
  id: string;
  data: {
    addNode: (template: ITemplate, connectParam?: IConnectParam) => void;
    attributes: any;
  };
  xPos: number;
  yPos: number;
}

const StartNode: React.FC<IProps> = (props) => {
  const { id, data } = props;
  const { addNode, attributes } = data;
  // 图谱数据
  const flowSnap = useSnapshot(EKGFlowState);
  // 当前悬浮到的桩点
  const [currentHoverHandle, setCurrentHoverHandle] = useState<string>('');
  // 是否进入到节点圆形
  const [isHoverNode, setIshoverNode] = useState(false);
  /**
   * 连接桩是否展示
   */
  const isShowHandle = (handleId: string) => {
    const { connectStartParams, currentGraphData } = flowSnap;
    // 当前桩点是否被连接
    const connectFlag = currentGraphData?.edges?.some(
      (item) => item.source === id && item.sourceHandle === handleId,
    );
    // 悬浮到某个桩点时，需要隐藏其他的桩点
    if (currentHoverHandle) {
      return (isHoverNode && currentHoverHandle === handleId) || connectFlag;
    }
    // 展示全部
    // 正在进行连接的桩点
    // edges中已经连接过的桩点
    return (
      isHoverNode ||
      (connectStartParams?.handleId === handleId &&
        connectStartParams?.nodeId === id) ||
      connectFlag
    );
  };

  /**
   * 添加节点
   */
  const handleAddNode = (handleIndex: number) => {
    const connectParam: IConnectParam = {
      nodeId: id,
      sourceHandleIndex: handleIndex,
      type: 'startNode',
      position: {
        x: props?.xPos,
        y: props?.yPos,
      },
    };
    addNode(sceneNode, connectParam);
  };

  /**
   * 连接线在桩点的位置
   * @param dotIndex
   * @returns
   */
  const dotPosition = (dotIndex: number) => {
    switch (dotIndex) {
      case 0:
        return 'Right';
      case 1:
      case 2:
      case 3:
        return 'Bottom';
      case 4:
        return 'Left';
      case 5:
      case 6:
      case 7:
        return 'Top';
      default:
        return 'Top';
    }
  };

  /**
   * 渲染连接桩
   * @returns
   */
  const renderConnectHandle = () => {
    // 指定连接桩数量的数组
    const handleArr = Array.from({ length: 8 });
    return handleArr.map((_item, index) => {
      const { x, y } = calculateDotPosition({
        index,
        radius: 32,
        handleCount: 8,
        handleRadius: currentHoverHandle === `${index}` ? 8 : 2,
      });
      return (
        <Tooltip key={index} title="可点击添加节点/拖动连接节点">
          <Handle
            position={Position[dotPosition(index)]}
            className="node-circle-handle-dot"
            type="source"
            onMouseEnter={() => {
              setCurrentHoverHandle(`${index}`);
            }}
            onMouseLeave={() => {
              setCurrentHoverHandle('');
            }}
            onClick={() => {
              handleAddNode(index);
            }}
            style={{
              transform: `translate(${x}px, ${y}px)`,
              opacity: isShowHandle(`${index}`) ? 1 : 0,
              cursor: 'pointer',
            }}
            id={`${index}`}
          />
        </Tooltip>
      );
    });
  };

  return (
    <StartNodeWrapper>
      <Flex
        className="node-circle"
        justify={'center'}
        align="center"
        onMouseEnter={() => {
          setIshoverNode(true);
        }}
        onMouseLeave={() => {
          setIshoverNode(false);
        }}
      >
        <span className="node-circle-label">开始</span>
        {/* 渲染连接桩 */}
        {renderConnectHandle()}
        <div className="node-title">
          {flowSnap?.knowledgeData?.name || attributes?.description}
        </div>
      </Flex>
    </StartNodeWrapper>
  );
};

export default StartNode;
