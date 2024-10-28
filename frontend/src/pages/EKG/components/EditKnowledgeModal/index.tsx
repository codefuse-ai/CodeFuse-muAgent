import { hasKnowledgeBaseByType } from '@/services/nexa/PortalKnowledgeController';
import { useParams, useRequest } from '@umijs/max';
import {
  Button,
  Card,
  Col,
  Flex,
  Form,
  Input,
  message,
  Radio,
  Row,
  Space,
  Tooltip,
} from 'antd';
import React, { useEffect, useState } from 'react';
import { EditKnowledgeModalWrapper } from './style';

interface IPops {
  open: boolean;
  handleSubmit: any;
  setOpen: (open: boolean) => void;
  knowledgeData?: any;
}
const CreateKnowledgeModal: React.FC<IPops> = (props) => {
  const { open, handleSubmit, setOpen, knowledgeData } = props;
  const [form] = Form.useForm();
  // 监听name字段的变化
  const nameValue = Form.useWatch('name', form);
  const { spaceId } = useParams();
  // 当前选中的知识库模式
  const [selectedKnowledgeMode, setSelectedKnowledgeMode] =
    useState<string>('EKG');
  // 空间中是否已经添加过EKG模式知识库
  const [isEKGKnowledge, setIsEKGKnowledge] = useState(false);

  /**
   * 查询是否创建过ekg知识
   */
  const handleQueryEKGKnowledge = useRequest(hasKnowledgeBaseByType, {
    manual: true,
    formatResult: (res) => res,
    onSuccess: (res) => {
      if (res?.success) {
        setIsEKGKnowledge(res?.data);
      } else {
        message.error(res?.errorMessage);
      }
    },
  });

  /**
   * 关闭弹窗
   */
  const handleCancel = () => {
    setOpen(false);
  };

  /**
   * 创建
   */
  const handleCreate = () => {
    form.validateFields().then((values) => {
      const params = {
        ...values,
        spaceId,
        source: 'OPSGPT',
        type: selectedKnowledgeMode,
      };
      const updateParams = {
        ...values,
        id: knowledgeData?.id,
        spaceId,
      };
      // 编辑
      if (knowledgeData?.id) {
        handleSubmit?.run(updateParams);
      } else {
        // 新增
        handleSubmit?.run(params);
      }
    });
  };

  // 知识库模式
  const knowledgeMode = [
    {
      key: 'EKG',
      title: '知识图谱EKG模式',
      description: '通过将知识存储为知识图谱，大模型结合知识图谱检索知识',
      icon: 'https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*3tR1Qr_eh0cAAAAAAAAAAAAADprcAQ/original',
    },
  ];

  /**
   * 知识库模式是否禁用
   */
  const knowledgeDisabled = (key: string) => {
    return key === 'EKG' && isEKGKnowledge;
  };

  useEffect(() => {
    if (open) {
      handleQueryEKGKnowledge?.run({
        spaceId,
        type: 'EKG',
      });
    }
    if (open && knowledgeData?.id) {
      form.setFieldsValue(knowledgeData);
      setSelectedKnowledgeMode(knowledgeData?.type);
    }

    // 关闭弹窗时清空
    if (!open) {
      form.resetFields();
    }
  }, [open]);

  return (
    <EditKnowledgeModalWrapper
      title={knowledgeData?.id ? '编辑知识' : '创建知识'}
      open={open}
      onCancel={handleCancel}
      maskClosable={false}
      centered
      width={768}
      destroyOnClose
      footer={[
        <Button key="back" onClick={handleCancel}>
          取消
        </Button>,
        <Button
          style={{
            background: '#1b62ff',
            opacity: !nameValue ? 0.4 : 1,
            color: '#fff',
          }}
          key="submit"
          type="primary"
          loading={handleSubmit?.loading}
          onClick={handleCreate}
          disabled={!nameValue || isEKGKnowledge}
        >
          {knowledgeData?.id ? '确认' : '创建'}
        </Button>,
      ]}
    >
      <>
        <Form form={form} layout="vertical">
          <div>
            <div style={{ marginBottom: '8px', marginTop: '24px' }}>
              <span
                style={{ color: '#ff4d4f', fontFamily: 'SimSun, sans-serif' }}
              >
                *{' '}
              </span>
              知识库模式
            </div>
            <Radio.Group
              name="radiogroup"
              value={selectedKnowledgeMode}
              disabled={knowledgeData?.id}
              style={{ width: '100%' }}
            >
              <Row gutter={16}>
                {knowledgeMode?.map((item) => {
                  return (
                    <Col span={8} key={item.key}>
                      <Tooltip
                        title={
                          knowledgeDisabled(item.key)
                            ? '已经创建过团队知识图谱，可在知识列表中查看'
                            : ''
                        }
                        overlayStyle={{
                          maxWidth: '310px',
                        }}
                      >
                        <Card
                          className={`${
                            selectedKnowledgeMode === item.key
                              ? 'mode-item mode-item-active'
                              : 'mode-item'
                          }`}
                          style={{
                            cursor: knowledgeDisabled(item.key)
                              ? 'not-allowed'
                              : 'pointer',
                          }}
                          hoverable
                          onClick={() => {
                            if (knowledgeDisabled(item.key)) {
                              return;
                            }
                            if (!knowledgeData?.id) {
                              setSelectedKnowledgeMode(item.key);
                            }
                          }}
                        >
                          <Flex justify={'space-between'} align={'center'}>
                            <Space>
                              <img width={32} height={32} src={item.icon} />
                              <span className="mode-item-title">
                                {item.title}
                              </span>
                            </Space>
                            <Radio
                              value={item.key}
                              disabled={
                                knowledgeDisabled(item.key) || knowledgeData?.id
                              }
                            />
                          </Flex>
                          <div className="mode-item-description">
                            {item.description}
                          </div>
                        </Card>
                      </Tooltip>
                    </Col>
                  );
                })}
              </Row>
            </Radio.Group>
          </div>
          <Form.Item
            name={'name'}
            rules={[{ required: true, message: '请输入名称' }]}
            className="create-modal-name"
            label="名称"
          >
            <Input placeholder="请输入名称（必填）" showCount maxLength={50} />
          </Form.Item>
          <Form.Item name={'description'} label="描述">
            <Input.TextArea placeholder="请输入知识库的相关描述" />
          </Form.Item>
        </Form>
      </>
    </EditKnowledgeModalWrapper>
  );
};

export default CreateKnowledgeModal;
