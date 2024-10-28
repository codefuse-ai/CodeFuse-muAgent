import { EKGFlowState } from '@/pages/EKG/store';
import { history, useParams, useSnapshot } from '@umijs/max';
import {
  ArrowRightOutlined,
  CloseOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import { Button, Form, Input, Space, Switch, Tooltip } from 'antd';
import React, { useEffect, useState } from 'react';
import ModalFlow from '../../Flow';
import SceneModalInfo from './SceneModalInfo';
import { Container, FlowWrapperDrawer } from './style';
interface IProps {
  setNodes: (nodes: any) => void;
}
const { TextArea } = Input;
export default (props: IProps) => {
  // 获取图谱数据
  const detailData = useSnapshot(EKGFlowState);
  const { setNodes } = props;
  const [nodeData, setNodeData] = useState({});
  const [form] = Form.useForm();

  const { ekgId } = useParams();
  /* 
  编辑保存节点详情
  */
  const save = () => {
    form.validateFields().then((values) => {
      setNodes((nodes) => {
        return nodes?.map((node) => {
          if (node.id === nodeData.id) {
            return {
              ...node,
              data: {
                ...node.data,
                attributes: {
                  ...node.data.attributes,
                  ...values,
                },
              },
            };
          }
          return node;
        });
      });
      EKGFlowState.nodeDetailOpen = false;
      EKGFlowState.nodeDetailData = {};
    });
  };
  useEffect(() => {
    console.log('节点面板data>>>', detailData.nodeDetailData.data);
    setNodeData(detailData.nodeDetailData.data);
    form.setFieldsValue(detailData.nodeDetailData.data);
  }, [detailData.nodeDetailData]);

  return (
    detailData.nodeDetailOpen && (
      <Container>
        <div className="header">
          <div
            className="close"
            onClick={() => {
              EKGFlowState.nodeDetailOpen = false;
              EKGFlowState.nodeDetailData = {};
            }}
          >
            <CloseOutlined />
          </div>
          <div
            className="icon"
            style={{
              background:
                nodeData.type === 'operationPlanNode' ? '#5dbb30' : '#5272e0',
            }}
          ></div>
          <div className="title">
            {' '}
            {nodeData.type === 'operationPlanNode'
              ? '操作计划节点'
              : '场景意图节点'}
          </div>
          <div className="save">
            <Button className="save-button" onClick={save} type="primary">
              保存
            </Button>
          </div>
        </div>
        <div className="content">
          <Form form={form} layout="vertical">
            <Form.Item
              rules={[{ required: true, message: '请输入节点名称' }]}
              label="节点名称"
              name="name"
            >
              <Input placeholder="请输入节点名称" maxLength={20} />
            </Form.Item>
            <Form.Item
              rules={[{ required: true, message: '请输入描述' }]}
              label={
                <Space>
                  <span>描述</span>
                  {nodeData.type !== 'operationPlanNode' && (
                    <Tooltip
                      title={
                        nodeData.type === 'operationPlanNode'
                          ? '描述文字'
                          : '用来描述该场景的意图，一般需要写详细的意图，方便大模型匹配用户意图'
                      }
                    >
                      <QuestionCircleOutlined style={{ cursor: 'pointer' }} />
                    </Tooltip>
                  )}
                </Space>
              }
              name="description"
            >
              <TextArea
                autoSize={{ minRows: 4, maxRows: 4 }}
                placeholder="请输入描述"
              />
            </Form.Item>
            {nodeData.type === 'sceneNode' && <SceneModalInfo />}
            {nodeData.type === 'operationPlanNode' && (
              <Form.Item label="编排流程">
                <FlowWrapperDrawer
                  onClick={() => {
                    history.push(
                      `./${ekgId}/flow/${encodeURIComponent(nodeData?.id)}`,
                    );
                  }}
                >
                  <div className="flowWrapper" key={nodeData?.id}>
                    <ModalFlow flowType="chidren" id={nodeData?.id} />
                    <div className="flowMask">
                      <span>点击进入流程编排视图</span>&nbsp;
                      <ArrowRightOutlined />
                    </div>
                  </div>
                </FlowWrapperDrawer>
              </Form.Item>
            )}
            {nodeData.type === 'operationPlanNode' && (
              <div
                style={{
                  padding: '4px 8px 0 0',
                  float: 'left',
                }}
              >
                是否执行该操作计划
              </div>
            )}
            {nodeData.type === 'operationPlanNode' && (
              <Form.Item name="enable" valuePropName="checked">
                <Switch />
              </Form.Item>
            )}
          </Form>
        </div>
      </Container>
    )
  );
};
