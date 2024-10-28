import { searchNode as queryNode } from '@/services/nexa/EkgProdController';
import { SearchOutlined } from '@ant-design/icons';
import { useParams, useRequest } from '@umijs/max';
import { Input, message, Spin } from 'antd';
import React from 'react';
import { EKGFlowState } from '../../store';

const SearchNode = () => {
  const { spaceId } = useParams();

  /**
   * 搜索节点
   */
  const queryNodeInfo = useRequest(queryNode, {
    manual: true,
    formatResult: (res) => res,
    onSuccess: (res) => {
      if (res?.success) {
        EKGFlowState.nodeActionList = {
          type: 'search',
          data: {
            nodes: res?.data || [],
          },
        };
      } else {
        message.error(res?.errorMessage);
      }
    },
  });

  return (
    <Spin spinning={queryNodeInfo.loading}>
      <Input
        size="large"
        allowClear
        placeholder="搜索节点名称"
        prefix={<SearchOutlined />}
        style={{ width: '320px' }}
        onPressEnter={(e: React.KeyboardEvent<HTMLInputElement>) => {
          queryNodeInfo.run({
            teamId: spaceId,
            text: (e.target as HTMLInputElement).value,
          });
        }}
        onChange={(e) => {
          if (e.target.value === '') {
            EKGFlowState.nodeActionList = {
              type: '',
              data: {},
            };
          }
        }}
      />
    </Spin>
  );
};

export default SearchNode;
