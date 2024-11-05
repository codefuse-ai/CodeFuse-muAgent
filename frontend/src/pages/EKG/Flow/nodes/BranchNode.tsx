import { dataToJson } from '../../utils/format';
import React, { useEffect } from 'react';
import { Form, Input } from 'antd';
import { Handle, Position } from 'reactflow';
import NodeHeader from '../components/NodeHeader';
import { NodeContainer } from './style';

const BranchNode = (props: any) => {
  const [form] = Form.useForm();
  const { TextArea } = Input;
  const { attributes } = props?.data;
  const { description } = attributes;

  useEffect(() => {
    form.setFieldsValue({ description });
  }, [dataToJson(props?.data)?.data]);

  return (
    <NodeContainer>
      <NodeHeader
        moduleData={props}
        icon="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*kq5pRbKCVdEAAAAAAAAAAAAADprcAQ/original"
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
      <Form
        form={form}
        onBlur={() => {
          form
            .validateFields()
            .then((values) => {
              props?.data?.setNodes((nodes) => {
                return nodes.map((node) => {
                  if (node.id === props.id) {
                    return {
                      ...node,
                      data: {
                        ...node.data,
                        attributes: {
                          ...node.data.attributes,
                          description: values.description,
                        },
                        isVerification: true,
                      },
                    };
                  } else {
                    return node;
                  }
                });
              });
            })
            .catch(() => {
              props?.data?.setNodes((nodes) => {
                return nodes.map((node) => {
                  if (node.id === props.id) {
                    return {
                      ...node,
                      data: { ...node.data, isVerification: false },
                    };
                  } else {
                    return node;
                  }
                });
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
            autoSize={{ minRows: 4, maxRows: 12 }}
            placeholder="请用自然语言描述您的判断条件"
          />
        </Form.Item>
      </Form>
    </NodeContainer>
  );
};

export default BranchNode;
