/* eslint-disable */
// 该文件由 OneAPI 自动生成，请勿手动修改！
import { request } from '@umijs/max';

/** 对话chat
@param chatRequest @ApiOperation: 对话chat @SseEmitter: Server-Sent
    Events（SSE）是一种服务器发送事件的协议，它使服务器可以向客户端推送事件流。
@return: SseEmitter对象
 POST /api/portal/conversation/chat */
export async function chatPost(
  body?: NEXA_API.ChatRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.SseEmitter>('/api/portal/conversation/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    responseType: 'text/event-stream',
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 创建session
@param sessionCreateRequest session创建请求体
@param request HTTP请求对象
@param response HTTP响应对象
@return 返回创建的sessionId
 POST /api/portal/conversation/createSession */
export async function createSession(
  body?: NEXA_API.SessionCreateRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_String_>(
    '/api/portal/conversation/createSession',
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

/** 此处后端没有提供注释 DELETE /api/portal/conversation/deleteSessionList */
export async function deleteSessionList(
  body?: Array<NEXA_API.MsgRecordRequest>,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/conversation/deleteSessionList',
    {
      method: 'DELETE',
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

/** 此处后端没有提供注释 POST /api/portal/conversation/msgFeedback */
export async function msgFeedback(
  body?: NEXA_API.MsgFeedbackRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/conversation/msgFeedback',
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

/** 此处后端没有提供注释 GET /api/portal/conversation/queryMsgList */
export async function queryMsgList(
  params: {
    // query
    sessionId?: string;
    agentId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_List_NexaSessionMessageVO__>(
    '/api/portal/conversation/queryMsgList',
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

/** 此处后端没有提供注释 GET /api/portal/conversation/querySessionList */
export async function querySessionList(
  params: {
    // query
    userId?: string;
    pageSize?: number;
    currentPage?: number;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_PageResultList_NexaSessionVO__>(
    '/api/portal/conversation/querySessionList',
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

/** 此处后端没有提供注释 GET /api/portal/conversation/querySessionListByAgentId */
export async function querySessionListByAgentId(
  params: {
    // query
    agentId?: string;
    name?: string;
    pageNum?: number;
    pageSize?: number;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_PageResultList_NexaSessionVO__>(
    '/api/portal/conversation/querySessionListByAgentId',
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

/** 搜索session
@param request HTTP请求对象
@param response HTTP响应对象
@param q q
@param pageSize 页面大小
@param currentPage 当前页
@return 返回创建的sessionId
 GET /api/portal/conversation/searchSession */
export async function searchSession(
  params: {
    // query
    /** q */
    q?: string;
    /** 页面大小 */
    pageSize?: number;
    /** 当前页 */
    currentPage?: number;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_PageResultList_NexaSessionVO__>(
    '/api/portal/conversation/searchSession',
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

/** 此处后端没有提供注释 POST /api/portal/conversation/sessionFeedback */
export async function sessionFeedback(
  body?: NEXA_API.SessionFeedbackRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/conversation/sessionFeedback',
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

/** 更新session摘要
@param sessionUpdateRequest session更新请求体
@param request HTTP请求对象
@param response HTTP响应对象
@return 返回创建的sessionId
 PUT /api/portal/conversation/updateSession */
export async function updateSession(
  body?: NEXA_API.SessionUpdateRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/conversation/updateSession',
    {
      method: 'PUT',
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
