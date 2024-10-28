import { createSession } from '@/services/nexa/PortalConversationController';
import { getMyEmpId, getMyLoginName } from '../../utils/userStore';
import { useParams, useRequest } from '@umijs/max';
import {
  Button,
  Form,
  Input,
  message,
  Space,
  Spin,
} from 'antd';
import React, {
  createContext,
  useContext,
  useState,
} from 'react';
import { CloseOutlined } from '@ant-design/icons';
import { cloneDeep } from 'lodash';
import type { CommonContextType } from '../../Common';
import { CommonContext } from '../../Common';
import { ssePost } from './sseport';
import { FooterWrapper } from './style';

interface InputContextType {
  type: 'ANTEMC' | 'NLP';
  setType: React.Dispatch<React.SetStateAction<'ANTEMC' | 'NLP'>>;
  form: any;
}

const InputContext = createContext<InputContextType | undefined>(undefined);

const ChatFooter = () => {
  const [type, setType] = useState<'ANTEMC' | 'NLP'>('NLP');
  const [loading, setLoading] = useState<boolean>(false);

  const { selectedAgent, setMsgList, msgList } = useContext(
    CommonContext,
  ) as CommonContextType;

  const [form] = Form.useForm();
  const { TextArea } = Input;
  const { spaceId } = useParams();

  const RenderTextBtn = () => {
    return (
      <Button
        onClick={() => {
          form.resetFields();
          setType('ANTEMC');
        }}
      >
        <Space>
          <img
            src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*ohd3SLyQp4oAAAAAAAAAAAAADprcAQ/original"
            style={{
              width: '24px',
              height: '24px',
              border: 'none',
              transform: 'scale(.8)',
            }}
          />
          <span>应急场景调试</span>
        </Space>
      </Button>
    );
  };

  const RenderDebugBtn = () => {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '100%',
          height: '32px',
          marginTop: '8px',
          padding: '0 8px',
          background: '#000a1a0a',
          borderRadius: '8px 8px 0 0',
        }}
      >
        <Space>
          <img
            src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*ohd3SLyQp4oAAAAAAAAAAAAADprcAQ/original"
            style={{
              width: '24px',
              height: '24px',
              border: 'none',
              transform: 'scale(.8)',
            }}
          />
          <span>应急场景调试</span>
        </Space>
        <CloseOutlined
          style={{ cursor: 'pointer' }}
          onClick={() => {
            form.resetFields();
            setType('NLP');
          }}
        />
      </div>
    );
  };

  const renderHeader = () => {
    if (type === 'NLP') {
      return <RenderTextBtn />;
    }
    if (type === 'ANTEMC') {
      return <RenderDebugBtn />;
    }
  };

  /**
   * 发送普通会话
   * @param props_sessionId
   * @param inputValueStr
   */
  const sendSession = (props_sessionId: string, inputValueStr?: string) => {
    setMsgList((preMsg: NEX_MAIN_API.EKGChatMsgList) => {
      const newMsg = cloneDeep(preMsg);
      return [
        ...newMsg,
        {
          type: 'json',
          msgId: new Date().getTime(),
          content: {
            output: inputValueStr,
            input: inputValueStr,
            role: 'user',
            messageType: 'json',
            conversationId: new Date().getTime(),
            status: 'EXECUTING',
          },
          traceId: new Date().getTime(),
          chatResultTypeCode: 'cover',
          streamingDisplay: false,
        },
        {
          type: 'json',
          msgId: new Date().getTime(),
          content: {
            output: '输出中',
            input: inputValueStr,
            role: 'assistant',
            messageType: 'json',
            conversationId: new Date().getTime(),
            status: 'EXECUTING',
          },
          traceId: new Date().getTime(),
          chatResultTypeCode: 'cover',
          streamingDisplay: false,
        },
      ];
    });
    ssePost(
      '/api/portal/conversation/chat',
      {
        sessionId: props_sessionId,
        agentId: selectedAgent?.agentId,
        userId: getMyLoginName(),
        empId: getMyEmpId(),
        type: 'text',
        submitType: 'NORMAL',
        content: { text: inputValueStr },
        stream: false,
        extendContext: {
          debugMode: true,
          ekgMode: true,
          ekgSource: type,
          spaceId,
          ...(msgList[msgList.length - 1]?.extendContext || {})
        },
      },
      {
        setLoading,
        props_sessionId,
        setMsgList,
      },
    );
    form.resetFields();
  };

  /**
   * 创建普通会话
   */
  const createSession_action = useRequest(createSession, {
    manual: true,
    formatResult: (res: any) => res,
    onSuccess: (res: any, params: any) => {
      if (res?.success) {
        sendSession(res?.data, params[0]?.summary);
      } else {
        message.error(res?.errorMessage);
      }
    },
  });

  const sendMessage = (inputValueStr: string) => {
    if (inputValueStr) {
      setLoading(true);
      if (!msgList || msgList?.length === 0) {
        createSession_action.run({
          userId: getMyLoginName(),
          empId: getMyEmpId(),
          summary: inputValueStr,
          debugMode: true,
        });
      } else {
        const preData = msgList[msgList.length - 1];
        sendSession(preData?.extendContext?.chatUnidId, inputValueStr);
      }
    } else {
      message.warning('请先问一个问题');
    }
  };

  return (
    <FooterWrapper>
      <InputContext.Provider
        value={{
          type,
          setType,
          form,
        }}
      >
        <Form form={form} style={{ width: '100%', height: '100%' }}>
          <div className="InputMainWrapper">
            {/* <div style={{ width: '100%', height: '40px' }}>
              {renderHeader()}
            </div> */}
            <div
              className="InputWrapper"
              style={{
                border: `${type === 'NLP' ? '1px solid #d9d9d9' : 'none'}`,
                borderRadius: `${type === 'NLP' ? '8px' : '0 0 8px 8px'}`,
              }}
            >
              <div className="sendInputWrapper">
                <Form.Item name="input" noStyle>
                  <TextArea
                    placeholder={`${type === 'NLP'
                      ? '有问题可以随时问我…'
                      : '请输入极光事件ID'
                      }`}
                    onPressEnter={(e: any) => {
                      e.preventDefault();
                      if (e.shiftKey) {
                        form.setFieldValue('input', e.target.value + '\n');
                      } else {
                        sendMessage(e.target.value);
                        form.resetFields();
                      }
                    }}
                  />
                </Form.Item>
              </div>
              <div className="sendBtnWrapper">
                <Spin
                  size="small"
                  style={{ width: '28px', height: '28px' }}
                  spinning={loading}
                >
                  <img
                    src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*LZ9PS5jN2swAAAAAAAAAAAAADprcAQ/original"
                    style={{
                      width: '28px',
                      height: '28px',
                      border: 'none',
                      transform: 'scale(.8)',
                      cursor: 'pointer',
                    }}
                    onClick={() => {
                      sendMessage(form.getFieldValue('input'));
                      form.resetFields();
                    }}
                  />
                </Spin>
              </div>
            </div>
          </div>
        </Form>
      </InputContext.Provider>
    </FooterWrapper>
  );
};

export default ChatFooter;
