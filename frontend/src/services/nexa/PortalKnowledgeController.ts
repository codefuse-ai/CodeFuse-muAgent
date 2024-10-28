/* eslint-disable */
// 该文件由 OneAPI 自动生成，请勿手动修改！
import { request } from '@umijs/max';

/** 此处后端没有提供注释 POST /api/portal/knowledgeBase/add */
export async function addKnowledgeBase(
  body?: NEXA_API.KnowledgeBaseRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_String_>('/api/portal/knowledgeBase/add', {
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

/** 此处后端没有提供注释 DELETE /api/portal/knowledgeBase/delete */
export async function deleteKnowledgeBase(
  params: {
    // query
    spaceId?: string;
    id?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/knowledgeBase/delete', {
    method: 'DELETE',
    params: {
      ...params,
    },
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}

/** 根据下游知识库id查询知识库信息
@param knowledgeBaseIdList 下游知识库id
@return 知识库信息
 POST /api/portal/knowledgeBase/getByKnowledgeBase */
export async function getByKnowledgeBaseIdList(
  body?: Array<string>,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_List_NexaKnowledgeBaseVO__>(
    '/api/portal/knowledgeBase/getByKnowledgeBase',
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

/** 根据id获取知识库信息
@param id portal知识库id
@return 知识库信息
 GET /api/portal/knowledgeBase/get */
export async function getKnowledgeBaseById(
  params: {
    // query
    /** portal知识库id */
    id?: string;
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_NexaKnowledgeBaseVO_>(
    '/api/portal/knowledgeBase/get',
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

/** 根据id获取知识库信息
@param spaceId 空间 ID
@param type 知识库类型
@return true/false
 GET /api/portal/knowledgeBase/hasType */
export async function hasKnowledgeBaseByType(
  params: {
    // query
    /** 空间 ID */
    spaceId?: string;
    /** 知识库类型 */
    type?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/knowledgeBase/hasType',
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

/** 批量导入公共知识库
@param knowledgeBaseVOList 知识库信息列表
@return 操作结果
 POST /api/portal/knowledgeBase/importPublicKnowledge */
export async function importPublicKnowledge(
  body?: Array<NEXA_API.NexaKnowledgeBaseVO>,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/knowledgeBase/importPublicKnowledge',
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

const cookie =
  'ordv=XmtiYQwhBw..; antLoginLang=zh_CN; receive-cookie-deprecation=1; cna=T3HdHn9EAEsBASQBsYBY7WxC; ALIPAYCHAIRBUCJSESSIONID=7c44bd2b-0aff-4a5a-aa57-4e91b62b92c8; _hjSessionUser_1577352=eyJpZCI6IjJhYTE1ZDk1LTUzZTAtNWU0My04NmUzLTdjOWI2ZWY5YmMzNCIsImNyZWF0ZWQiOjE3MjI1ODc1NDUyNzQsImV4aXN0aW5nIjpmYWxzZX0=; userId=WB01362665; __TRACERT_COOKIE_bucUserId=WB01362665; session.cookieNameId=ALIPAYBUMNGJSESSIONID; ALIPAYBUMNGJSESSIONID=GZ00SCVXWtKiTcdis7OGkb8XFC5wodantbuserviceGZ00; LOCALE=zh_CN; IAM_TOKEN=eyJraWQiOiJkZWZhdWx0IiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ.eyJjbmwiOiJCVUMiLCJzdWIiOiJobHQwMTM2MjY2NSIsImF1dGhfdHAiOlsiWkZBUkIiXSwiaXNzIjoiYnVtbmcuYWxpcGF5LmNvbSIsIm5vbmNlIjoiN2I4NDhmNWQiLCJzaWQiOiI0MDUyMDI1IiwiZHZjIjoiO05PUk1BTDsiLCJhdWQiOiIqIiwibmJmIjoxNzI3MDczNzAxLCJzbm8iOiJXQjAxMzYyNjY1IiwidG50X2lkIjoiQUxJUFczQ04iLCJuYW1lIjoiaGx0MDEzNjI2NjUiLCJleHAiOjE3MjcxNjAxNjEsImlhdCI6MTcyNzA3Mzc2MSwianRpIjoiMjA2MzBlYTM4M2E3NDZlOTlhY2FlMjhlYmUyNjcyZWMifQ.QeDu40ODgGOwV-UA3ShnGhkjmm-DwI0m9jPD_5b9orlsiKqhi5xAKGx3AusD4Dwx68QNP4jhY0k4lfO4yLoJfQ; mustAddPartitionedTag=noNeedToAdd; bs_n_lang=zh_CN; ALIPAYDWDISSESSIONID=GZ00f25LGhTnMoWF95S9hzcdJSux9TcapGZ00; ctoken=W8ktF73bi6XBgZgg; isg=BCYn-ktmfEB47yhDw3Dq9PLBd5qoB2rBuVTIrxDAI8gEk5ysfpMB0Wch748fO2LZ';

/** 此处后端没有提供注释 GET /api/portal/knowledgeBase/pageSearch */
export async function pageSearchKnowledgeBase(
  params: {
    // query
    spaceId?: string;
    name?: string;
    creator?: string;
    pageNum?: number;
    pageSize?: number;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_PageResultList_NexaKnowledgeBaseVO__>(
    '/api/portal/knowledgeBase/pageSearch',
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

/** 将个人空间下的知识库转移到团队空间
@param portalKnowledgeBaseId 个人空间下的知识库ID
@param spaceId 团队空间ID
@return 转移结果
 GET /api/portal/knowledgeBase/transfer */
export async function transferKnowledgeToGroup(
  params: {
    // query
    /** 个人空间下的知识库ID */
    portalKnowledgeBaseId?: string;
    /** 团队空间ID */
    spaceId?: string;
  },
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>(
    '/api/portal/knowledgeBase/transfer',
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

/** 此处后端没有提供注释 PUT /api/portal/knowledgeBase/update */
export async function updateKnowledgeBase(
  body?: NEXA_API.KnowledgeBaseRequest,
  options?: { [key: string]: any },
) {
  return request<NEXA_API.Result_Boolean_>('/api/portal/knowledgeBase/update', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    // @ts-ignore
    appName: 'nexa',
    ...(options || {}),
  });
}
