import { queryList } from '@/services/nexa/PortalAgentOperationController';
import { dataToJson } from '../utils/format';
import { Outlet, useRequest } from '@umijs/max';
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react';
import {
  CheckOutlined,
  ExclamationCircleFilled,
  QuestionCircleOutlined,
  RightOutlined,
} from '@ant-design/icons';
import {
  Button,
  Col,
  Form,
  message,
  Modal,
  Popover,
  Row,
  Segmented,
  Select,
  Space,
  Spin,
  Tooltip,
} from 'antd';
import Chat from './Chat';
import ChatDetail from './ChatDetail';
import { ChatWrapper, HeaderWrapper, SelectAgentWrapper } from './style';

export interface CommonContextType {
  isShowChat: boolean;
  setShowChat: React.Dispatch<React.SetStateAction<boolean>>;
  headerType: HeaderProps;
  setHeaderType: React.Dispatch<React.SetStateAction<HeaderProps>>;
  agentList: NEXA_API.AgentInfoVO[];
  setAgentList: React.Dispatch<React.SetStateAction<NEXA_API.AgentInfoVO[]>>;
  selectedAgent: NEXA_API.AgentInfoVO;
  setSelectedAgent: React.Dispatch<React.SetStateAction<NEXA_API.AgentInfoVO>>;
  msgList: any[];
  setMsgList: React.Dispatch<React.SetStateAction<any[]>>;
}

export const CommonContext = createContext<CommonContextType | undefined>(
  undefined,
);

type HeaderProps = 'chat' | 'chatDetail' | 'result' | '' | string;

const AgentChangeSelect = () => {
  const { agentList, selectedAgent } = useContext(
    CommonContext,
  ) as CommonContextType;

  return (
    <Form.Item
      name="agent"
      noStyle
      style={{ width: '100%' }}
      initialValue={selectedAgent?.agentId}
    >
      <Select style={{ width: '100%' }} allowClear>
        {(agentList || []).map((item: NEXA_API.AgentInfoVO, index: number) => (
          <Select.Option value={item?.agentId} key={index}>
            <Tooltip title={item?.agentName}>
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0 8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  {item?.avatar && (
                    <img
                      src={item?.avatar}
                      style={{
                        width: '24px',
                        height: '24px',
                        border: 'none',
                        borderRadius: '50%',
                        marginRight: '8px',
                      }}
                    />
                  )}
                  <span
                    style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}
                  >
                    {item?.agentName}
                  </span>
                </div>
              </div>
            </Tooltip>
          </Select.Option>
        ))}
      </Select>
    </Form.Item>
  );
};

const CommonHeader = () => {
  const [open, setOpen] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const {
    headerType,
    setHeaderType,
    setShowChat,
    selectedAgent,
    setSelectedAgent,
    agentList,
    setMsgList,
  } = useContext(CommonContext) as CommonContextType;

  const [form] = Form.useForm();

  const renderChangeAgent = () => {
    return (
      <Form form={form}>
        <Form.Item>
          <AgentChangeSelect />
        </Form.Item>
        <Row>
          <Col span={24} style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setOpen(false)}>取消</Button>
              <Button
                type="primary"
                onClick={() => {
                  setIsModalOpen(true);
                }}
              >
                保存
              </Button>
            </Space>
          </Col>
        </Row>
      </Form>
    );
  };

  const formatType = () => {
    switch (headerType) {
      case 'chat':
        return 'chat';
      case 'result':
        return 'result';
      case '':
        return 'chat';
      default:
        return 'result';
    }
  };

  return (
    <HeaderWrapper>
      <Button
        className="headerBtn"
        onClick={() => {
          setSelectedAgent({});
          setHeaderType('');
          setShowChat(false);
        }}
      >
        <RightOutlined />
      </Button>
      <Segmented
        // value={(
        //   headerType === 'chatDetail' ||
        //   headerType === 'result'
        // ) ? 'result' : 'chat'
        // }
        value={formatType()}
        options={[
          { label: '对话运行', value: 'chat' },
          { label: '运行结果', value: 'result' },
        ]}
        onChange={(value: HeaderProps) => {
          if (!dataToJson(selectedAgent).flag && value === 'chat') {
            setHeaderType('');
            return;
          }
          setHeaderType(value);
        }}
      />
      {headerType === 'chat' ? (
        <Space>
          <div className="headerIcon">
            <Popover
              trigger="click"
              placement="bottomRight"
              content={renderChangeAgent()}
              title={
                <Space>
                  <span>关联Agent</span>
                  <Tooltip title="关联后将使用 Agent 中的技能为您进行运行调试">
                    <QuestionCircleOutlined style={{ cursor: 'help' }} />
                  </Tooltip>
                </Space>
              }
              open={open}
              onOpenChange={(newOpen: boolean) => {
                if (!isModalOpen) {
                  setOpen(newOpen);
                }
                return;
              }}
            >
              <img
                src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*XzjlR5gE1OEAAAAAAAAAAAAADprcAQ/original"
                style={{
                  width: '24px',
                  height: '24px',
                  border: 'none',
                }}
              />
            </Popover>
          </div>
          <div className="headerIcon">
            <Tooltip title="点击清除聊天记录">
              <img
                src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*ZtqnTpAiVG4AAAAAAAAAAAAADprcAQ/original"
                style={{
                  width: '24px',
                  height: '24px',
                  border: 'none',
                }}
                onClick={() => setMsgList([])}
              />
            </Tooltip>
          </div>
        </Space>
      ) : (
        <div />
      )}
      {isModalOpen && (
        <Modal
          title={
            <Space>
              <ExclamationCircleFilled style={{ color: '#faad14' }} />
              <span style={{ fontSize: '16px', fontWeight: 500 }}>
                是否要保存 ?
              </span>
            </Space>
          }
          open={isModalOpen}
          onOk={(e) => {
            e.stopPropagation();
            setSelectedAgent(
              agentList?.filter(
                (item: NEXA_API.AgentInfoVO) =>
                  item.agentId === form.getFieldValue('agent'),
              )[0],
            );
            setMsgList([]);
            setIsModalOpen(false);
            setOpen(false);
            message.success('切换成功');
          }}
          onCancel={(e) => {
            e.stopPropagation();
            setIsModalOpen(false);
          }}
        >
          <p>更改关联Agent后将清空当前的对话记录, 无法恢复</p>
        </Modal>
      )}
    </HeaderWrapper>
  );
};

const SelectAgent = () => {
  const {
    agentList,
    setAgentList,
    setHeaderType,
    selectedAgent,
    setSelectedAgent,
  } = useContext(CommonContext) as CommonContextType;
  /**
   * 获取图谱信息
   */
  const queryGraphDetail = useRequest(queryList, {
    manual: true,
    formatResult: (res) => res,
    onSuccess: (res) => {
      if (res?.success) {
        setAgentList(res?.data);
      } else {
        message.error(res?.errorMessage);
      }
    },
  });

  useEffect(() => {
    queryGraphDetail.run({});
  }, []);

  return (
    <SelectAgentWrapper>
      <div className="agentTitle">请先关联 Agent</div>
      <div className="agentDes">
        关联后将使用 Agent 中的技能为您进行运行调试
      </div>
      <Spin spinning={queryGraphDetail.loading} style={{ width: '100%' }}>
        <Select
          size="large"
          style={{ width: '100%' }}
          allowClear
          onChange={(value: string | undefined) => {
            if (value) {
              const data = agentList?.filter((it) => it.agentId === value)[0];
              setSelectedAgent(data as NEXA_API.AgentInfoVO);
            } else {
              setSelectedAgent({});
            }
          }}
        >
          {(agentList || []).map(
            (item: NEXA_API.AgentInfoVO, index: number) => (
              <Select.Option value={item?.agentId} key={index}>
                <Tooltip title={item?.agentName}>
                  <div
                    style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0 8px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      {item?.avatar && (
                        <img
                          src={item?.avatar}
                          style={{
                            width: '24px',
                            height: '24px',
                            border: 'none',
                            borderRadius: '50%',
                            marginRight: '8px',
                          }}
                        />
                      )}
                      <span
                        style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}
                      >
                        {item?.agentName}
                      </span>
                    </div>
                    {(dataToJson(selectedAgent).data as NEXA_API.AgentInfoVO)
                      ?.agentId === item?.agentId && (
                        <CheckOutlined style={{ color: '#5272e0' }} />
                      )}
                  </div>
                </Tooltip>
              </Select.Option>
            ),
          )}
        </Select>
      </Spin>
      <Button
        block
        type="primary"
        disabled={!dataToJson(selectedAgent).flag}
        onClick={() => dataToJson(selectedAgent).flag && setHeaderType('chat')}
        className={
          !dataToJson(selectedAgent).flag ? 'noSelected' : 'hasSelected'
        }
      >
        开始对话运行
      </Button>
    </SelectAgentWrapper>
  );
};

export default () => {
  const [isShowChat, setShowChat] = useState(false);
  const [headerType, setHeaderType] = useState<HeaderProps>('');
  const [agentList, setAgentList] = useState<any>([]);
  const [selectedAgent, setSelectedAgent] = useState<any>({});
  const [msgList, setMsgList] = useState<any[]>([]);

  const renderContent = () => {
    if (!headerType || headerType === 'chat') {
      if (headerType === 'chat') {
        return dataToJson(selectedAgent).flag ? <Chat /> : <SelectAgent />;
      }
      return <SelectAgent />;
    }
    return <ChatDetail />;
  };

  return (
    <CommonContext.Provider
      value={{
        isShowChat,
        setShowChat,
        headerType,
        setHeaderType,
        agentList,
        setAgentList,
        selectedAgent,
        setSelectedAgent,
        msgList,
        setMsgList,
      }}
    >
      {isShowChat && (
        <ChatWrapper>
          <CommonHeader />
          {renderContent()}
        </ChatWrapper>
      )}
      <Outlet></Outlet>
    </CommonContext.Provider>
  );
};
