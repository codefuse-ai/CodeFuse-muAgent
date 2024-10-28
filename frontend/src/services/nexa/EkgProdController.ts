/* eslint-disable */
// 该文件由 OneAPI 自动生成，请勿手动修改！
import { request } from '@umijs/max';

/** 根据节点ID查询图谱(内层图谱)
@param nodeId 节点ID
@return 图谱(内层图谱)
 GET /api/ekg/prod/graph/node */
export async function getGraphByNode(
  params: {
    // query
    /** 节点ID */
    nodeId?: string;
    nodeType?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_GGraph_>('/api/ekg/prod/graph/node', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 根据团队ID查询图谱(外层图谱)
@param teamId 团队ID
@return 团队图谱(外层图谱)
 GET /api/ekg/prod/graph/team */
export async function getGraphByTeam(
  params: {
    // query
    /** 团队ID */
    teamId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_GGraph_>('/api/ekg/prod/graph/team', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 获取节点详情
@param nodeId 节点ID
@return 节点详情
 GET /api/ekg/prod/node */
export async function getNode(
  params: {
    // query
    /** 节点ID */
    nodeId?: string;
    nodeType?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_GNode_>('/api/ekg/prod/node', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 根据节点ID查询祖先链路
@param teamId 团队ID
@param nodeId 节点ID
@return 祖先链路
 GET /api/ekg/prod/graph/ancestor */
export async function getNodeAncestor(
  params: {
    // query
    /** 团队ID */
    teamId?: string;
    /** 节点ID */
    nodeId?: string;
    nodeType?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_GGraph_>('/api/ekg/prod/graph/ancestor', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 从语雀文档导入EKG
@param request
@return 
 POST /api/ekg/prod/graph/import/yuque */
export async function importByYuque(
  body?: NEXA_API.GraphImportByYuqueRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_String_>('/api/ekg/prod/graph/import/yuque', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 查询EKG导入任务状态
@param teamId
@param taskId
@return 任务状态
 GET /api/ekg/prod/graph/import/task/status */
export async function importTaskStatus(
  params: {
    // query
    teamId?: string;
    taskId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_String_>(
    '/api/ekg/prod/graph/import/task/status',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 节点搜索
@param teamId 团队ID
@param text 搜索文本
@return 搜索结果
 GET /api/ekg/prod/node/search */
export async function searchNode(
  params: {
    // query
    /** 团队ID */
    teamId?: string;
    /** 搜索文本 */
    text?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_List_GNode__>('/api/ekg/prod/node/search', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 查询团队运行中的EKG导入任务
@param teamId
@return 运行中的task
 GET /api/ekg/prod/graph/import/team/taskDetail */
export async function teamImportTaskDetail(
  params: {
    // query
    teamId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_List_GraphImportTaskDetail__>(
    '/api/ekg/prod/graph/import/team/taskDetail',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 查询团队运行中的EKG导入任务
@param teamId
@return 运行中的taskId
 GET /api/ekg/prod/graph/import/team/task */
export async function teamImportTasks(
  params: {
    // query
    teamId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_List_String__>(
    '/api/ekg/prod/graph/import/team/task',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 更新图谱数据
@param request 请求参数
@return 
 POST /api/ekg/prod/graph/update */
export async function updateGraph(
  body?: NEXA_API.GraphUpdateRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_GGraph_>('/api/ekg/prod/graph/update', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}
