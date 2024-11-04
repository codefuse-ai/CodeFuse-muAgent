import { dataToJson, jsonToData } from '../../utils/format';
import { getMyEmpId } from '../../utils/userStore';
import { Avatar, Button, Space } from 'antd';
import React, { useContext, useState, useRef, useEffect } from 'react';
import {
  CheckCircleFilled,
  CloseCircleFilled,
  ExclamationCircleFilled,
} from '@ant-design/icons';
import type { CommonContextType } from '../../Common';
import { CommonContext } from '../../Common';
import AgentPrologue from './AgentPrologue';
import { ContentWrapper } from './style';
import TemplateCode from './TemplateCode';

const ChatContent = () => {
  const { msgList, selectedAgent, setHeaderType } = useContext(
    CommonContext,
  ) as CommonContextType;
  const contentRef = useRef(null);

  const formatMsgContent = (dataItem: NEX_MAIN_API.EKGChatJSONMsg) => {
    const { content, type } = dataItem;
    if (type === 'json') {
      const { costMs, output, input, status } =
        content as NEX_MAIN_API.EKGChatJSONMsgContent;
      return {
        costMs,
        text: output,
        input,
        status,
      };
    }
    if (type === 'text') {
      return { text: jsonToData(content as unknown as string)?.data?.text };
    }
    if (type === 'role_response') {
      if (content.response?.type === 'text') {
        return { text: content.response.content.text }
      }
      return { text: content.response.text }
    }
    return { text: '解析错误' };
  };

  const renderAvatarSrc = (item: any) => {
    if (item?.content?.role === 'user') {
      return `https://work.alibaba-inc.com/photo/${getMyEmpId()}.100x100.jpg`;
    }
    if (item?.type === "role_response") {
      return item?.content?.url;
    }
    return selectedAgent?.avatar;
  };

  const renderAvatarTitle = (item: any) => {
    if (item?.type === "role_response") {
      return item?.content?.name;
    }
  };

  useEffect(() => {
    const contentElement = contentRef.current;
    const scrollToBottom = () => {
      contentElement.scrollTop = contentElement.scrollHeight;
    };
    const observer = new MutationObserver(scrollToBottom);
    observer.observe(contentElement, { childList: true, subtree: true });
    scrollToBottom();
    return () => observer.disconnect();
  }, []);


  return (
    <ContentWrapper className='contentClass' ref={contentRef}>
      {!dataToJson(msgList).flag && <AgentPrologue agent={selectedAgent} />}
      {msgList?.length > 0 && (
        <>
          {msgList?.map((items: NEX_MAIN_API.EKGChatJSONMsg, index: number) => {
            console.log('debug_msgList渲染>>>>', msgList);
            return (
              <div
                key={index}
                className="msg_wrap"
                style={{
                  flexDirection: `${items.content.role === 'user' ? 'row-reverse' : 'row'
                    }`,
                }}
              >
                <Space direction='vertical' align='start'>
                  <Avatar
                    style={{
                      width: '30px',
                      height: '30px',
                      borderRadius: '50%',
                      marginLeft: `${items.content.role === 'user' ? '8px' : '0'
                        }`,
                      marginRight: `${items.content.role === 'user' ? '0' : '8px'
                        }`,
                    }}
                    src={renderAvatarSrc(items)}
                  />
                  <span style={{ fontSize: '11px' }}>{renderAvatarTitle(items)}</span>
                </Space>
                <span
                  className={`${items.content.role === 'user'
                    ? 'user_wrap'
                    : 'assistant_wrap'
                    }`}
                  style={{
                    marginLeft: `${items.content.role === 'user' ? '38px' : '0'
                      }`,
                    marginRight: `${items.content.role === 'user' ? '0' : '38px'
                      }`,
                    color: `${items.content.role === 'user' ? '#fff' : '#000'}`,
                  }}
                >
                  {formatMsgContent(items)?.text === '输出中' ? (
                    <img
                      src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*WrVSTKIIUGkAAAAAAAAAAAAADprcAQ/original"
                      alt=""
                    />
                  ) : (
                    <div
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                      }}
                    >
                      <TemplateCode
                        dataSource={formatMsgContent(items)?.text}
                      />
                    </div>
                  )}
                </span>
              </div>
            );
          })}
        </>
      )}
    </ContentWrapper>
  );
};

export default ChatContent;
