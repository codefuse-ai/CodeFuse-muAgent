/* eslint-disable */
// 该文件由 OneAPI 自动生成，请勿手动修改！
import { request } from '@umijs/max';

/** 增加会话
@param sessionRecord
@return 
 POST /api/conversation/addSession */
export async function addSession(
  body?: OPSGPT_API.SessionRecord,
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_SessionRecord_>(
    '/api/conversation/addSession',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 获取与用户关联的 agent 列表
@return 
 GET /api/conversation/agents */
export async function agents(options?: { [key: string]: any }) {
  return request<OPSGPT_API.BaseResult_List_Agent__>(
    '/api/conversation/agents',
    {
      method: 'GET',
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 清除记忆
@param sessionId
@return 
 GET /api/conversation/clearMemory */
export async function clearMemory(
  params: {
    // query
    sessionId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_Integer_>(
    '/api/conversation/clearMemory',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 逻辑删除会话
@param sessionId
@return 
 GET /api/conversation/delSession */
export async function delSession(
  params: {
    // query
    sessionId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_Integer_>(
    '/api/conversation/delSession',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 此处后端没有提供注释 DELETE /api/conversation/session/agent/${param0} */
export async function delSessionByAgent(
  params: {
    // path
    agentId?: string;
  },
  options?: { [key: string]: any },
) {
  const { agentId: param0 } = params;
  return request<OPSGPT_API.BaseResult_Integer_>(
    `/api/conversation/session/agent/${param0}`,
    {
      method: 'DELETE',
      params: { ...params },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 反馈
@param feedBack
@return 
 POST /api/conversation/feedBack */
export async function feedBack(
  body?: OPSGPT_API.FeedBack,
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_FeedBack_>(
    '/api/conversation/feedBack',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 此处后端没有提供注释 POST /api/conversation/ekgGraph/query */
export async function query(
  body?: OPSGPT_API.EkgGraphRequest,
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.ServiceResult_EkgGraphInfoVo_>(
    '/api/conversation/ekgGraph/query',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 查询消息的反馈信息
@param msgId
@return 
 GET /api/conversation/queryFeedBacksByMsgId */
export async function queryFeedBacksByMsgId(
  params: {
    // query
    msgId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_List_FeedBack__>(
    '/api/conversation/queryFeedBacksByMsgId',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 查询消息
@param msgId
@return 
 GET /api/conversation/queryMsg */
export async function queryMsg(
  params: {
    // query
    msgId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_MsgRecord_>(
    '/api/conversation/queryMsg',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 查询消息列表
@param sessionId
@param pageNo
@param pageSize
@return 
 GET /api/conversation/queryMsgList */
export async function queryMsgList(
  params: {
    // query
    sessionId?: string;
    pageNo?: number;
    pageSize?: number;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BasePageResult_List_MsgRecord__>(
    '/api/conversation/queryMsgList',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 通过 id 集合查询查询关联的 msg id 为 msgRecord 的 id 字段，即消息的主键 id
@param idSet id 集合，":" 分隔，base64编码
@return 
 GET /api/conversation/queryMsgSet */
export async function queryMsgSet(
  params: {
    // query
    /** id 集合，":" 分隔，base64编码 */
    idSet?: string;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_List_MsgRecord__>(
    '/api/conversation/queryMsgSet',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 继续任务
@param msgId
@return 
 GET /api/conversation/resumeTask */
export async function resumeTask(
  params: {
    // query
    msgId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_Integer_>(
    '/api/conversation/resumeTask',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 发送信息
@param msgRecord
@return 
 POST /api/conversation/sendOpsMsg */
export async function sendOpsMsg(
  body?: OPSGPT_API.MsgRecord,
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_MsgRecord_>(
    '/api/conversation/sendOpsMsg',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 发送信息
@param msgRecord
@return 
 POST /api/conversation/sendOpsMsgWithType */
export async function sendOpsMsgWithType(
  body?: OPSGPT_API.MsgRecord,
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_MsgRecord_>(
    '/api/conversation/sendOpsMsgWithType',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 获取会话列表
@param request
@return 
 POST /api/conversation/sessionList */
export async function sessionList(
  body?: OPSGPT_API.ListSessionPageRequest,
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BasePageResult_List_SessionRecord__>(
    '/api/conversation/sessionList',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}

/** 停止任务
@param msgId
@return 
 GET /api/conversation/stopRespTask */
export async function stopRespTask(
  params: {
    // query
    msgId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<OPSGPT_API.BaseResult_Integer_>(
    '/api/conversation/stopRespTask',
    {
      method: 'GET',
      params: {
        ...params,
      },
      // @ts-ignore
      appName: 'opsgpt',
      ...(options || {}),
    },
  );
}
