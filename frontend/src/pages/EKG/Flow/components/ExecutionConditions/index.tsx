import { safeJsonParse } from '@/pages/EKG/utils';
import { useSnapshot } from '@umijs/max';
import { Col, Collapse, Form, Radio, Row } from 'antd';
import React, { useEffect } from 'react';
import { EKGChildFlowState } from '../../store';
import { ExecutionConditionsWrapper } from './style';

interface IProps {
  setNodes: any;
  nodeId: string;
  accesscriteria?: string;
  form: any;
}

/**
 * 执行条件组件
 * @returns
 */
const ExecutionConditions: React.FC<IProps> = (props) => {
  const { nodeId, setNodes, form, accesscriteria } = props;
  // 图谱数据
  const flowSnap = useSnapshot(EKGChildFlowState);
  // 当前节点的输入边
  const currentEdges = flowSnap?.currentGraphData?.edges?.filter(
    (item) => item?.target === nodeId,
  );

  /**
   * 条件选择改变
   */
  const handleChange = (type?: string) => {
    const currentAccesscriteria = JSON.stringify({
      type,
    });
    setNodes((nodes: any[]) => {
      return nodes?.map((item) => {
        if (item?.id === nodeId) {
          return {
            ...item,
            data: {
              ...item?.data,
              attributes: {
                ...item?.data?.attributes,
                accesscriteria: type ? currentAccesscriteria : '',
              },
            },
          };
        }
        return item;
      });
    });
  };

  useEffect(() => {
    if (currentEdges?.length > 1) {
      let type = 'AND';
      if (accesscriteria) {
        type = safeJsonParse(accesscriteria).type;
        type = type === 'OR' ? type : 'AND';
      }
      // 条件执行赋值
      form.setFieldValue(['accesscriteria', 'type'], type);
      handleChange(type);
    } else {
      // 条件执行赋值
      form.setFieldValue(['accesscriteria', 'type'], '');
      handleChange();
    }
  }, [flowSnap?.currentGraphData?.edges]);

  // 节点少于两条输入连接边时不展示
  if (!(currentEdges?.length > 1)) {
    return null;
  }

  /**
   * 条件选择
   */
  const conditions = [
    {
      label: '所有上级节点满足时执行',
      value: 'AND',
    },
    {
      label: '任意上级节点满足时执行',
      value: 'OR',
    },
    // {
    //   label: '指定上级节点满足时执行',
    //   value: 'DSL',
    // },
  ];

  /**
   * 表单渲染
   * @returns
   */
  const renderConditions = () => {
    return (
      <div>
        <Form.Item
          name={['accesscriteria', 'type']}
          className="conditions-radio"
          initialValue={'AND'}
        >
          <Radio.Group
            onChange={(e) => {
              const type = e.target?.value;
              handleChange(type);
            }}
          >
            <Row gutter={[0, 8]}>
              {conditions?.map((item) => {
                return (
                  <Col
                    span={24}
                    key={item.value}
                    className="conditions-radio-item"
                  >
                    <Radio value={item.value} key={item.value}>
                      {item.label}
                    </Radio>
                  </Col>
                );
              })}
            </Row>
          </Radio.Group>
        </Form.Item>
      </div>
    );
  };

  const items = [
    {
      key: 'condition',
      label: <span>节点执行条件</span>,
      children: renderConditions(),
      forceRender: true,
    },
  ];

  return (
    <>
      <ExecutionConditionsWrapper>
        <Collapse
          bordered={false}
          items={items}
          defaultActiveKey={['condition']}
        />
      </ExecutionConditionsWrapper>
    </>
  );
};

export default ExecutionConditions;
