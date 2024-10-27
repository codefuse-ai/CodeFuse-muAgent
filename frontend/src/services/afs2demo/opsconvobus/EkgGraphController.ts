/* eslint-disable */
import { request } from '@umijs/max';

/** 展示EKG运行时的树形(意图+操作计划)节点
@param conversationId
@return 
 GET /v1/opsconvobus/ekgGraph/intentTree */
export async function intent(
  params: {
    // query
    conversationId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<Record<string, any>>('/v1/opsconvobus/ekgGraph/intentTree', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'opsconvobus',
    ...(options || {}),
  });
}

/** POST /v1/opsconvobus/ekgGraph/query */
export async function query(body?: any, options?: { [key: string]: any }) {
  return request<Record<string, any>>('/v1/opsconvobus/ekgGraph/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    // @ts-ignore
    appName: 'opsconvobus',
    ...(options || {}),
  });
}
