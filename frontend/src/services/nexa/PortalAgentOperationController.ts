/* eslint-disable */
// 该文件由 OneAPI 自动生成，请勿手动修改！
import { request } from '@umijs/max';

/** 创建agent
@param agentInfoVO agent信息
@return portal agentId
 POST /api/portal/agent/add */
export async function addAgent(
  body?: NEXA_API.AgentInfoVO,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_String_>('/api/portal/agent/add', {
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

/** agent调试
@param agentDebugRequest agent调试请求体
@return agent调试响应体列表
 POST /api/portal/agent/chat/debug */
export async function agentDebug(
  body?: NEXA_API.AgentDebugRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_List_AitorAgentDebugResponse__>(
    '/api/portal/agent/chat/debug',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 分页查询个人空间下的agent信息
@param pageRequest 分页查询请求
@param request HTTP 请求对象
@param response HTTP 响应对象
@return agent列表
 POST /api/portal/agent/agentInfoPage */
export async function agentInfoPage(
  body?: NEXA_API.AgentInfoPageRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_PageResultList_AgentInfoVO__>(
    '/api/portal/agent/agentInfoPage',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 分页查询空间下的agent信息
@param pageRequest 分页查询请求
@param request HTTP 请求对象
@param response HTTP 响应对象
@return agent列表
 POST /api/portal/agent/queryAgentPageBySpaceId */
export async function agentPageBySpaceId(
  body?: NEXA_API.AgentInfoPageRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_PageResultList_AgentInfoVO__>(
    '/api/portal/agent/queryAgentPageBySpaceId',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** code节点调试
@param codeDebugRequest code调试请求
@return 调试结果
 POST /api/portal/agent/code/debug */
export async function codeDebug(
  body?: NEXA_API.CodeDebugRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Map_String_Object__>(
    '/api/portal/agent/code/debug',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 通过模板创建 agent
@param templateType 模板类型
@param spaceId 空间 id
@return 
 POST /api/portal/agent/${param0}/${param1} */
export async function createTemplateAgent(
  params: {
    // path
    /** 构建详情枚举 */
    templateType?: NEXA_API.BuildDetailEnum;
    /** 空间 id */
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  const { templateType: param0, spaceId: param1 } = params;
  return request<NEXA_API.Result_String_>(
    `/api/portal/agent/${param0}/${param1}`,
    {
      method: 'POST',
      params: { ...params },
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 此处后端没有提供注释 POST /api/portal/agent/relatedTool */
export async function createToolRelation(
  body?: NEXA_API.CreateToolRelationRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_String_>('/api/portal/agent/relatedTool', {
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

/** 场景agent信息删除
@param agentId agentId
@param spaceId 空间id
@return 删除结果
 DELETE /api/portal/agent/delete */
export async function deleteAgentById(
  params: {
    // query
    /** agentId */
    agentId?: string;
    /** 空间id */
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/agent/delete', {
    method: 'DELETE',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 此处后端没有提供注释 POST /api/portal/agent/cancelRelatedTool */
export async function deleteToolRelation(
  params: {
    // query
    agentId?: string;
    relationId?: string;
    taskType?: NEXA_API.TaskTypeEnum;
    bindingKey?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/agent/cancelRelatedTool',
    {
      method: 'POST',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 导入用户在灵思创建的agent
@param request
@return 
 POST /api/portal/agent/importOpsGPTAgent */
export async function importOpsGPTAgent(
  body?: NEXA_API.AgentImportRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/agent/importOpsGPTAgent',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 批量导入公共agent
@param agentInfoVOList 公共agent列表
@return 导入结果
 POST /api/portal/agent/importPublicAgents */
export async function importPublicAgents(
  body?: Array<NEXA_API.AgentInfoVO>,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/agent/importPublicAgents',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** LLM列表查询
@return 返回LLM列表查询结果
 GET /api/portal/agent/llm/list */
export async function llmList(options?: { [key: string]: any }) {
  return request<NEXA_API.Result_List_LlmResponse__>(
    '/api/portal/agent/llm/list',
    {
      method: 'GET',
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** Prompt 优化
@param promptRequest Prompt请求对象
@return 返回处理结果
 POST /api/portal/agent/nl2agent */
export async function nl2agent(
  body?: NEXA_API.PromptRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_String_>('/api/portal/agent/nl2agent', {
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

/** Code+ 代码生成
@param generateCodeRequest 生成代码请求
@return 生成的脚本内容
 POST /api/portal/agent/nl2script */
export async function nl2script(
  body?: NEXA_API.GenerateCodeRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_ScriptContent_>(
    '/api/portal/agent/nl2script',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 发布 agent 到插件
@param agentId agentId
@param spaceId 空间id
@return 返回结果状态码和消息
 GET /api/portal/agent/publish */
export async function publish(
  params: {
    // query
    /** agentId */
    agentId?: string;
    /** 空间id */
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/agent/publish', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 根据agentId查询agent详细信息
@param queryAgentDetailInfoRequest session创建请求体
@return 返回agent列表
 POST /api/portal/agent/queryAgentDetailInfo */
export async function queryAgentDetailInfo(
  body?: NEXA_API.QueryAgentDetailInfoRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_AgentDetailInfoVO_>(
    '/api/portal/agent/queryAgentDetailInfo',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 根据agentId查询agent基本信息
@param queryAgentInfoRequest session创建请求体
@return 返回agent列表
 POST /api/portal/agent/queryAgentInfo */
export async function queryAgentInfo(
  body?: NEXA_API.QueryAgentInfoRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_AgentInfoVO_>(
    '/api/portal/agent/queryAgentInfo',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'nexa',
      ...(options || {}),
    },
  );
}

/** 查询agent列表
@return 返回agent列表
 POST /api/portal/agent/queryList */
export async function queryList(
  params: {
    // query
    name?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_List_AgentInfoVO__>(
    '/api/portal/agent/queryList',
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

/** 发布agent
@param request 发布agent请求信息
@return 发布结果
 POST /api/portal/agent/release */
export async function releaseAgent(
  body?: NEXA_API.ReleaseAgentRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/agent/release', {
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

/** statusPolling 接口
@param agentId 代理ID
@param spaceId 空间ID
@return 返回一个Result对象，包含一个Map<String, Object>对象
 GET /api/portal/agent/observation/statusPolling */
export async function statusPolling(
  params: {
    // query
    /** 代理ID */
    agentId?: string;
    /** 空间ID */
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Map_String_Object__>(
    '/api/portal/agent/observation/statusPolling',
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

/** 将个人空间下的agent转移到团队空间
@param portalAgentId 个人空间下的agent ID
@param spaceId 团队空间ID
@return 转移结果，成功返回true，失败返回false
 POST /api/portal/agent/transfer */
export async function transferAgentToGroup(
  params: {
    // query
    /** 个人空间下的agent ID */
    portalAgentId?: string;
    /** 团队空间ID */
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/agent/transfer', {
    method: 'POST',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 撤销 agent 发布
@param agentId agentId
@param spaceId 空间id
@return 返回结果状态码和消息
 GET /api/portal/agent/unpublish */
export async function unPublish(
  params: {
    // query
    /** agentId */
    agentId?: string;
    /** 空间id */
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/agent/unpublish', {
    method: 'GET',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 更新agent信息
@param agentInfoVO agent信息
@return 更新结果
 POST /api/portal/agent/update */
export async function updateAgentByAgentId(
  body?: NEXA_API.AgentInfoVO,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/agent/update', {
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

/** 修改agent信息(同步修改下游)
@param agentDetailInfoVO agent信息
@return 更新结果
 POST /api/portal/agent/modify */
export async function updateAgentById(
  body?: NEXA_API.AgentModifyRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/agent/modify', {
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
