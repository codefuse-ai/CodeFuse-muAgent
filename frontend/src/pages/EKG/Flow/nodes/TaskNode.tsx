import { Form, Input } from 'antd';
import React, { useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import ExecutionConditions from '../components/ExecutionConditions';
import NodeHeader from '../components/NodeHeader';
import { NodeContainer } from './style';
const { TextArea } = Input;
interface IProps {
  id: string;
  data: {
    description: string;
    setNodes: (nodes: any) => void;
    accesscriteria: string;
    attributes: any;
  };
}
export default (props: IProps) => {
  const [form] = Form.useForm();
  const { data } = props;
  const { setNodes, attributes } = data;
  const { accesscriteria } = attributes;
  useEffect(() => {
    form.setFieldsValue({ description: attributes?.description });
  }, [attributes?.description]);
  return (
    <NodeContainer>
      <NodeHeader
        moduleData={props}
        icon="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*yAbSSbagshMAAAAAAAAAAAAADprcAQ/original"
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
      <Handle
        type="source"
        style={{
          width: '12px',
          height: '12px',
          background: '#bdc0c4',
        }}
        id={props?.id}
        position={Position.Right}
      />
      <div>
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
          <Form.Item
            name="description"
            style={{ marginBottom: '0px' }}
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <TextArea
              className="nowheel"
              autoSize={{ minRows: 4, maxRows: 12 }}
            />
          </Form.Item>

          <ExecutionConditions
            accesscriteria={accesscriteria}
            setNodes={setNodes}
            form={form}
            nodeId={props.id}
          />
        </Form>
      </div>
    </NodeContainer>
  );
};
