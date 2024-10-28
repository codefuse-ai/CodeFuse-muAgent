import { intent } from '@/services/afs2demo/opsconvobus/EkgGraphController';
import { query } from '@/services/opsgpt/ConversationController';
import { copyText, dataToJson } from '../../utils/format';
import { history, useParams, useRequest } from '@umijs/max';
import {
  Button,
  Card,
  Col,
  message,
  Row,
  Space,
  Tag,
  Tooltip,
  Tree,
} from 'antd';
import React, { useContext, useEffect, useState } from 'react';
import { cloneDeep, debounce } from 'lodash';
import {
  ApartmentOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
  ExclamationCircleFilled,
} from '@ant-design/icons';
import type { CommonContextType } from '../../Common';
import { CommonContext } from '../../Common';
import { EKGChildFlowState } from '../../Flow/store';
import TemplateCode from '../Chat/TemplateCode';
import { ChatDetailWrapper } from './style';

const ResultPage = ({
  msgList,
}: {
  msgList: NEX_MAIN_API.EKGChatJSONMsg[];
}) => {
  const renderStatusIcon = (dataItem: NEX_MAIN_API.EKGChatJSONMsg) => {
    const { status = 'EXECUTING', input } = dataItem?.content;
    switch (status) {
      case 'EXECUTING':
        return {
          icon: <ExclamationCircleFilled style={{ color: '#ccc' }} />,
          text: <span>{input}</span>,
        };
      case 'FAILED':
        return {
          icon: <CloseCircleFilled style={{ color: '#ff4d4f' }} />,
          text: <span>{input}</span>,
        };
      case 'FINISHED':
        return {
          icon: <CheckCircleFilled style={{ color: '#52c41a' }} />,
          text: <span>{input}</span>,
        };
      default:
        return {
          icon: <ExclamationCircleFilled style={{ color: '#ccc' }} />,
          text: <span>{input}</span>,
        };
    }
  };
  return (
    <ChatDetailWrapper>
      <Row style={{ width: '100%', marginTop: '12px' }}>
        {(msgList || [])?.map(
          (item: NEX_MAIN_API.EKGChatJSONMsg, index: number) => {
            if (item.content.role !== 'user') {
              return (
                <Col
                  key={index}
                  span={24}
                  className="detailCol"
                // 二期再支持
                // onClick={() => {
                //   history.push(`./${ekgId}/flow/${item?.id}`);
                // }}
                >
                  <Tooltip title={renderStatusIcon(item).text}>
                    <div
                      style={{
                        width: '100%',
                        height: '100%',
                        background: '#fff',
                        padding: '12px',
                        borderRadius: '12px',
                      }}
                    >
                      <div
                        style={{
                          width: '100%',
                          overflow: 'hidden',
                          display: 'flex',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        <span style={{ margin: '0 8px' }}>
                          {renderStatusIcon(item).icon}
                        </span>
                        <div className="dec">{renderStatusIcon(item).text}</div>
                      </div>
                    </div>
                  </Tooltip>
                </Col>
              );
            }
            return false;
          },
        )}
      </Row>
    </ChatDetailWrapper>
  );
};

const DetailResultPage = ({
  conversationId,
}: {
  conversationId: string;
  setHeaderType: (type: string) => void;
}) => {
  const [detailData, setDetilData] = useState([]);
  const [expandedKeys, setExpandedKeys] = useState<string[]>(['startNode']);
  const [extraInfo, setExtraInfo] = useState<any>({});

  const { ekgId, flowId } = useParams();

  const formatTitle = (name: string, type: string) => {
    switch (type) {
      case 'startNode':
        return (
          <Space>
            <div className="startNodeIcon" />
            <span>{name}</span>
          </Space>
        );
      case 'opsgptkg_intent':
        return (
          <Space>
            <div className="opsgptkgIntentIcon" />
            <span>{`跳转至${name}`}</span>
          </Space>
        );
      case 'opsgptkg_schedule':
        return (
          <Space>
            <div className="opsgptkgScheduleIcon" />
            <span>{name}</span>
          </Space>
        );
    }
  };

  const transformData = (data: any) => {
    return data.map((item: any) => {
      const { child, ...rest } = item;
      setExpandedKeys((pre: any) => [...pre, rest.id]);
      return {
        ...rest,
        title: formatTitle(rest.name, rest.type),
        key: rest.id,
        children: child ? transformData(child) : [],
      };
    });
  };

  const query_action = useRequest(query, {
    manual: true,
    formatResult: (res: any) => res,
    onSuccess: (res: any) => {
      if (res?.success) {
        EKGChildFlowState.currentGraphData.nodeHeaderStatus = true;
        EKGChildFlowState.currentGraphData.nodeHeaderStatusInfo = res.data;
      } else {
        message.error(res?.errorMsg);
      }
    },
  });

  const intent_action = useRequest(intent, {
    manual: true,
    formatResult: (res: any) => res,
    onSuccess: (res: any) => {
      if (res?.success) {
        if (res.data && dataToJson(res.data)?.flag) {
          const newData = cloneDeep([
            {
              id: 'startNode',
              name: '开始',
              type: 'startNode',
              status: 'EXECUTED_SUCCESS',
              child: res.data?.intents,
            },
          ]);
          const modifiedData = transformData(newData);
          setDetilData(modifiedData);
        }
      } else {
        message.error(res?.errorMsg);
      }
    },
  });

  const transformSelectData = (data: any, curKey: string) => {
    return (
      data
        .map((item: any) => {
          if (
            data?.filter((dataItem: any) => dataItem.key === curKey).length > 0
          ) {
            return data?.filter((dataItem: any) => dataItem.key === curKey);
          }
          return item.children
            ? transformSelectData(item.children, curKey)
            : null;
        })
        .find((item: any) => item !== null) || {}
    );
  };

  const selectTree = (curKey: string) => {
    const curData = transformSelectData(detailData, curKey)[0];
    console.log('curData', curData);
    setExtraInfo(curData);
  };

  const handleCopy = debounce((text) => {
    copyText(text);
  }, 300);

  useEffect(() => {
    intent_action.run({
      conversationId,
    });
    query_action.run({
      sessionId: conversationId,
    });
    return () => {
      EKGChildFlowState.currentGraphData.nodeHeaderStatus = false;
      EKGChildFlowState.currentGraphData.nodeHeaderStatusInfo = {};
    };
  }, []);

  return (
    <ChatDetailWrapper>
      <div className="detailResultWrapper">
        <Card style={{ margin: '8px 0' }} bodyStyle={{ padding: '12px' }}>
          <h4 style={{ fontSize: '15px' }}>确认路径</h4>
          <Tree
            expandedKeys={expandedKeys}
            treeData={detailData}
            onSelect={(selectedKeys) => {
              console.log('selectedKeys', selectedKeys);
              selectTree(selectedKeys[0] as string);
            }}
          />
        </Card>
        {dataToJson(extraInfo)?.flag && (
          <Card style={{ margin: '8px 0' }} bodyStyle={{ padding: '12px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <h4
                  style={{
                    fontSize: '15px',
                    margin: '0 8px 0 0',
                    display: 'inline-block',
                  }}
                >
                  {extraInfo?.name}
                </h4>
                <Tag
                  color={`${extraInfo?.status === 'EXECUTED_SUCCESS'
                    ? '#52c41a1a'
                    : '#f5222d1a'
                    }`}
                  style={{ border: 'none' }}
                >
                  {extraInfo?.status === 'EXECUTED_SUCCESS' ? (
                    <CheckCircleFilled style={{ color: '#52c41a' }} />
                  ) : (
                    <CloseCircleFilled style={{ color: '#ff4d4f' }} />
                  )}
                  <span
                    style={{
                      color:
                        extraInfo?.status === 'EXECUTED_SUCCESS'
                          ? '#52c41a'
                          : '#ff4d4f',
                    }}
                  >
                    {`${extraInfo?.costMs / 1000 || 0.0}s`}
                  </span>
                </Tag>
              </div>
              <Button
                type="link"
                loading={query_action.loading}
                disabled={flowId ? true : false}
                style={{ margin: 0, padding: 0 }}
                onClick={() => {
                  history.push(`${ekgId}/flow/${extraInfo.id}`);
                }}
              >
                <Space>
                  <ApartmentOutlined />
                  <span>查看流程</span>
                </Space>
              </Button>
            </div>
            <div
              style={{
                marginTop: '12px',
                borderRadius: '12px',
                background: '#000a1a0a',
                padding: '12px',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  borderBottom: '1px solid #e3e4e6',
                  paddingBottom: '8px',
                }}
              >
                <h4 style={{ margin: 0 }}>输入</h4>
                <img
                  src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*7ARCT7alifwAAAAAAAAAAAAADprcAQ/original"
                  style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                  onClick={() => {
                    handleCopy(extraInfo?.input || '');
                  }}
                />
              </div>
              <TemplateCode dataSource={extraInfo?.input || ''} />
            </div>
            {(extraInfo?.output || [])?.map((item: string, index: number) => (
              <div
                key={index}
                style={{
                  marginTop: '12px',
                  borderRadius: '12px',
                  background: '#000a1a0a',
                  padding: '12px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderBottom: '1px solid #e3e4e6',
                    paddingBottom: '8px',
                  }}
                >
                  <h4 style={{ margin: 0 }}>输出</h4>
                  <img
                    src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*7ARCT7alifwAAAAAAAAAAAAADprcAQ/original"
                    style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                    onClick={() => {
                      handleCopy(item || '');
                    }}
                  />
                </div>
                <TemplateCode dataSource={item || ''} />
              </div>
            ))}
          </Card>
        )}
      </div>
    </ChatDetailWrapper>
  );
};

const ChatDetail = () => {
  const { msgList, headerType, setHeaderType } = useContext(
    CommonContext,
  ) as CommonContextType;

  return (
    <ChatDetailWrapper>
      <div className="detailListWrapper">
        {headerType === 'result' ? (
          <ResultPage msgList={msgList} />
        ) : (
          <DetailResultPage
            conversationId={headerType}
            setHeaderType={setHeaderType}
          />
        )}
      </div>
    </ChatDetailWrapper>
  );
};

export default ChatDetail;
