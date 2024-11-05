import { QuestionCircleOutlined } from '@ant-design/icons';
import { Collapse, Divider, Form, Input, Tooltip } from 'antd';
import React, { useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import ExecutionConditions from '../components/ExecutionConditions';
import NodeHeader from '../components/NodeHeader';
import { NodeContainer } from './style';
interface IProps {
  id: string;
  data: {
    attributes: {
      description: string;
      accesscriteria: string;
    };

    setNodes: (nodes: any) => void;
  };
}
const { Panel } = Collapse;
const { TextArea } = Input;
export default (props: IProps) => {
  const [form] = Form.useForm();
  const { data } = props;
  const { setNodes, attributes } = data;
  const { description, accesscriteria } = attributes;
  useEffect(() => {
    form.setFieldsValue({ description });
  }, [data]);
  return (
    <NodeContainer>
      <NodeHeader
        moduleData={props}
        icon="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*5reDQ6Z-3vIAAAAAAAAAAAAADprcAQ/original"
      />
      <Handle
        type="target"
        style={{
          width: '12px',
          height: '12px',
          background: '#bdc0c4',
        }}
        id={props?.id}
        position={Position.Left}
      />
      <Form
        form={form}
        onValuesChange={() => {
          setNodes((nodes) => {
            let isVerification = false;
            form
              .validateFields()
              .then(() => {
                isVerification = true;
              })
              .catch(() => {
                isVerification = false;
              });

            return nodes.map((node) => {
              if (node.id === props.id) {
                return {
                  ...node,
                  data: {
                    ...node.data,
                    attributes: {
                      ...node.data.attributes,
                      description: form.getFieldValue('description'),
                    },
                    isVerification,
                  },
                };
              } else {
                return node;
              }
            });
          });
        }}
      >
        <Collapse
          bordered={false}
          style={{
            background: '#000a1a0a',
          }}
          defaultActiveKey={['names']}
        >
          <Panel
            key={'names'}
            header={
              <span style={{ fontWeight: '700' }}>
                回答内容&nbsp;
                <Tooltip title="最终输出的结论">
                  <QuestionCircleOutlined
                    style={{ fontSize: 11, color: '#525964' }}
                  />
                </Tooltip>
              </span>
            }
          >
            <Divider
              style={{ margin: '-12px 0 12px', borderColor: '#d6d8da' }}
            />
            <Form.Item
              rules={[{ required: true, message: '请输入内容' }]}
              name="description"
              style={{ marginBottom: '0px' }}
            >
              <TextArea
                className="nowheel"
                autoSize={{ minRows: 4, maxRows: 12 }}
              />
            </Form.Item>
          </Panel>
        </Collapse>
        {/* <div className="summarize-switch">
          <div>
            是否输入推理过程总结&nbsp;
            <Tooltip title="是否将模型中间的推理过程也输出在结论总结里">
              <QuestionCircleOutlined
                style={{ fontSize: 11, color: '#525964' }}
              />
            </Tooltip>
          </div>
          <div style={{ paddingTop: 20 }}>
            <Form.Item valuePropName="checked" name="switch">
              <Switch size="small" />
            </Form.Item>
          </div>{' '}
        </div> */}
        <ExecutionConditions
          accesscriteria={accesscriteria}
          setNodes={setNodes}
          form={form}
          nodeId={props.id}
        />
      </Form>
    </NodeContainer>
  );
};
