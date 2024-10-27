import { safeJsonStringify } from '@/pages/EKG/utils';
import {
  CloseOutlined,
  createFromIconfontCN,
  EditOutlined,
  EllipsisOutlined,
} from '@ant-design/icons';
import { useSnapshot } from '@umijs/max';
import { Dropdown, Input, message, Popconfirm, Tag, Typography } from 'antd';
import React, { useEffect, useState } from 'react';
import JSONInput from 'react-json-editor-ajrm';
import locale from 'react-json-editor-ajrm/locale/en';
import ReactMarkdown from 'react-markdown';
import { EKGChildFlowState } from '../store';
import { Container } from './style';
interface IProps {
  icon?: string;
  moduleData?: {
    data: {
      attributes: {
        name: string;
      };
      onChangeNode: ({ name, id }: any) => void;
      onCopyNode: ({ template }: any) => void;
    };
    id: string;
  };
}

export default (props: IProps) => {
  const { nodeHeaderStatus, nodeHeaderStatusInfo } =
    useSnapshot(EKGChildFlowState).currentGraphData;

  const [recordVisible, setRecordVisible] = useState(false); // 展示运行记录
  const IconFont = createFromIconfontCN({
    scriptUrl: ['//at.alicdn.com/t/a/font_4444522_biui96gf7f.js'],
  });
  const [isEditTitle, setIsEditTitle] = useState(false); // 是否编辑标题
  const iptRef = React.useRef(null);
  const { icon, moduleData } = props;
  const width = 420;
  let statusInfo = {} as any;

  Object.entries(nodeHeaderStatusInfo?.nodes || {}).forEach((i) => {
    if (i[0] === moduleData?.id) {
      statusInfo = i[1];
    }
  });
  const Code = {
    code({ children, ...props }) {
      return <code {...props}>{String(children).replace(/\n$/, '')}</code>;
    },
    // img: ImageRender,
  };
  const items = [
    {
      key: '1',
      label: (
        <div
          onClick={() => {
            moduleData?.data.onCopyNode({
              template: {
                id: moduleData?.id,
                name: `${moduleData?.data.attributes.name}_1`,
                type: moduleData?.type,
              },
              position: { x: moduleData.xPos + 200, y: moduleData.yPos + 50 },
            });
          }}
        >
          创建副本
        </div>
      ),
    },
    {
      key: '2',
      label: (
        <Popconfirm
          title="确定删除节点吗？"
          onConfirm={() => {
            moduleData?.data.onChangeNode({
              id: moduleData?.id,
              type: 'delete',
            });
          }}
        >
          <div style={{ color: '#ff4d4f' }}>删除</div>
        </Popconfirm>
      ),
    },
  ];
  const handleCopy = (response: any) => {
    const textArea = document.createElement('textarea');
    textArea.value = safeJsonStringify(response);
    document.body.appendChild(textArea);
    textArea.select();
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        message.success('复制成功');
      } else {
        message.error('复制失败');
      }
    } catch (err) {
      console.error('Oops, unable to  copy', err);
    }
    document.body.removeChild(textArea);
  };
  const onChangeTitle = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsEditTitle(false);
    if (!e.target.value) {
      message.warning('模块名称不能为空');
      return;
    }
    moduleData?.data.onChangeNode({
      id: moduleData?.id,
      type: 'editName',
      value: e.target.value,
    });
  };
  useEffect(() => {
    if (nodeHeaderStatus === false) {
      setRecordVisible(false);
    }
  }, [nodeHeaderStatus]);
  return (
    <Container>
      {recordVisible && nodeHeaderStatus && (
        <div style={{ marginLeft: `${width}px` }} className="content">
          <div className="content_header">
            <div className="content_header_text">执行结果</div>
            <div
              onClick={() => setRecordVisible(false)}
              className="content_header_close"
            >
              <CloseOutlined />
            </div>{' '}
          </div>
          <div className="content_item">
            <div className="content_title">
              <div className="content_title_text">输入</div>
              <div
                onClick={() => handleCopy(statusInfo?.toolParam)}
                className="content_title_icon"
              >
                <img
                  width={18}
                  src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*7ARCT7alifwAAAAAAAAAAAAADprcAQ/original"
                />
              </div>
            </div>
            <div className="markdown nowheel">
              {typeof statusInfo.toolParam === 'string' ? (
                <ReactMarkdown components={Code}>
                  {safeJsonStringify(statusInfo?.toolParam)}
                </ReactMarkdown>
              ) : (
                <JSONInput
                  id="1"
                  locale={locale}
                  placeholder={statusInfo?.toolParam}
                  height={200}
                  theme="light_mitsuketa_tribute"
                />
              )}
            </div>
          </div>
          <div className="content_item">
            <div className="content_title">
              <div className="content_title_text">输出</div>
              <div
                className="content_title_icon"
                onClick={() => handleCopy(statusInfo?.toolResponse)}
              >
                <img
                  width={18}
                  src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*7ARCT7alifwAAAAAAAAAAAAADprcAQ/original"
                />
              </div>
            </div>
            <div className="markdown nowheel">
              {typeof statusInfo?.toolResponse === 'string' ? (
                <ReactMarkdown components={Code}>
                  {safeJsonStringify(statusInfo?.toolResponse)}
                </ReactMarkdown>
              ) : (
                <JSONInput
                  id="2"
                  locale={locale}
                  placeholder={statusInfo?.toolResponse}
                  height={200}
                  theme="light_mitsuketa_tribute"
                />
              )}
            </div>
          </div>
        </div>
      )}
      {nodeHeaderStatus && Object.keys(statusInfo).length > 0 && (
        <div>
          {statusInfo.status === 'EXECUTED_SUCCESS' && (
            <div style={{ width }} className={`status success`}>
              <IconFont
                type={'icon-wancheng'}
                style={{ fontSize: '20px', marginRight: '10px' }}
              />
              <div> 运行成功</div>
              <div style={{ marginLeft: 8 }}>
                <Tag color="success">{statusInfo?.costMs / 1000}s</Tag>
              </div>
              <div className="expand">
                {' '}
                <a onClick={() => setRecordVisible(!recordVisible)}>
                  {recordVisible ? '关闭运行记录' : '展开运行记录'}
                </a>
              </div>
            </div>
          )}
          {statusInfo.status === 'EXECUTED_FAIL' && (
            <div style={{ width }} className="status error">
              <IconFont
                type="icon-71shibai"
                style={{ fontSize: '20px', marginRight: '10px' }}
              />
              <div>运行失败</div>
              <div style={{ marginLeft: 8 }}>
                <Tag color="error">{statusInfo?.costMs / 1000}s</Tag>
              </div>
              <div className="expand">
                {' '}
                <a onClick={() => setRecordVisible(!recordVisible)}>
                  {recordVisible ? '关闭运行记录' : '展开运行记录'}
                </a>
              </div>
            </div>
          )}
          {statusInfo.status === 'EXECUTING' && (
            <div style={{ width }} className="status exe">
              <img
                width={20}
                style={{ marginRight: '10px' }}
                src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*PYO-QJlILp0AAAAAAAAAAAAADprcAQ/original"
              />
              <div>运行中</div>
            </div>
          )}
        </div>
      )}
      {moduleData?.type !== 'opsgptkg_schedule' && (
        <div className={'title'}>
          <img width={32} src={icon} />
          {isEditTitle ? (
            <Input
              style={{ flex: 1, marginLeft: 6 }}
              defaultValue={moduleData?.data.attributes.name}
              ref={iptRef}
              onPressEnter={(e) => {
                onChangeTitle(e);
              }}
              onBlur={(e) => {
                onChangeTitle(e);
              }}
            />
          ) : (
            <div style={{ fontWeight: 600, color: '#1c2533' }}>
              <Typography.Text ellipsis style={{ maxWidth: '300px' }}>
                {moduleData.data?.attributes.name}
              </Typography.Text>
              <EditOutlined
                onClick={() => {
                  setIsEditTitle(true);
                  setTimeout(() => {
                    if (iptRef?.current) {
                      (iptRef.current as any).focus();
                    }
                  }, 200);
                }}
                style={{
                  cursor: 'pointer',
                  marginLeft: 8,
                  fontSize: 16,
                }}
              />
            </div>
          )}
          <Dropdown
            placement="bottomRight"
            menu={{ items }}
            trigger={['click']}
          >
            <div
              style={{
                marginLeft: 'auto',
                cursor: 'pointer',
              }}
            >
              <EllipsisOutlined />
            </div>
          </Dropdown>
        </div>
      )}
    </Container>
  );
};
