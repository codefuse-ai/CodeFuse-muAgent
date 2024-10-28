import { CheckCircleFilled, LoadingOutlined } from '@ant-design/icons';
import { history, useParams, useSnapshot } from '@umijs/max';
import { Button, Flex, Space, Typography } from 'antd';
import { EKGChildFlowState } from '../../Flow/store';
import { EKGHeaderWrapper } from './style';

interface IProps {
  onRun: () => void;
  onRelease: () => void;
  saveLoading?: boolean;
  saveTime?: string;
  onSave: () => void;
  type?: string;
  onExitEditing?: () => void;
  childrenTitle?: string;
}
const EKGHeader = (props: IProps) => {
  const {
    onRun,
    // onRelease,
    saveLoading,
    saveTime,
    onSave,
    type,
    onExitEditing,
    childrenTitle,
  } = props;
  const { spaceId, ekgId: knowledgeId } = useParams();
  const { nodeHeaderStatus, nodeHeaderStatusInfo } =
    useSnapshot(EKGChildFlowState).currentGraphData;

  return (
    <EKGHeaderWrapper>
      <Flex
        style={{
          height: '100%',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Space>
          {type === 'children' && (
            <img
              onClick={() => {
                // 返回前保存一次
                onSave();
                history.push(`/space/${spaceId}/ekg/${knowledgeId}`);
              }}
              style={{ cursor: 'pointer' }}
              src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*rvs8Sqo9ul8AAAAAAAAAAAAADprcAQ/original"
            />
          )}
          {saveLoading ? (
            <div
              style={{
                fontSize: '12px',
                color: '#000a1a78',
                marginLeft: '16px',
              }}
            >
              <LoadingOutlined style={{ color: '#1677ff' }} />{' '}
              <span>保存中</span>
            </div>
          ) : (
            <>
              {saveTime && (
                <>
                  <CheckCircleFilled style={{ color: '#52c41a' }} />
                  <div className="header-save-tip">已自动保存 {saveTime}</div>
                </>
              )}
            </>
          )}
        </Space>
        {/* 子flow中展示操作计划名称 */}
        {type === 'children' && (
          <Flex
            className="header-children-wrapper"
            justify="space-between"
            align={'center'}
          >
            <Flex style={{ overflow: 'hidden' }}>
              <img
                width={24}
                src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*DcO9Tpen2n8AAAAAAAAAAAAADprcAQ/original"
              />
              <Typography.Text className="header-children-name" ellipsis>
                {childrenTitle || ''}
              </Typography.Text>
            </Flex>
            <Button type="primary" onClick={onExitEditing}>
              结束编排
            </Button>
          </Flex>
        )}

        <Space>
          {Object.keys(nodeHeaderStatusInfo || {}).length > 0 &&
            type === 'children' && (
              <Button
                onClick={() => {
                  EKGChildFlowState.currentGraphData.nodeHeaderStatus =
                    !nodeHeaderStatus;
                }}
              >
                {nodeHeaderStatus ? '隐藏运行结果' : '展示运行结果'}
              </Button>
            )}
          <Button onClick={onSave}>保存</Button>
          <Button
            onClick={onRun}
          >
            <img src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*JGCiQ5RDgkUAAAAAAAAAAAAADprcAQ/original" />
            运行
          </Button>
        </Space>
      </Flex>
    </EKGHeaderWrapper>
  );
};

export default EKGHeader;
