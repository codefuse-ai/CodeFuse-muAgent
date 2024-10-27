import { EKGFlowState } from '@/pages/EKG/store';
import { getNodeAncestor } from '@/services/nexa/EkgProdController';
import { useRequest } from '@umijs/max';
import { useEffect } from 'react';

interface AncestorParams {
  teamId: string;
  nodeId: string;
  nodeType: 'opsgptkg_intent' | 'opsgptkg_schedule';
}

export const useSearchAncestor = (
  params: AncestorParams,
  callback?: (res: any) => void,
) => {
  const { run, data, error, loading, cancel } = useRequest(getNodeAncestor, {
    manual: true,
  });

  const searchAncestor = () => {
    run(params);
  };

  useEffect(() => {
    if (data) {
      if (callback) {
        callback(data);
      }
      console.log('data<<', data);
      EKGFlowState.nodeActionList = {
        type: 'select',
        data,
      };
    }
  }, [data, callback]);

  useEffect(() => {
    if (error) {
      console.error('节点搜索出错:', error);
    }
  }, [error]);

  useEffect(() => {
    cancel();
  }, []);

  return { searchAncestor, loading, data };
};
