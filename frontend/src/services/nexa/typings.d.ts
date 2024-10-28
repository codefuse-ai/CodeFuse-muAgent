/* eslint-disable */
// 该文件由 OneAPI 自动生成，请勿手动修改！

declare namespace NEXA_API {
  type AgentAttributeEnum = 'LLM' | 'BIZ';

  type AgentAuthority = 'AGENT_KNOWLEDGE' | 'AGENT_SPACE';

  interface AgentAuthorityDTO {
    /** agentID */
    agentId?: string;
    /** agentID */
    spaceId?: string;
    /** 域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
    /** 员工姓名 */
    lastName?: string;
    /** 员工花名 */
    nickNameCn?: string;
    /** 用户头像 */
    employeeAvatar?: string;
    /** 被授权用户域账号 */
    authorizedUserId?: string;
    /** 被授权用户域账号列表 */
    authorizedUserIdList?: Array<string>;
    /** 被授权的部门号列表 */
    deptNoList?: Array<string>;
    /** 授权角色@see com.alipay.nexa.service.authority.enums.AuthorityRoleEnum */
    role?: AuthorityRoleEnum;
    /** 查询类型 space/agent */
    type?: string;
  }

  type AgentAuthorityEnum = 'CREATOR' | 'ADMIN' | 'MEMBER' | 'SUPER_MANAGER';

  interface AgentAuthorityRequest {
    /** 每页大小 */
    pageSize: number;
    /** 当前页 */
    currentPage: number;
    /** agentID */
    agentId?: string;
    /** 空间id */
    spaceId?: string;
    /** 域账号 */
    userId?: string;
    /** 被授权用户域账号 */
    authorizedUserId?: string;
    /** 被授权用户域账号列表 */
    authorizedUserIdList?: Array<string>;
    /** 被授权的部门号列表 */
    deptNoList?: Array<string>;
    /** 授权角色@see com.alipay.nexa.service.authority.enums.AuthorityRoleEnum */
    role?: AuthorityRoleEnum;
  }

  interface AgentDebugRequest {
    /** portal-agentId */
    agentId?: string;
    /** 空间id */
    spaceId?: string;
    /** 内容 */
    content?: Record<string, any>;
    /** 输入参数 */
    injectParams?: Record<string, any>;
  }

  interface AgentDetailInfoVO {
    /** agentId */
    id?: number;
    /** AI推荐 */
    aiRecommend?: boolean;
    /** 下游agentId */
    agentId?: string;
    /** agent名称 */
    agentName?: string;
    /** agent类型 ● PUBLIC：公共 ● PRIVATE：私有 */
    agentType?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 头像 */
    avatar?: string;
    /** 构建类型 */
    buildType?: string;
    /** 构建类型信息 */
    buildTypeInfo?: string;
    /** 来源 */
    source?: string;
    /** agent属性 */
    agentAttribute?: string;
    /** 插件状态 */
    pluginStatus?: string;
    /** 空间id */
    spaceId?: string;
    /** 调试版本 */
    debugVersion?: string;
    /** 发布版本 */
    publishVersion?: string;
    /** 最后操作人 */
    lastModifyUser?: string;
    /** 创建人 */
    creator?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** 最后操作人花名 */
    lastModifyUserView?: string;
    /** 插件权限信息 */
    relationshipList?: Array<AgentAuthorityDTO>;
    /** agent关联关系 */
    agentRelationshipList?: Array<string>;
    /** 知识库关联关系 */
    knowledgeBaseRelationshipList?: Array<string>;
    /** 技能关联关系 */
    skillRelationshipList?: Array<string>;
    /** 是否展示开场白 */
    showPrologue?: boolean;
    /** 开场白 */
    prologue?: string;
    /** 开场白预设问题 */
    questionSample?: Array<string>;
    /** 扩展信息 */
    extendContext?: Record<string, any>;
    /** agent配置 */
    agentConfig?: Record<string, any>;
  }

  interface AgentImportRequest {
    /** 用户域账号列表 */
    userIdList?: Array<string>;
  }

  interface AgentInfoPageRequest {
    /** 每页大小 */
    pageSize: number;
    /** 当前页 */
    currentPage: number;
    /** 域账号 */
    userId?: string;
    /** agent名称 */
    agentName?: string;
    /** agent描述 */
    agentDescription?: string;
    /** 来源 */
    source?: string;
    /** 空间id */
    spaceId?: string;
  }

  interface AgentInfoVO {
    /** agentId */
    id?: number;
    /** AI推荐 */
    aiRecommend?: boolean;
    /** 下游agentId */
    agentId?: string;
    /** agent名称 */
    agentName?: string;
    /** agent类型 ● PUBLIC：公共 ● PRIVATE：私有 */
    agentType?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 头像 */
    avatar?: string;
    /** 构建类型 */
    buildType?: string;
    /** 构建类型信息 */
    buildTypeInfo?: string;
    /** 来源 */
    source?: string;
    /** agent属性 */
    agentAttribute?: string;
    /** 插件状态 */
    pluginStatus?: string;
    /** 空间id */
    spaceId?: string;
    /** 调试版本 */
    debugVersion?: string;
    /** 发布版本 */
    publishVersion?: string;
    /** 最后操作人 */
    lastModifyUser?: string;
    /** 创建人 */
    creator?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** 最后操作人花名 */
    lastModifyUserView?: string;
    /** 插件权限信息 */
    relationshipList?: Array<AgentAuthorityDTO>;
    /** agent关联关系 */
    agentRelationshipList?: Array<string>;
    /** 知识库关联关系 */
    knowledgeBaseRelationshipList?: Array<string>;
    /** 技能关联关系 */
    skillRelationshipList?: Array<string>;
  }

  interface AgentModifyRequest {
    /** portal-agentId */
    agentId?: string;
    /** 空间id */
    spaceId?: string;
    /** agent名称 */
    agentName?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 头像 */
    avatar?: string;
    /** agent关联关系 */
    agentRelationshipList?: Array<string>;
    /** 知识库关联关系 */
    knowledgeBaseRelationshipList?: Array<string>;
    /** 技能关联关系 */
    skillRelationshipList?: Array<string>;
    /** 扩展信息 */
    extendContext?: Record<string, any>;
    /** agent配置 */
    agentConfig?: Record<string, any>;
  }

  type AgentPlatformEnum =
    | 'MODELOPS'
    | 'ZDFMNG'
    | 'OPSGPT'
    | 'AITOR'
    | 'PORTAL'
    | 'OPSCLOUD'
    | 'OTHER';

  interface AgentRelationVO {
    /** agentId */
    agentId?: string;
    /** 来源和知识库id列表的map */
    sourceToKnowledgeBaseIdListMap?: Record<string, any>;
    /** 来源和工具id列表的map */
    sourceToToolIdListMap?: Record<string, any>;
    /** 来源和子agentId列表的map */
    sourceToChildAgentIdListMap?: Record<string, any>;
  }

  type AgentSubmitTypeEnum = 'NORMAL' | 'AGAIN' | 'INTERRUPT_RECOVERY';

  type AgentTypeEnum = 'LLM' | 'PUBLIC' | 'PRIVATE';

  interface AgentUserRelationshipVO {
    /** agentID */
    agentId?: string;
    /** 域账号 */
    userId?: string;
    /** 域账号 */
    loginName?: string;
    /** 用户头像 */
    employeeAvatar?: string;
    /** 员工花名 */
    nickNameCn?: string;
    /** 授权角色@see com.alipay.nexa.service.authority.enums.AuthorityRoleEnum */
    role?: AuthorityRoleEnum;
    /** 是否为当前用户权限关系 */
    isCurrentUserRelationship?: boolean;
  }

  type AgentVersionEnum = 'online' | 'downline' | 'temporarily';

  interface AitorAgentDebugResponse {
    /** 类型 */
    type?: string;
    /** 内容 */
    content?: Record<string, any>;
  }

  interface AtUser {
    /** 加密的发送者ID */
    dingtalkId?: string;
  }

  type Authority = Record<string, any>;

  type AuthorityRoleEnum =
    | 'SPACE_CREATOR'
    | 'SPACE_ADMIN'
    | 'SPACE_MEMBER'
    | 'SPACE_SUPER_MANAGER'
    | 'AGENT_CREATOR'
    | 'AGENT_ADMIN'
    | 'AGENT_MEMBER'
    | 'AGENT_SUPER_MANAGER'
    | 'WEB_MODEL_CREATOR'
    | 'WEB_MODEL_ADMIN'
    | 'WEB_MODEL_MEMBER'
    | 'WEB_MODEL_SUPER_MANAGER';

  interface AuthoritySpaceVO {
    /** 被授权的用户域账号 */
    userId?: string;
    /** 空间 id */
    spaceId?: string;
    /** 被授权的用户域账号列表 */
    userIdList?: Array<string>;
    /** 被授权的部门号列表 */
    deptNoList?: Array<string>;
    /** 授权角色@see com.alipay.nexa.service.authority.enums.AuthorityRoleEnum */
    role?: AuthorityRoleEnum;
  }

  type AuthorityStrategyMapping = 'INSTANCE';

  type AuthorityTargetTypeEnum = 'USER' | 'DEPT';

  type AuthorityTypeEnum = 'SPACE' | 'AGENT' | 'WEB_MODEL';

  type AuthorizeEnum = 'PERSON' | 'TOKEN';

  interface AuthorizeRequest {
    /** Web 模型 ID */
    webModelId?: string;
    /** 生效范围 ● SPECIFIC：特定 ● ALL：所有 */
    scope?: WebModelScopeEnum;
    /** 用户域账号列表 */
    userIdList?: Array<string>;
    /** 被授权的部门号列表 */
    deptNoList?: Array<string>;
  }

  interface BaseInfo {
    /** 域名 */
    domainName?: string;
    /** 页面路径 */
    domainPath?: string;
    /** 页面名称 */
    pageName?: string;
    /** 操作类型 */
    opType?: string;
  }

  interface BaseResult {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Record<string, any>;
  }

  interface BaseResult_DingGroupMessageSendResult_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: DingGroupMessageSendResult;
  }

  type BaseVO = Record<string, any>;

  interface BatchDeleteLinkRequest {
    /** 页面模型id */
    webModelId?: string;
    /** 生效链接信息列表 */
    linkIdList?: Array<string>;
  }

  interface BatchInsertLinkRequest {
    /** 页面模型id */
    webModelId?: string;
    /** 生效链接信息列表 */
    linkModel?: Array<LinkModelDTO>;
  }

  type BuildDetailEnum = 'SRE_TEMPLATE' | 'SHAKE_TEMPLATE' | 'LLM';

  type BuildTypeEnum = 'TEMPLATE' | 'FLOW' | 'BASE' | 'LLM';

  type ChangeCheckStatusEnum = 'EXE' | 'PASS' | 'BLOCK' | 'WARNING' | 'FAIL';

  type ChangeExeStatusEnum =
    | 'CLOSE'
    | 'EXE'
    | 'SUCC'
    | 'FAIL'
    | 'TIMEOUT'
    | 'SKIP';

  type ChangeFeedbackStatusEnum = 'IGNORE' | 'ACCEPT';

  interface ChangeOrderRequest {
    /** 用户域账号 */
    userId?: string;
    /** 变更id */
    changeId?: string;
    /** 规则id */
    ruleExeId?: string;
    /** 反馈状态 */
    status?: string;
  }

  interface ChangeRuleRequest {
    /** 变更id */
    changeId?: string;
    /** 规则id */
    ruleExeId?: string;
  }

  type ChangeVerdictEnum = 'NONE' | 'PASS' | 'INCONC' | 'FAIL';

  interface ChatAnswer {
    /** 是否流式展示 */
    streamingDisplay?: boolean;
    /** 消息类型 */
    type?: string;
    /** 消息id */
    msgId?: string;
    /** 内容详情 */
    content?: Record<string, any>;
  }

  interface ChatContent {
    /** card code */
    code?: string;
    /** 非text类型数据 */
    data?: Record<string, any>;
    /** text类型数据 */
    text?: string;
  }

  interface ChatRequest {
    /** 会话ID */
    sessionId: string;
    /** agent ID */
    agentId: string;
    /** 用户域账号 */
    userId: string;
    /** 用户工号 */
    empId?: string;
    /** 流式输出协议 不填默认：false，流式输出必须传入 true */
    stream?: boolean;
    /** 类型 text/card */
    type: string;
    /** 内容 */
    content: ChatContent;
    /** 提交模式 */
    submitType: AgentSubmitTypeEnum;
    /** 重试的时候需要带上提问id */
    msgId?: string;
    /** 扩展字段 */
    extendContext?: Record<string, any>;
    /** 接口调用来源 */
    callSource?: string;
    /** 上一次submit chat返回的id */
    chatUniqueId?: string;
  }

  type ChatRequestTypeEnum = 'NORMAL_CHAT' | 'INTERRUPT_RECOVERY';

  type ChatResultTypeEnum = 'cover' | 'append';

  type ChatRoleEnum = 'system' | 'bot' | 'user';

  type ChatTypeEnum = 'text' | 'card' | 'json';

  interface CodeDebugRequest {
    /** portal-agentId */
    agentId?: string;
    /** 空间id */
    spaceId?: string;
    /** 代码实现 */
    code?: string;
    /** 输入参数 */
    inputParam?: Record<string, any>;
    /** 输出定义 */
    outputDefine?: Array<OutputParam>;
  }

  interface ComAlipayNexaServiceDtoDingDingTalkBotMsg$AtUser {
    /** Gets get dingtalk id. */
    dingtalkId?: string;
  }

  interface Component {
    /** 组件的唯一标识ID。 */
    componentId?: string;
    /** 标识该组件是否为触发点组件，用于特殊交互逻辑处理。 */
    triggerPoint?: boolean;
    /** 组件的关键键值，用于区分和识别不同组件，需在当前页面模型中唯一。 */
    componentKey?: string;
    /** 组件的展示名称，通常为中文，便于用户理解和配置。 */
    name?: string;
    /** 组件类型 */
    componentType?: string;
    /** 与该组件关联的事件列表，描述了组件在不同交互下的行为。 */
    events?: Array<ComponentEvent>;
  }

  interface ComponentEvent {
    /** 事件id */
    eventId?: string;
    /** 父组件变量key */
    parentComponentKey?: string;
    /** 父组件id */
    parentComponentId?: string;
    /** 触发方式 */
    triggerMethod?: string;
    /** 触发事件 */
    triggerEvent?: string;
    /** 触发服务 */
    service?: string;
    /** 服务实例 */
    serviceInstance?: Record<string, any>;
    /** 参数 */
    payload?: Record<string, any>;
  }

  type ComponentTypeEnum = 'ORIGIN' | 'INJECTION';

  interface ConfigInfoVO {
    /** 每页大小 */
    pageSize: number;
    /** 当前页 */
    currentPage: number;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** 配置名称 */
    configName?: string;
    /** 配置项 */
    configKey?: string;
    /** 配置值 */
    configValue?: string;
  }

  type ConfigSwitchEnum = 'HOSTED' | 'UN_HOSTED';

  interface ContentArea {
    /** 内容 */
    content?: Record<string, any>;
  }

  type ContentSecurityCheckServiceEnum = 'ALIYUN_GREEN' | 'ANT_SECURITY';

  interface CreateSpaceWithAdminRequest {
    /** 空间名称 */
    name?: string;
    /** 空间描述 */
    description?: string;
    /** 空间创建者 */
    creator?: string;
    /** 空间管理员 */
    admin?: Array<string>;
    /** 空间成员 */
    member?: Array<string>;
  }

  interface CreateToolRelationRequest {
    /** agentId */
    agentId?: string;
    /** 关联的技能id（下游id） */
    bindingKey?: string;
    /** 名称 */
    name?: string;
    /** 描述 */
    description?: string;
    /** 类型 */
    taskType?: TaskTypeEnum;
  }

  type CustomCardCodeEnum = 'shake_card' | 'SHAKE_CARD';

  type DataWithMediaType = Record<string, any>;

  type DefaultCallback = Record<string, any>;

  type DefenseStageEnum = 'PRE' | 'POST';

  interface DeleteInjectionComponentRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 组件id */
    componentId?: string;
  }

  interface DeleteInteractionRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 事件id */
    eventId?: string;
    /** 模型类型 */
    modelType?: string;
  }

  interface DeleteOriginComponentRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 原始组件id */
    componentId?: string;
  }

  type DeleteStatusEnum = 'NOT_DELETED' | 'DELETED';

  interface DeleteUniversalComponentRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 原始组件id */
    componentId?: string;
  }

  interface DeleteWebModelRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 页面模型id */
    webModelId?: string;
  }

  interface Dept {
    /** 部门简称（最后一级部门名称） */
    deptShortName?: string;
    /** 部门编号 */
    deptNo?: string;
    /** 部门下的人 */
    deptPersonNum?: number;
    /** 部门全称 */
    deptName?: string;
    /** 部门路径 */
    deptPath?: string;
  }

  interface DetectData {
    /** 基础信息 */
    baseInfo?: BaseInfo;
    /** 内容区域 */
    contentArea?: ContentArea;
  }

  interface DingGroupMessageSendRequest {
    /** 消息模板参数 */
    msgParam?: string;
    /** 消息模板key */
    msgKey?: string;
    /** 会话ID */
    openConversationId?: string;
  }

  interface DingGroupMessageSendResult {
    /** processQueryKey */
    processQueryKey?: string;
  }

  interface DingTalkBotMsg {
    /** 目前只支持text */
    msgtype?: string;
    /** 消息文本 */
    text?: DingTalkBotMsgMsgContext;
    /** 消息文本 */
    content?: DingTalkBotMsgMsgContent;
    /** 加密的消息ID */
    msgId?: string;
    /** 消息的时间戳，单位ms */
    createAt?: number;
    /** 1-单聊、2-群聊 */
    conversationType?: string;
    /** 加密的会话ID */
    conversationId?: string;
    /** 会话标题（群聊时才有） */
    conversationTitle?: string;
    /** 加密的发送者ID */
    senderId?: string;
    /** 发送者昵称 非花名 非花名 非花名 */
    senderNick?: string;
    /** 发送者工号 */
    senderStaffId?: string;
    /** 加密的机器人ID */
    chatbotUserId?: string;
    /** 被@人的信息

<p>dingtalkId: 加密的发送者ID

<p>staffId: 发送者在企业内的userid（企业内部群有） */
    atUsers?: Array<DingTalkBotMsgAtUser>;
    /** 会话钩子 */
    sessionWebhook?: string;
    /** 会话钩子有效期 */
    sessionWebhookExpiredTime?: number;
    /** 机器人代码 */
    robotCode?: string;
  }

  interface DingTalkBotMsgAtUser {
    /** Gets get dingtalk id. */
    dingtalkId?: string;
  }

  interface DingTalkBotMsgMsgContent {
    /** Getter method for property <tt>downloadCode</tt>. */
    downloadCode?: string;
    /** Getter method for property <tt>recognition</tt>. */
    recognition?: string;
    /** Getter method for property <tt>duration</tt>. */
    duration?: number;
  }

  interface DingTalkBotMsgMsgContext {
    debug?: boolean;
    /** Gets get content. */
    content?: string;
  }

  interface DirYuQueKnowledgeVO {
    yuQues?: Array<YuQue>;
    qas?: Array<Record<string, any>>;
  }

  interface DocumentResponse {
    /** 文档的唯一标识 */
    docSlug?: string;
    /** 文档的标题 */
    title?: string;
    /** 文档的类型，可以是"DIR"或"DOC" */
    type?: string;
    /** 父目录的唯一标识，只有"type"为"DIR"时有值 */
    parentDocSlug?: string;
    /** 子文档的唯一标识，只有"type"为"DIR"时有值 */
    childDocSlug?: string;
    /** 前一个文档的唯一标识，用于分页时的上一页操作 */
    prevDocSlug?: string;
    /** 兄弟文档的唯一标识，用于分页时的下一页操作 */
    siblingDocSlug?: string;
    /** 是否选中该文档 */
    selected?: boolean;
    /** 文件id，只有"type"="DOC"才有 */
    fileId?: string;
    /** 百分比，只有"type"="DOC"才有 */
    progress?: string;
    /** 文件状态 */
    fileStatus?: string;
  }

  interface EffectiveLinkVO {
    /** 主键id */
    id?: number;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** 链接ID */
    linkId?: string;
    /** 页面模型id */
    webModelId?: string;
    /** 生效链接 */
    url?: string;
    /** 是否开启数据传输 */
    enable?: boolean;
    /** 备注信息 */
    remark?: string;
  }

  type ErrorCallback = Record<string, any>;

  type ErrorEnum =
    | '100'
    | 'PARAM_INVALID'
    | '101'
    | 'DATA_NOT_FOUND'
    | '102'
    | 'INSUFFICIENT_PERMISSIONS'
    | '103'
    | 'REQUEST_DOWNSTREAM_ERROR'
    | '104'
    | 'UNKNOWN_ERROR'
    | '105'
    | 'DATA_REPEAT'
    | '106'
    | 'TIME_OUT'
    | '107'
    | 'NO_USER'
    | '108'
    | 'QUERY_LIMITED'
    | '109'
    | 'URL_DISABLE'
    | '110'
    | 'INTERNAL_ERROR'
    | '111'
    | 'REPORT_ERROR'
    | '112'
    | 'CHECK_PERMISSION_ERROR'
    | '113'
    | 'RPC_NOT_EXIST'
    | '114'
    | 'RPC_FAIL'
    | '115'
    | 'AGENT_PAGE_FAIL'
    | '116'
    | 'AGENT_INFO_FAIL'
    | '117'
    | 'AGENT_SUBMIT_CHAT_FAIL'
    | '118'
    | 'AGENT_CHAT_RESULT_FAIL'
    | '119'
    | 'AGENT_END_SESSION_FAIL'
    | '120'
    | 'AGENT_DELETE_FAIL'
    | '121'
    | 'SUBMIT_OPSCLOUD_FAIL'
    | '122'
    | 'RETRIEVE_OPSCLOUD_FAIL'
    | '123'
    | 'NOTIFY_OPSCLOUD_FAIL'
    | '124'
    | 'OPSGPT_ERROR'
    | '125'
    | 'AGENT_CHAT_ASYNC_RESULT_NOT_COMPLETED'
    | '126'
    | 'UPDATE_AGENT_FAILED'
    | '127'
    | 'RELEASE_AGENT_FAILED'
    | '128'
    | 'AGENT_VERSION_FAIL'
    | '129'
    | 'ROLLBACK_VERSION_FAIL'
    | '130'
    | 'PUBLISH_VERSION_FAIL'
    | '131'
    | 'AGENT_STREAM_CHAT_RESULT_FAIL'
    | '500'
    | 'DB_ERROR'
    | '201'
    | 'FS_DOWNLOAD_FILE_ERROR';

  type Flux = Record<string, any>;

  type Flux_StreamAgentChatAnswerDTO_ = Record<string, any>;

  interface GEdge {
    /** 起点节点ID */
    startId?: string;
    /** 终点节点ID */
    endId?: string;
    /** 属性 */
    attributes?: Record<string, any>;
  }

  interface GGraph {
    /** 节点列表 */
    nodes?: Array<GNode>;
    /** 边列表 */
    edges?: Array<GEdge>;
  }

  interface GNode {
    /** 节点ID */
    id?: string;
    /** 节点类型 */
    type?: string;
    /** 节点属性 */
    attributes?: Record<string, any>;
  }

  interface GenerateCodeRequest {
    /** LLM 模型 */
    llmModel?: string;
    /** 温度 */
    temperature?: number;
    /** 用户聊天内容 */
    chatContent?: string;
  }

  interface GraphImportByYuqueRequest {
    /** 团队ID */
    teamId?: string;
    /** 导入哪个意图节点ID下 */
    intentNodeId?: string;
    /** 知识库ID */
    knowledgeBaseId?: string;
    /** 语雀Token */
    yuqueToken?: string;
    /** 语雀groupLogin */
    groupLogin?: string;
    /** 语雀bookSlug */
    bookSlug?: string;
    /** 语雀docSlug */
    docSlug?: string;
  }

  interface GraphImportTaskDetail {
    /** 任务id */
    taskId?: string;
    /** 任务状态 */
    status?: string;
    /** 导入哪个意图节点ID下 */
    intentNodeId?: string;
    /** 语雀groupLogin */
    groupLogin?: string;
    /** 语雀bookSlug */
    bookSlug?: string;
    /** 语雀docSlug */
    docSlug?: string;
    /** 文档标题 */
    docTitle?: string;
  }

  interface GraphUpdateRequest {
    /** 团队ID */
    teamId?: string;
    /** 当前层级的根节点ID 外层图谱: 团队根节点(开始节点) 内层图谱: 计划节点 */
    rootNodeId?: string;
    /** 更新前的图 */
    oldGraph?: GGraph;
    /** 更新后的图 */
    newGraph?: GGraph;
  }

  type GroupAuthorizeTypeEnum = 'PERSONAL' | 'TOKEN';

  type Handler = Record<string, any>;

  interface HttpServletRequest {
    /** String identifier for Basic authentication. Value "BASIC" */
    BASIC_AUTH?: string;
    /** String identifier for Form authentication. Value "FORM" */
    FORM_AUTH?: string;
    /** String identifier for Client Certificate authentication. Value "CLIENT_CERT" */
    CLIENT_CERT_AUTH?: string;
    /** String identifier for Digest authentication. Value "DIGEST" */
    DIGEST_AUTH?: string;
  }

  interface HttpServletResponse {
    /** Status code (100) indicating the client can continue. */
    SC_CONTINUE?: number;
    /** Status code (101) indicating the server is switching protocols according to Upgrade header. */
    SC_SWITCHING_PROTOCOLS?: number;
    /** Status code (200) indicating the request succeeded normally. */
    SC_OK?: number;
    /** Status code (201) indicating the request succeeded and created a new resource on the server. */
    SC_CREATED?: number;
    /** Status code (202) indicating that a request was accepted for processing, but was not completed. */
    SC_ACCEPTED?: number;
    /** Status code (203) indicating that the meta information presented by the client did not originate from the server. */
    SC_NON_AUTHORITATIVE_INFORMATION?: number;
    /** Status code (204) indicating that the request succeeded but that there was no new information to return. */
    SC_NO_CONTENT?: number;
    /** Status code (205) indicating that the agent <em>SHOULD</em> reset the document view which caused the request to
be sent. */
    SC_RESET_CONTENT?: number;
    /** Status code (206) indicating that the server has fulfilled the partial GET request for the resource. */
    SC_PARTIAL_CONTENT?: number;
    /** Status code (300) indicating that the requested resource corresponds to any one of a set of representations, each
with its own specific location. */
    SC_MULTIPLE_CHOICES?: number;
    /** Status code (301) indicating that the resource has permanently moved to a new location, and that future
references should use a new URI with their requests. */
    SC_MOVED_PERMANENTLY?: number;
    /** Status code (302) indicating that the resource has temporarily moved to another location, but that future
references should still use the original URI to access the resource. This definition is being retained for
backwards compatibility. SC_FOUND is now the preferred definition. */
    SC_MOVED_TEMPORARILY?: number;
    /** Status code (302) indicating that the resource reside temporarily under a different URI. Since the redirection
might be altered on occasion, the client should continue to use the Request-URI for future requests.(HTTP/1.1) To
represent the status code (302), it is recommended to use this variable. */
    SC_FOUND?: number;
    /** Status code (303) indicating that the response to the request can be found under a different URI. */
    SC_SEE_OTHER?: number;
    /** Status code (304) indicating that a conditional GET operation found that the resource was available and not
modified. */
    SC_NOT_MODIFIED?: number;
    /** Status code (305) indicating that the requested resource <em>MUST</em> be accessed through the proxy given by the
<code><em>Location</em></code> field. */
    SC_USE_PROXY?: number;
    /** Status code (307) indicating that the requested resource resides temporarily under a different URI. The temporary
URI <em>SHOULD</em> be given by the <code><em>Location</em></code> field in the response. */
    SC_TEMPORARY_REDIRECT?: number;
    /** Status code (400) indicating the request sent by the client was syntactically incorrect. */
    SC_BAD_REQUEST?: number;
    /** Status code (401) indicating that the request requires HTTP authentication. */
    SC_UNAUTHORIZED?: number;
    /** Status code (402) reserved for future use. */
    SC_PAYMENT_REQUIRED?: number;
    /** Status code (403) indicating the server understood the request but refused to fulfill it. */
    SC_FORBIDDEN?: number;
    /** Status code (404) indicating that the requested resource is not available. */
    SC_NOT_FOUND?: number;
    /** Status code (405) indicating that the method specified in the <code><em>Request-Line</em></code> is not allowed
for the resource identified by the <code><em>Request-URI</em></code>. */
    SC_METHOD_NOT_ALLOWED?: number;
    /** Status code (406) indicating that the resource identified by the request is only capable of generating response
entities which have content characteristics not acceptable according to the accept headers sent in the request. */
    SC_NOT_ACCEPTABLE?: number;
    /** Status code (407) indicating that the client <em>MUST</em> first authenticate itself with the proxy. */
    SC_PROXY_AUTHENTICATION_REQUIRED?: number;
    /** Status code (408) indicating that the client did not produce a request within the time that the server was
prepared to wait. */
    SC_REQUEST_TIMEOUT?: number;
    /** Status code (409) indicating that the request could not be completed due to a conflict with the current state of
the resource. */
    SC_CONFLICT?: number;
    /** Status code (410) indicating that the resource is no longer available at the server and no forwarding address is
known. This condition <em>SHOULD</em> be considered permanent. */
    SC_GONE?: number;
    /** Status code (411) indicating that the request cannot be handled without a defined
<code><em>Content-Length</em></code>. */
    SC_LENGTH_REQUIRED?: number;
    /** Status code (412) indicating that the precondition given in one or more of the request-header fields evaluated to
false when it was tested on the server. */
    SC_PRECONDITION_FAILED?: number;
    /** Status code (413) indicating that the server is refusing to process the request because the request entity is
larger than the server is willing or able to process. */
    SC_REQUEST_ENTITY_TOO_LARGE?: number;
    /** Status code (414) indicating that the server is refusing to service the request because the
<code><em>Request-URI</em></code> is longer than the server is willing to interpret. */
    SC_REQUEST_URI_TOO_LONG?: number;
    /** Status code (415) indicating that the server is refusing to service the request because the entity of the request
is in a format not supported by the requested resource for the requested method. */
    SC_UNSUPPORTED_MEDIA_TYPE?: number;
    /** Status code (416) indicating that the server cannot serve the requested byte range. */
    SC_REQUESTED_RANGE_NOT_SATISFIABLE?: number;
    /** Status code (417) indicating that the server could not meet the expectation given in the Expect request header. */
    SC_EXPECTATION_FAILED?: number;
    /** Status code (500) indicating an error inside the HTTP server which prevented it from fulfilling the request. */
    SC_INTERNAL_SERVER_ERROR?: number;
    /** Status code (501) indicating the HTTP server does not support the functionality needed to fulfill the request. */
    SC_NOT_IMPLEMENTED?: number;
    /** Status code (502) indicating that the HTTP server received an invalid response from a server it consulted when
acting as a proxy or gateway. */
    SC_BAD_GATEWAY?: number;
    /** Status code (503) indicating that the HTTP server is temporarily overloaded, and unable to handle the request. */
    SC_SERVICE_UNAVAILABLE?: number;
    /** Status code (504) indicating that the server did not receive a timely response from the upstream server while
acting as a gateway or proxy. */
    SC_GATEWAY_TIMEOUT?: number;
    /** Status code (505) indicating that the server does not support or refuses to support the HTTP protocol version
that was used in the request message. */
    SC_HTTP_VERSION_NOT_SUPPORTED?: number;
  }

  interface ImportQAFileRequest {
    /** 知识库id */
    knowledgeBaseId?: string;
    /** qa id */
    qaId?: string;
    /** 文件列表，示例如下 */
    fileUploadList?: Array<QAFileUpload>;
  }

  interface ImportToolsVO {
    /** 导入工具列表 */
    toolList?: Array<ToolVO>;
    /** 空间id */
    spaceId?: string;
    /** 来源（AITOR，OPSGPT） */
    source?: string;
  }

  interface ImportYuQueKnowledgeRequest {
    /** 知识库ID */
    knowledgeBaseId?: string;
    /** 选中的要更新的语雀团队列表 */
    groups?: Array<YuQueGroupRequest>;
    /** 授权类型 PERSONAL：个人 TOKEN：token */
    type?: string;
  }

  interface InjectionComponent {
    /** 组件的唯一标识ID。 */
    componentId?: string;
    /** 标识该组件是否为触发点组件，用于特殊交互逻辑处理。 */
    triggerPoint?: boolean;
    /** 组件的关键键值，用于区分和识别不同组件，需在当前页面模型中唯一。 */
    componentKey?: string;
    /** 组件的展示名称，通常为中文，便于用户理解和配置。 */
    name?: string;
    /** 组件类型 */
    componentType?: string;
    /** 与该组件关联的事件列表，描述了组件在不同交互下的行为。 */
    events?: Array<ComponentEvent>;
    /** 父组件变量key */
    parentComponentKey?: string;
    /** 组件样式 */
    props?: string;
    /** 偏移量 */
    position?: Record<string, any>;
  }

  interface InsertListRequest {
    /** 用户域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
    /** 头像 */
    avatar?: string;
    /** 工具ID */
    toolId?: string;
    /** 工具名称 */
    toolName?: string;
    /** 工具描述 */
    toolDesc?: string;
    /** 代理ID */
    agentId?: string;
    /** 工具栏是否显示 */
    toolbarDisplay?: boolean;
    /** 工具箱是否显示 */
    toolboxDisplay?: boolean;
    /** 是否私有 */
    toolType?: string;
    /** 来源 */
    source?: string;
    colorAvatar?: string;
    toolbarAvatar?: string;
    owners?: string;
    status?: string;
    registration?: string;
  }

  interface InterfaceTypeDTO {
    /** 接口类型 */
    interfaceType?: string;
    /** 输入参数 */
    inputParams?: string;
    /** 输出参数 */
    outputParams?: string;
  }

  type InterfaceTypeEnum = 'RISK_DETECTION' | 'API_CALL' | 'TOOL_CALL';

  interface Knowledge {
    aContent?: string;
    fileId?: string;
    gmtCreate?: string;
    gmtModified?: string;
    id?: number;
    jsonExt?: string;
    knowledgeId?: string;
    knowledgebaseId?: string;
    qContent?: string;
    source?: string;
    status?: string;
    keys?: Array<string>;
  }

  interface KnowledgeBaseRequest {
    /** 每页大小 */
    pageSize: number;
    /** 当前页 */
    currentPage: number;
    /** 知识库Id */
    id?: string;
    /** 知识库名称 */
    name?: string;
    /** 知识库描述 */
    description?: string;
    /** 类型（图谱，非图谱...） */
    type?: string;
    /** 下游知识库id */
    knowledgeBaseId?: string;
    /** 空间 ID */
    spaceId?: string;
    /** 源 （Aitor，OPSGPT） */
    source?: string;
  }

  type KnowledgeBaseTypeEnum = 'ATLAS' | 'RAG';

  interface KnowledgeEntity {
    knowledges?: Array<Knowledge>;
  }

  type LLMModelEnum =
    | 'QWEN_CHAT_14B'
    | 'BAILING_CHAT_10B'
    | 'CHATGPT_35_TURBO'
    | 'Bailing65B'
    | 'Qwen15_110B'
    | 'Qwen2_72B';

  interface LinkModelDTO {
    /** 生效链接 */
    url?: string;
    /** 是否开启数据传输 */
    enable?: boolean;
    /** 评论信息 */
    remark?: string;
  }

  interface LlmResponse {
    /** 模型内容 */
    content?: string;
    /** 是否可用 */
    enable?: boolean;
    /** 模型内容展示 */
    viewContent?: string;
  }

  type MatchModeEnum =
    | 'StringMatcher'
    | 'STRING_MATCHER'
    | 'VectorSmilarityMatcher'
    | 'VECTOR_SMILARITY_MATCHER'
    | 'SequenceMatcher'
    | 'SEQUENCE_MATCHER';

  type MessageTypeEnum = 'TEXT' | 'CARD';

  interface MessageVO {
    /** 消息类型 */
    type?: string;
    /** 角色 */
    role?: string;
    /** 消息内容 */
    content?: Record<string, any>;
  }

  type ModelMap = Record<string, any>;

  type ModelTypeEnum = 'UNIVERSAL' | 'SPECIFIC';

  interface ModifyConfigRequest {
    /** 域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
    /** 工具栏配置 ● HOSTED：开启 ● UNHOSTED：关闭 */
    toolbar?: string;
  }

  interface MsgContent {
    downloadCode?: string;
    recognition?: string;
    duration?: number;
  }

  interface MsgContext {
    debug?: boolean;
    content?: string;
  }

  interface MsgFeedbackRequest {
    /** 消息id */
    messageId?: string;
    /** 反馈类型 POSITIVE：积极反馈 NEGATIVE：消极反馈 */
    feedbackType?: string;
    /** 反馈内容 */
    feedbackContent?: string;
  }

  interface MsgRecordRequest {
    /** 会话id */
    sessionId?: string;
    /** 消息id */
    messageId?: string;
  }

  type MsgTypeEnum = 'text' | 'photo' | 'markdown' | 'actionCard' | 'empty';

  type NewMsgTypeEnum = 'text' | 'photo' | 'markdown' | 'actionCard' | 'empty';

  interface NexaConfigModifyDTO {
    /** 用户ID */
    userId?: string;
    /** 员工ID */
    empId?: string;
    /** 配置名称 */
    configName?: string;
    /** 配置项 */
    configKey?: string;
    /** 配置值 */
    configValue?: Record<string, any>;
  }

  interface NexaDingGroupAgentRelationDO {
    id?: number;
    gmtCreate?: string;
    gmtModified?: string;
    agentId?: string;
    dingGroupId?: string;
    operator?: string;
  }

  interface NexaDingProxyConfigDO {
    id?: number;
    gmtCreate?: string;
    gmtModified?: string;
    agentId?: string;
    dingGroupId?: string;
    proxyUrl?: string;
    enable?: boolean;
  }

  type NexaDingRobotEnum = 'NEXA' | 'SHAKE';

  interface NexaKnowledgeBaseVO {
    /** 知识库Id */
    id?: number;
    /** 知识库名称 */
    name?: string;
    /** 知识库描述 */
    description?: string;
    /** 类型（图谱，非图谱...）@see com.alipay.nexa.service.dto.knowledge.enums.KnowledgeBaseTypeEnum */
    type?: string;
    /** 下游知识库id */
    knowledgeBaseId?: string;
    /** 空间 ID */
    spaceId?: string;
    /** 来源（Aitor，OPSGPT） */
    source?: string;
    /** 创建人 */
    creator?: string;
    /** 最后修改时间 */
    gmtModified?: string;
    /** 最后修改人 */
    lastModifyUser?: string;
    /** 最后修改人花名 */
    lastModifyUserView?: string;
    /** 知识库属性 PUBLIC/PRIVATE */
    knowledgeType?: string;
    /** 是否同步标识 */
    autoSyncFlag?: boolean;
  }

  interface NexaOCRRVO {
    explanation?: string;
  }

  interface NexaOCRRequest {
    /** 图片url */
    url?: string;
    /** 原图片base64 */
    image?: string;
    /** 原图片base64,保留参数，与image含义相同。建议使用image */
    imageBytes?: string;
    /** 额外参数 */
    ext?: Record<string, any>;
  }

  interface NexaResult {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: Record<string, any>;
  }

  type NexaResultCodeEnum =
    | '000'
    | 'SUCCESS'
    | '001'
    | 'SUCCESS_APPEND'
    | '101'
    | 'ACCESS_LIMIT_EXCEEDED'
    | '102'
    | 'DOWNSTREAM_ERROR'
    | '103'
    | 'ASYNC_RESULT_NOT_COMPLETED'
    | '104'
    | 'OPENAPI_ERROR'
    | '105'
    | 'STREAM_COVER_HALF_SUCCESS'
    | '106'
    | 'STREAM_APPEND_HALF_SUCCESS'
    | '999'
    | 'UNKNOWN_ERROR';

  interface NexaResult_Boolean_ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: boolean;
  }

  interface NexaResult_List_MessageVO__ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: Array<MessageVO>;
  }

  interface NexaResult_NexaOCRRVO_ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: NexaOCRRVO;
  }

  interface NexaResult_SpaceResourceResponse_ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: SpaceResourceResponse;
  }

  interface NexaResult_String_ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: string;
  }

  interface NexaSessionMessageVO {
    /** ID */
    id?: string;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** 消息ID */
    messageId?: string;
    /** conversationID */
    conversationId?: string;
    /** 会话ID */
    sessionId?: string;
    /** agentId */
    agentId?: string;
    /** agent名称 */
    agentName?: string;
    /** agent属性 */
    agentAttribute?: string;
    /** 头像 */
    avatar?: string;
    /** 消息类型 */
    messageType?: string;
    /** 消息内容 */
    messageContent?: string;
    /** 角色 */
    role?: string;
    /** 发送时间 */
    sendTime?: string;
    /** 反馈类型 */
    feedbackType?: string;
    /** 反馈内容 */
    feedbackContent?: string;
  }

  interface NexaSessionVO {
    /** 会话ID */
    id?: string;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** session信息ID */
    sessionId?: string;
    /** 用户ID */
    userId?: string;
    /** 消息总结 */
    summary?: string;
  }

  interface NexaToolProtocol {
    /** 工具名称 */
    toolName?: string;
    /** 工具描述 */
    description?: string;
    /** 工具入参描述 */
    parameters?: Array<Parameter>;
    /** 工具出参描述 */
    response?: Array<Parameter>;
  }

  type NexaUserConfigModifyEnum =
    | 'SIDEBAR'
    | 'PLUGiN_AUTH'
    | 'TOOLBAR'
    | 'COMMON'
    | 'AGENT'
    | 'ADVANCED';

  interface NexaUserConfigRequest {
    /** 用户 ID */
    userId?: string;
    /** 员工 ID */
    empId?: string;
    /** 类型 */
    type?: string;
    /** 配置 */
    config?: Record<string, any>;
  }

  interface NexaUserConfigVO {
    /** 通用配置 */
    common?: Record<string, any>;
    /** 侧边栏配置 */
    sidebar?: Record<string, any>;
    /** 工具栏配置 */
    toolbar?: Record<string, any>;
    /** 高级配置 */
    advanced?: Record<string, any>;
    /** 代理配置 */
    agent?: Record<string, any>;
    /** 插件身份验证配置 */
    pluginAuth?: Record<string, any>;
  }

  type OneApiResult_object_ = Record<string, any>;

  type OneApiResult_string_ = Record<string, any>;

  type OperationTargetTypeEnum =
    | 'SPACE'
    | 'AGENT'
    | 'KNOWLEDGE_BASE'
    | 'TOOL'
    | 'AUTHORITY'
    | 'PLUGIN_TOOL'
    | 'SESSION';

  type OperationTypeEnum =
    | 'CREATE'
    | 'UPDATE'
    | 'QUERY'
    | 'DELETE'
    | 'EXECUTE'
    | 'PUBLISH'
    | 'ROLLBACK';

  type OpsCloudChangeCheckStatusEnum = 'EXE' | 'FAIL' | 'SUCC' | 'TIMEOUT';

  type OpsCloudChangeCheckVerdictEnum = 'NONE' | 'PASS' | 'INCONC' | 'FAIL';

  interface OptimizeJsonRequest {
    /** 用户文本 */
    userText?: string;
    /** 模型类型 */
    modelType?: string;
  }

  interface OrderPojo {
    id?: number;
    price?: number;
    address?: string;
  }

  type OrgSpringframeworkWebServletMvcMethodAnnotationResponseBodyEmitterDataWithMediaType =
    Record<string, any>;

  interface OriginComponent {
    /** 组件的唯一标识ID。 */
    componentId?: string;
    /** 标识该组件是否为触发点组件，用于特殊交互逻辑处理。 */
    triggerPoint?: boolean;
    /** 组件的关键键值，用于区分和识别不同组件，需在当前页面模型中唯一。 */
    componentKey?: string;
    /** 组件的展示名称，通常为中文，便于用户理解和配置。 */
    name?: string;
    /** 组件类型 */
    componentType?: string;
    /** 与该组件关联的事件列表，描述了组件在不同交互下的行为。 */
    events?: Array<ComponentEvent>;
    /** 页面元素选择器 */
    selector?: string;
  }

  interface OssResourceRelationResponse {
    /** 文件id */
    fileId?: string;
    /** 文件名称 */
    fileName?: string;
    /** 文件url */
    fileUrl?: string;
  }

  interface OutGoingMsg {
    msgtype?: string;
    /** 消息文本 */
    text?: MsgContext;
    /** 消息文本 */
    content?: MsgContent;
    /** 加密的消息ID */
    msgId?: string;
    /** 回复的消息ID */
    originalMsgId?: string;
    /** 回复的消息ProcessQueryKey */
    originalProcessQueryKey?: string;
    /** 消息的时间戳，单位ms */
    createAt?: number;
    /** 1-单聊、2-群聊 */
    conversationType?: string;
    /** 加密的会话ID */
    conversationId?: string;
    /** 会话标题（群聊时才有） */
    conversationTitle?: string;
    /** 加密的发送者ID */
    senderId?: string;
    /** 发送者昵称 非花名 非花名 非花名 */
    senderNick?: string;
    /** 发送者工号 */
    senderStaffId?: string;
    /** 加密的机器人ID */
    chatbotUserId?: string;
    /** 被@人的信息

<p>dingtalkId: 加密的发送者ID

<p>staffId: 发送者在企业内的userid（企业内部群有） */
    atUsers?: Array<AtUser>;
    /** 会话钩子 */
    sessionWebhook?: string;
    /** 会话钩子有效期 */
    sessionWebhookExpiredTime?: number;
    /** 钉钉 token */
    token?: string;
    /** 当前请求的上下文信息 */
    context?: RequestContext;
  }

  interface OutputParam {
    /** id */
    id?: number;
    /** 参数值 */
    key?: string;
    /** 参数类型 */
    type?: string;
  }

  interface PageQueryPluginRequest {
    /** 代理名称 */
    agentName?: string;
    /** 页码 */
    currentPage?: number;
    /** 页面大小 */
    pageSize?: number;
  }

  interface PageResultList {
    /** 分页数据 */
    resultList?: Array<Record<string, any>>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_AgentInfoVO_ {
    /** 分页数据 */
    resultList?: Array<AgentInfoVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_AgentUserRelationshipVO_ {
    /** 分页数据 */
    resultList?: Array<AgentUserRelationshipVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_ConfigInfoVO_ {
    /** 分页数据 */
    resultList?: Array<ConfigInfoVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_EffectiveLinkVO_ {
    /** 分页数据 */
    resultList?: Array<EffectiveLinkVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_NexaKnowledgeBaseVO_ {
    /** 分页数据 */
    resultList?: Array<NexaKnowledgeBaseVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_NexaSessionVO_ {
    /** 分页数据 */
    resultList?: Array<NexaSessionVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_PluginAgentVO_ {
    /** 分页数据 */
    resultList?: Array<PluginAgentVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_PluginToolVO_ {
    /** 分页数据 */
    resultList?: Array<PluginToolVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_QueryModelListVO_ {
    /** 分页数据 */
    resultList?: Array<QueryModelListVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageResultList_ToolVO_ {
    /** 分页数据 */
    resultList?: Array<ToolVO>;
    /** 分页信息 */
    pagination?: Pagination;
  }

  interface PageVO {
    /** 每页大小 */
    pageSize: number;
    /** 当前页 */
    currentPage: number;
  }

  interface Pagination {
    /** 当前页数 */
    currentPage?: number;
    /** 每页显示多少 */
    pageSize?: number;
    /** 记录总数 */
    totalRecords?: number;
    /** 管理员总数 */
    totalAdmins?: number;
    /** 成员总数 */
    totalMembers?: number;
  }

  interface Parameter {
    /** 参数类型 */
    type?: ParameterTypeEnum;
    /** 参数名称 */
    name?: string;
    /** 参数描述 */
    description?: string;
    /** 是否必填 */
    required?: boolean;
    /** object 类型参数结构 */
    object?: Array<Parameter>;
    /** array_object 类型参数结构,定义object中的参数类型 */
    arrayObject?: Array<Parameter>;
  }

  type ParameterTypeEnum =
    | 'integer'
    | 'number'
    | 'bool'
    | 'string'
    | 'array_integer'
    | 'array_number'
    | 'array_string'
    | 'array_bool'
    | 'array_object'
    | 'object';

  type PermissionEnum =
    | 'CREATE'
    | 'UPDATE'
    | 'QUERY'
    | 'DELETE'
    | 'EXECUTE'
    | 'PUBLISH';

  type PlateFormInvokeModeEnum = 'SYNC_HTTP' | 'SYNC_TR';

  type PlatformTypeEnum = 'PLUGIN' | 'PORTAL';

  interface PluginAgentVO {
    /** 同上 */
    id?: number;
    /** GMT 创建 */
    gmtCreate?: string;
    /** GMT修改 */
    gmtModified?: string;
    /** 代理 ID */
    agentId?: string;
    /** 代理名称 */
    agentName?: string;
    /** 化身 */
    avatar?: string;
    /** 代理 DESC */
    agentDesc?: string;
    /** 座席提示 */
    agentPrompt?: string;
    /** 代理类型 */
    agentType?: string;
    /** 构建类型 */
    agentAttribute?: string;
    /** 源 */
    source?: string;
    /** 是否前调用 */
    agentChat?: boolean;
    /** 创建者 */
    creator?: string;
    /** 管理员 */
    owners?: string;
    /** 上次修改用户 */
    lastModifyUser?: string;
    /** 状态 */
    status?: string;
    /** 删除状态 */
    deleteStatus?: number;
    /** 注册 */
    registration?: string;
    /** 接口调用 */
    interfaceCall?: boolean;
    /** 聊天配置 */
    chatConfig?: Record<string, any>;
    /** 接口配置 */
    interfaceConfig?: Record<string, any>;
    /** 是否开启AI推荐 */
    aiRecommend?: boolean;
  }

  type PluginStatusEnum = 'ON' | 'OFF';

  interface PluginSystemConfigVO {
    /** 配置名称 */
    configName?: string;
    /** 配置项 */
    configKey?: string;
    /** 配置值 */
    configValue?: Record<string, any>;
  }

  interface PluginSystemToolConfigVO {
    /** 是否开启AI推荐 */
    aiRecommend?: boolean;
    /** 配置名称 */
    configName?: string;
    /** 配置项 */
    configKey?: string;
    /** 配置值 */
    configValue?: Record<string, any>;
    /** 划词推荐配置 */
    recommendationConfig?: Record<string, any>;
    /** 划词展示配置 */
    displayConfig?: Record<string, any>;
  }

  interface PluginToolPageRequest {
    /** 每页大小 */
    pageSize: number;
    /** 当前页 */
    currentPage: number;
    toolName?: string;
  }

  type PluginToolTypeEnum = 'PUBLIC' | 'PRIVATE';

  interface PluginToolVO {
    id?: number;
    gmtCreate?: string;
    gmtModified?: string;
    creator?: string;
    lastModifyUser?: string;
    avatar?: string;
    toolId?: string;
    toolName?: string;
    toolDesc?: string;
    agentId?: string;
    toolbarDisplay?: boolean;
    toolboxDisplay?: boolean;
    source?: string;
    deleteStatus?: number;
    toolType?: string;
    colorAvatar?: string;
    toolbarAvatar?: string;
    owners?: string;
    status?: string;
    registration?: string;
    /** 工具调用类型 */
    interface_type?: string;
  }

  interface PromptRequest {
    /** LLM模型 */
    llmModel?: string;
    /** 温度 */
    temperature?: number;
    /** 内容 */
    content?: string;
  }

  interface PublishWebModelRequest {
    /** 页面模型id */
    webModelId?: string;
  }

  interface QAFileEntity {
    fileId?: string;
    gmtCreate?: string;
    gmtModified?: string;
    id?: string;
    knowledgeBaseId?: string;
    fileName?: string;
    fileStatus?: string;
    fileSize?: number;
    errorMsg?: string;
  }

  interface QAFileUpload {
    /** 文件名 */
    fileName?: string;
    /** 文件id */
    fileId?: string;
    /** 是否成功 */
    success?: boolean;
    /** 错误信息 */
    errorMsg?: string;
  }

  interface QAFileUploadResponse {
    /** 文件列表 */
    files?: Array<QAFileUpload>;
  }

  interface QAKnowledge {
    /** 知识库id */
    knowledgeBaseId?: string;
    /** 知识id */
    knowledgeId?: string;
    /** 知识id */
    qaId?: string;
    /** 问题 */
    questionContent?: string;
    /** 答案 */
    answerContent?: string;
    /** 关键字列表 */
    keys?: Array<string>;
  }

  interface QueryAgentDetailInfoRequest {
    /** 域账号 */
    userId?: string;
    /** agentId */
    agentId?: string;
    /** spaceId */
    spaceId?: string;
    /** agent 来源平台 */
    source?: string;
  }

  interface QueryAgentInfoRequest {
    /** 域账号 */
    userId?: string;
    /** agentId */
    agentId?: string;
    /** spaceId */
    spaceId?: string;
  }

  interface QueryAgentListRequest {
    /** 域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
    /** 网址 */
    url?: string;
    /** AgentId列表 */
    agentIdList?: Array<string>;
  }

  interface QueryConfigRequest {
    /** 域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
  }

  interface QueryEffectiveLinkPageRequest {
    /** 每页大小 */
    pageSize: number;
    /** 当前页 */
    currentPage: number;
    /** 页面模型id */
    webModelId?: string;
    /** 生效链接 */
    url?: string;
    /** 评论信息 */
    remark?: string;
  }

  interface QueryListRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 工具展示类型 1:TOOLBOX：工具箱 2:TOOLBAR：划词 3:空值：都展示 */
    toolDisplayType?: string;
  }

  interface QueryModelDetailListRequest {
    /** 页面模型 ID 列表 */
    webModelIdList?: Array<string>;
    /** 是否为线上版本 */
    online?: boolean;
  }

  interface QueryModelDetailVO {
    /** 页面id */
    webModelId?: string;
    /** 创建者 */
    creator?: string;
    /** 创建者花名 */
    nickName?: string;
    /** 页面名称 */
    name?: string;
    /** 版本状态 */
    status?: string;
    /** 创建时间 */
    gmtCreate?: string;
    /** 更新时间 */
    gmtModified?: string;
    /** URL 匹配规则 */
    urlMatchRule?: UrlMatchRule;
    /** 组件 */
    originComponents?: Array<OriginComponent>;
    /** 注入组件 */
    injectComponents?: Array<InjectionComponent>;
  }

  interface QueryModelListVO {
    /** 页面id */
    webModelId?: string;
    /** 页面名称 */
    name?: string;
    /** URL 匹配规则 */
    urlMatchRule?: UrlMatchRule;
    /** 创建时间 */
    gmtCreate?: string;
    /** 更新时间 */
    gmtModified?: string;
    /** 页面模型状态 CREATING：创建中 PUBLISHED：已发布 UPGRADING：升级中 OFFLINE：已下线 */
    status?: string;
    /** 生效范围 SPECIFIC：特定 ALL：所有 */
    scope?: string;
    /** 创建人 */
    creator?: string;
    /** 花名 */
    nickName?: string;
    /** 最后操作者 */
    lastModifyUser?: string;
    /** 管理员 */
    owners?: string;
    /** 模型类型 */
    modelType?: string;
  }

  interface QueryModelPageRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 部门路径 */
    deptPath?: string;
    /** 域账号,新逻辑使用，可以不传 */
    loginName?: string;
    /** 页面名称 */
    webModelName?: string;
    /** 页面模型id */
    webModelId?: string;
    /** 版本状态 */
    status?: string;
    /** 模型类型 */
    modelType?: ModelTypeEnum;
    /** 分页大小 */
    pageSize?: number;
    /** 当前页数 */
    currentPage?: number;
  }

  interface QuerySystemConfigRequest {
    /** 用户 ID */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 配置键列表 */
    configKeys?: Array<string>;
  }

  interface QueryUniversalModelDetailVO {
    /** 页面id */
    webModelId?: string;
    /** 创建者花名 */
    nickName?: string;
    /** 页面名称 */
    name?: string;
    /** 版本状态 */
    status?: string;
    /** 生效范围 SPECIFIC：特定 ALL：所有 */
    scope?: string;
    /** 创建时间 */
    gmtCreate?: string;
    /** 更新时间 */
    gmtModified?: string;
    /** 创建人 */
    creator?: string;
    /** 管理员 */
    owners?: string;
    /** 组件 */
    components?: Array<UniversalComponent>;
  }

  interface QueryUniversalModelListVO {
    /** 页面id */
    webModelId?: string;
    /** 页面名称 */
    name?: string;
    /** URL 匹配规则 */
    universalMatchRule?: Array<UniversalMatchRule>;
    /** 创建时间 */
    gmtCreate?: string;
    /** 更新时间 */
    gmtModified?: string;
    /** 页面模型状态 CREATING：创建中 PUBLISHED：已发布 UPGRADING：升级中 OFFLINE：已下线 */
    status?: string;
    /** 生效范围 SPECIFIC：特定 ALL：所有 */
    scope?: string;
    /** 创建人 */
    creator?: string;
    /** 花名 */
    nickName?: string;
    /** 最后操作者 */
    lastModifyUser?: string;
    /** 管理员 */
    owners?: string;
    /** 模型类型 */
    modelType?: string;
  }

  type RegistrationEnum = 'manual' | 'automatic';

  interface ReleaseAgentRequest {
    /** portal-agentId */
    agentId?: string;
    /** 发布内容 */
    releaseContent?: string;
  }

  interface RequestContext {
    /** 如果指定了 agentId，则表明该机器人单独绑定了一个 agent 则直接使用该 agent，不查询 agent 与 钉钉群组的绑定关系 */
    agentId?: string;
    /** 当前对话的上下文，是否仅关注该用户的对话 true: 只关注当前用户的聊天记录作为上下文 false: 整个群组的聊天记录都会记录 */
    focusUser?: boolean;
  }

  type ResourceTypeEnum =
    | 'SPACE'
    | 'AGENT'
    | 'KNOWLEDGE_BASE'
    | 'TOOL'
    | 'CREATOR_OPERATE'
    | 'ADMIN_OPERATE'
    | 'MEMBER_OPERATE'
    | 'WEB_MODEl';

  interface ResponseBodyEmitter {
    /** Return the configured timeout value, if any. */
    timeout?: number;
    handler?: ResponseBodyEmitterHandler;
    /** Store send data before handler is initialized. */
    earlySendAttempts?: Array<OrgSpringframeworkWebServletMvcMethodAnnotationResponseBodyEmitterDataWithMediaType>;
    /** Store successful completion before the handler is initialized. */
    complete?: boolean;
    /** Store an error before the handler is initialized. */
    failure?: Throwable;
    /** After an I/O error, we don't call {@link #completeWithError} directly but
wait for the Servlet container to call us via {@code AsyncListener#onError}
on a container thread at which point we call completeWithError.
This flag is used to ignore further calls to complete or completeWithError
that may come for example from an application try-catch block on the
thread of the I/O error. */
    sendFailed?: boolean;
    timeoutCallback?: ResponseBodyEmitterDefaultCallback;
    errorCallback?: ResponseBodyEmitterErrorCallback;
    completionCallback?: ResponseBodyEmitterDefaultCallback;
  }

  type ResponseBodyEmitter$DataWithMediaType = Record<string, any>;

  type ResponseBodyEmitterDefaultCallback = Record<string, any>;

  type ResponseBodyEmitterErrorCallback = Record<string, any>;

  type ResponseBodyEmitterHandler = Record<string, any>;

  interface Result {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Record<string, any>;
    traceId?: string;
    host?: string;
  }

  type ResultCodeEnum =
    | '000'
    | 'SUCCESS'
    | '001'
    | 'DO_NOT_SHOW_ERROR'
    | '101'
    | 'ILLEGAL_ARGUMENT'
    | '102'
    | 'PERMISSION_DENIED'
    | '103'
    | 'USER_NOT_LOGIN'
    | '104'
    | 'BIZ_FAIL'
    | '110'
    | 'PRECHECK_FAIL'
    | '210'
    | 'INVOKE_SPI_FAILED'
    | '211'
    | 'SPI_INNER_ERROR'
    | '212'
    | 'BUSGROUP_NOT_EXIST'
    | '998'
    | 'SYSTEM_ERROR';

  interface Result_AgentDetailInfoVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: AgentDetailInfoVO;
    traceId?: string;
    host?: string;
  }

  interface Result_AgentInfoVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: AgentInfoVO;
    traceId?: string;
    host?: string;
  }

  interface Result_Boolean_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: boolean;
    traceId?: string;
    host?: string;
  }

  interface Result_ConfigInfoVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: ConfigInfoVO;
    traceId?: string;
    host?: string;
  }

  interface Result_DirYuQueKnowledgeVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: DirYuQueKnowledgeVO;
    traceId?: string;
    host?: string;
  }

  interface Result_EffectiveLinkVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: EffectiveLinkVO;
    traceId?: string;
    host?: string;
  }

  interface Result_GGraph_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: GGraph;
    traceId?: string;
    host?: string;
  }

  interface Result_GNode_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: GNode;
    traceId?: string;
    host?: string;
  }

  interface Result_InterfaceTypeDTO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: InterfaceTypeDTO;
    traceId?: string;
    host?: string;
  }

  interface Result_JSONObject_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Record<string, any>;
    traceId?: string;
    host?: string;
  }

  interface Result_KnowledgeEntity_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: KnowledgeEntity;
    traceId?: string;
    host?: string;
  }

  interface Result_List_AgentInfoVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<AgentInfoVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_AitorAgentDebugResponse__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<AitorAgentDebugResponse>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_ConfigInfoVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<ConfigInfoVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_Dept__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<Dept>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_DocumentResponse__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<DocumentResponse>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_GNode__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<GNode>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_GraphImportTaskDetail__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<GraphImportTaskDetail>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_LlmResponse__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<LlmResponse>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_NexaKnowledgeBaseVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<NexaKnowledgeBaseVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_NexaSessionMessageVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<NexaSessionMessageVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_OssResourceRelationResponse__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<OssResourceRelationResponse>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_PluginAgentVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<PluginAgentVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_PluginSystemConfigVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<PluginSystemConfigVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_PluginToolVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<PluginToolVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_QAFileEntity__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<QAFileEntity>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_QueryModelDetailVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<QueryModelDetailVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_QueryModelListVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<QueryModelListVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_QueryUniversalModelDetailVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<QueryUniversalModelDetailVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_QueryUniversalModelListVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<QueryUniversalModelListVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_SkillNode__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<SkillNode>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_SpaceVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<SpaceVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_String__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<string>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_ToolResultDTO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<ToolResultDTO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_ToolVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<ToolVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_UserVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<UserVO>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_YuQueBookInfo__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<YuQueBookInfo>;
    traceId?: string;
    host?: string;
  }

  interface Result_List_YuQueGroupInfo__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Array<YuQueGroupInfo>;
    traceId?: string;
    host?: string;
  }

  interface Result_Map_String_Object__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Record<string, any>;
    traceId?: string;
    host?: string;
  }

  interface Result_NexaDingProxyConfigDO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: NexaDingProxyConfigDO;
    traceId?: string;
    host?: string;
  }

  interface Result_NexaKnowledgeBaseVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: NexaKnowledgeBaseVO;
    traceId?: string;
    host?: string;
  }

  interface Result_NexaOCRRVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: NexaOCRRVO;
    traceId?: string;
    host?: string;
  }

  interface Result_NexaUserConfigVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: NexaUserConfigVO;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_AgentInfoVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_AgentInfoVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_AgentUserRelationshipVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_AgentUserRelationshipVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_ConfigInfoVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_ConfigInfoVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_EffectiveLinkVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_EffectiveLinkVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_NexaKnowledgeBaseVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_NexaKnowledgeBaseVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_NexaSessionVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_NexaSessionVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_PluginAgentVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_PluginAgentVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_PluginToolVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_PluginToolVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_QueryModelListVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_QueryModelListVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PageResultList_ToolVO__ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PageResultList_ToolVO_;
    traceId?: string;
    host?: string;
  }

  interface Result_PluginAgentVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PluginAgentVO;
    traceId?: string;
    host?: string;
  }

  interface Result_PluginSystemToolConfigVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PluginSystemToolConfigVO;
    traceId?: string;
    host?: string;
  }

  interface Result_PluginToolVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: PluginToolVO;
    traceId?: string;
    host?: string;
  }

  interface Result_QAFileUploadResponse_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: QAFileUploadResponse;
    traceId?: string;
    host?: string;
  }

  interface Result_RiskCheckReslutVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: RiskCheckReslutVO;
    traceId?: string;
    host?: string;
  }

  interface Result_ScriptContent_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: ScriptContent;
    traceId?: string;
    host?: string;
  }

  interface Result_ServiceInstanceResponse_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: ServiceInstanceResponse;
    traceId?: string;
    host?: string;
  }

  interface Result_SpaceVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: SpaceVO;
    traceId?: string;
    host?: string;
  }

  interface Result_String_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: string;
    traceId?: string;
    host?: string;
  }

  interface Result_ToolExecuteInterfaceProtocolVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: ToolExecuteInterfaceProtocolVO;
    traceId?: string;
    host?: string;
  }

  interface Result_ToolVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: ToolVO;
    traceId?: string;
    host?: string;
  }

  interface Result_TriggerServiceResponse_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: TriggerServiceResponse;
    traceId?: string;
    host?: string;
  }

  interface Result_URL_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: URL;
    traceId?: string;
    host?: string;
  }

  interface Result_UserConfigVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: UserConfigVO;
    traceId?: string;
    host?: string;
  }

  interface Result_UserResponse_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: UserResponse;
    traceId?: string;
    host?: string;
  }

  interface Result_UserScopeConfigVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: UserScopeConfigVO;
    traceId?: string;
    host?: string;
  }

  interface Result_UserVO_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: UserVO;
    traceId?: string;
    host?: string;
  }

  interface Result_Void_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: Record<string, any>;
    traceId?: string;
    host?: string;
  }

  interface Result_YuQueKnowledgeResponse_ {
    success?: boolean;
    /** 获取错误码 */
    errorCode?: string;
    /** 获取错误信息 */
    errorMessage?: string;
    /** 获取返回数据 */
    data?: YuQueKnowledgeResponse;
    traceId?: string;
    host?: string;
  }

  interface RiskCheckRequest {
    /** 用户域账号 */
    userId?: string;
    /** 检测类型 */
    detectType?: string;
    /** 检测数据 */
    detectData?: DetectData;
  }

  interface RiskCheckReslutVO {
    /** 变更ID */
    changeId?: string;
    /** 变更状态 */
    status?: string;
    /** 检测结果 */
    verdict?: string;
    /** 所有防御规则是否全部执行完成 */
    allFinish?: boolean;
    /** 消息 */
    msg?: string;
    /** 变更核心地址 */
    url?: string;
    /** 风险规则列表 */
    riskRules?: Array<RiskCheckRule>;
  }

  interface RiskCheckRule {
    /** 规则执行ID，标识一次规则的执行实例 */
    ruleExeId?: string;
    /** 防御类型，例如"预变更检查"、"灰度变更"等 */
    defenseType?: string;
    /** 规则执行结果的JSON字符串，用于存储详细信息 */
    resultJsn?: string;
    /** 详情 */
    markdownResult?: string;
    /** BLOCK:阻断变更 RELEASE:放行变更 */
    exceptionStrategy?: string;
    /** 外部规则ID，可能来源于其他系统或服务的规则标识 */
    externalRuleId?: string;
    /** 控制键，用于关联特定的控制项或策略 */
    controlKey?: string;
    /** EXE:执行 FAIL:失败 SUCC:成功 TIMEOUT:超时 */
    status?: OpsCloudChangeCheckStatusEnum;
    /** none:无结果 pass:通过 inconc:无法判断 fail:失败 */
    verdict?: OpsCloudChangeCheckVerdictEnum;
    /** 风险检查状态 */
    checkStatus?: ChangeCheckStatusEnum;
    /** 检查过程中的消息，用于描述检查结果或异常信息 */
    msg?: string;
    /** 检查相关的URL，可能指向详细报告或其他资源 */
    url?: string;
    /** 关联ID，可能用于与其他系统或对象建立联系 */
    relationId?: string;
    /** 防御阶段，例如"部署前"、"部署后"等 */
    stage?: DefenseStageEnum;
    /** 是否处于灰度状态，true表示是，false表示否 */
    grayStatus?: boolean;
    /** NO_RISK:仅预警 LOW:low risk MEDIUM:medium risk HIGH:high risk BLOCK:阻断 ROLLBACK:直接回滚 RISK_CURE:阻断 */
    riskLevel?: string;
    /** 规则或检查项的名称 */
    name?: string;
    /** 规则或检查项的所有者，可能是用户名或角色名 */
    owner?: string;
    /** 是否允许忽略该规则的结果，true表示允许，false表示不允许 */
    allowIgnore?: boolean;
    /** 是否已忽略该规则的结果，true表示已忽略，false表示未忽略 */
    ignored?: boolean;
    /** 检查开始时间 */
    gmtStart?: string;
    /** 检查结束时间 */
    gmtFinish?: string;
  }

  type RoleEnum = 'ASSISTANT' | 'SYSTEM' | 'USER';

  type ScopeEnum = 'ALL' | 'CREATING';

  interface ScriptContent {
    /** 分析方法 */
    analysisMethod?: string;
    /** 脚本内容 */
    scriptContent?: string;
  }

  interface ServiceInstance {
    /** 服务实例id */
    id?: string;
    /** 服务实例名称 */
    serviceInstanceName?: string;
  }

  interface ServiceInstanceRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 触发服务 */
    service?: TriggerServiceTypeEnum;
  }

  interface ServiceInstanceResponse {
    /** 触发服务 */
    service?: TriggerServiceTypeEnum;
    /** 服务实例列表 */
    serviceInstanceList?: Array<ServiceInstance>;
  }

  interface SessionCreateRequest {
    /** 用户域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
    /** session 过期时间 */
    expireTime?: string;
    /** 标题摘要 */
    summary?: string;
    /** 是否调试模式 */
    debugMode?: boolean;
  }

  interface SessionFeedbackRequest {
    /** 会话id */
    sessionId?: string;
    /** 反馈类型 POSITIVE：积极反馈 NEGATIVE：消极反馈 */
    feedbackType?: string;
    /** 反馈内容 */
    feedbackContent?: string;
  }

  interface SessionUpdateRequest {
    /** 用户域账号 */
    userId?: string;
    /** 会话 ID */
    sessionId?: string;
    /** 用户工号 */
    empId?: string;
    /** session 过期时间 */
    expireTime?: string;
    /** 标题摘要 */
    summary?: string;
  }

  interface SkillNode {
    /** 技能 id */
    id?: number;
    /** 下游节点 */
    children?: Array<SkillNode>;
    /** 名称 */
    title?: string;
    /** 提问模板 */
    templates?: Array<string>;
    /** 当前指令的类型 */
    instructionType?: string;
    /** 当前指令绑定的能力 key */
    instructionKey?: string;
    /** 使用说明 */
    description?: string;
    /** 开关状态，true 为开，false 为关 */
    status?: boolean;
    /** 节点类型 */
    nodeType?: string;
  }

  interface SmartToolRequest {
    /** 工具名称 */
    toolName?: string;
    /** 工具id */
    toolId?: string;
    /** 类型 */
    type?: string;
    /** 提交类型 */
    submitType?: string;
    /** 扩展字段 */
    extendContext?: Record<string, any>;
    /** 内容 */
    content?: ChatContent;
    /** submit chat返回的id */
    chatUniqueId?: string;
  }

  interface SpaceResourceResponse {
    /** agentId列表 */
    agentIdList?: Array<string>;
    /** 知识库id列表 */
    knowledgeBaseIdList?: Array<string>;
    /** 技能id列表 */
    toolIdList?: Array<string>;
  }

  type SpaceTypeEnum = 'PERSONAL' | 'GROUP';

  type SpaceUserAuthority = 'SPACE_ADMIN' | 'SPACE_MEMBER';

  interface SpaceVO {
    /** 空间 id */
    id?: number;
    /** 空间名称 */
    name?: string;
    /** 头像 */
    avatar?: string;
    /** 头像(oss) */
    ossAvatarUrl?: string;
    /** 描述 */
    description?: string;
    /** 空间类型 PERSONAL - 个人空间 GROUP - 团队空间@see com.alipay.nexa.service.dto.space.enums.SpaceTypeEnum */
    type?: string;
  }

  interface SpiltYuQueDocRequest {
    /** 知识库id */
    knowledgeBaseId?: string;
    /** 文件id */
    fileId?: string;
    /** 拆分设置 */
    processingRule?: Record<string, any>;
  }

  interface SseEmitter {
    timeout?: number;
    handler?: ResponseBodyEmitterHandler;
    /** Store send data before handler is initialized. */
    earlySendAttempts?: Array<OrgSpringframeworkWebServletMvcMethodAnnotationResponseBodyEmitterDataWithMediaType>;
    /** Store successful completion before the handler is initialized. */
    complete?: boolean;
    /** Store an error before the handler is initialized. */
    failure?: Throwable;
    /** After an I/O error, we don't call {@link #completeWithError} directly but
wait for the Servlet container to call us via {@code AsyncListener#onError}
on a container thread at which point we call completeWithError.
This flag is used to ignore further calls to complete or completeWithError
that may come for example from an application try-catch block on the
thread of the I/O error. */
    sendFailed?: boolean;
    timeoutCallback?: ResponseBodyEmitterDefaultCallback;
    errorCallback?: ResponseBodyEmitterErrorCallback;
    completionCallback?: ResponseBodyEmitterDefaultCallback;
  }

  interface StreamAgentChatAnswerDTO {
    /** 对话唯一id */
    chatUniqueId?: string;
    /** traceId */
    traceId?: string;
    /** 对话返回的类型（cover覆盖，append追加） */
    chatResultTypeCode?: string;
    /** 对话返回的内容 */
    chatAnswer?: Array<ChatAnswer>;
  }

  type TaskTypeEnum =
    | 'SINGLE_TOOL'
    | 'AITOR_SCRIPT'
    | 'AITOR_PLUGIN'
    | 'OPSGPT_AGENT'
    | 'AITOR_AGENT';

  type TextProcessOperationEnum =
    | 'EXPLAIN'
    | 'SUMMARIZE'
    | 'EMBELLISH'
    | 'CORRECT'
    | 'TRANSLATE';

  interface TextProcessRequest {
    /** 内容 */
    content?: string;
    /** 选取的操作 */
    operation?: string;
    /** 选择的模型 */
    agentId?: string;
    /** 当前语言 */
    currentLanguage?: string;
    /** 目标语言 */
    targetLanguage?: string;
  }

  type Throwable = Record<string, any>;

  type ToolDeleteStatusEnum = 'NOT_DELETED' | 'DELETED';

  type ToolDisplayTypeEnum = 'TOOLBOX' | 'TOOLBAR' | 'EMPTY';

  interface ToolExecuteInterfaceProtocolVO {
    /** 协议内容 */
    protocol?: NexaToolProtocol;
    /** 需要透传的headers */
    headers?: Record<string, any>;
  }

  interface ToolResultDTO {
    /** 同上 */
    id?: number;
    /** GMT 创建 */
    gmtCreate?: string;
    /** GMT 修改 */
    gmtModified?: string;
    /** 创建者 */
    creator?: string;
    /** 最后修改用户 */
    lastModifyUser?: string;
    /** 头像 */
    avatar?: string;
    /** 工具ID */
    toolId?: string;
    /** 工具名称 */
    toolName?: string;
    /** 工具描述 */
    toolDesc?: string;
    /** 代理ID */
    agentId?: string;
    /** 工具栏是否显示 */
    toolbarDisplay?: boolean;
    /** 工具箱是否显示 */
    toolboxDisplay?: boolean;
    /** 来源 */
    source?: string;
    /** 工具调用类型 */
    interface_type?: string;
    /** 删除状态 */
    deleteStatus?: string;
    /** 是否私有 */
    toolType?: string;
    colorAvatar?: string;
    toolbarAvatar?: string;
  }

  type ToolTypeEnum = 'API' | 'SCRIPT' | 'PLUGIN';

  interface ToolVO {
    /** 知识库 id */
    id?: number;
    /** 工具名称 */
    name?: string;
    /** 描述 */
    description?: string;
    /** 类型（api，脚本，插件）@see com.alipay.nexa.service.dto.tool.enums.ToolTypeEnum */
    type?: ToolTypeEnum;
    /** 下游工具id */
    toolId?: string;
    /** 空间id */
    spaceId?: string;
    /** 来源（Aitor，OPSGPT） */
    source?: string;
    /** 工具状态（公开,私有） */
    toolType?: string;
    /** 创建人 */
    creator?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** 最后修改人 */
    lastModifyUser?: string;
    /** 最后修改人花名 */
    lastModifyUserView?: string;
  }

  type TranslateLanguageEnum = 'CHINESE' | 'ENGLISH';

  interface TranslateRequest {
    /** 内容 */
    content?: string;
    /** 当前语言 */
    currentLanguage?: string;
    /** 目标语言 */
    targetLanguage?: string;
    /** 流式输出协议 不填默认：false，流式输出必须传入 true */
    stream?: boolean;
  }

  interface TriggerCommand {
    /** 指令枚举@see com.alipay.nexa.service.enums.TriggerCommandEnum */
    command?: string;
    /** 参数内容 */
    payload?: Record<string, any>;
  }

  type TriggerCommandEnum =
    | 'EMPTY'
    | 'SWITCH_TO_AGENT'
    | 'CHAT_WITH_AGENT'
    | 'ACTION_WITH_TOOL'
    | 'SHOW_RISK'
    | 'SHOW_ASYN_RISK'
    | 'INJECT_COMPONENT'
    | 'HIGHLIGHT_FORM_ITEM'
    | 'SHOW_DYNAMIC_CONTENT';

  type TriggerEventTypeEnum = 'INVOKE_BACKEND' | 'INVOKE_FRONTEND';

  type TriggerResponseStatusEnum = 0 | 'SUCCESS' | 1 | 'DOING' | 2 | 'FAIL';

  interface TriggerServiceRequest {
    /** 域账号 */
    userId?: string;
    /** 工号Id */
    empId?: string;
    /** 当前页面完整url */
    url?: string;
    /** 页面模型ID */
    webModelId?: string;
    /** 组件 ID */
    componentId?: string;
    /** 事件 ID */
    eventId?: string;
    /** 参数 */
    params?: Record<string, any>;
  }

  interface TriggerServiceResponse {
    /** 指令集合 */
    commands?: Array<TriggerCommand>;
    /** 执行状态@see com.alipay.nexa.service.enums.TriggerResponseStatusEnum */
    responseStatus?: number;
  }

  type TriggerServiceTypeEnum = 'AGENT' | 'TOOL' | 'RISK' | 'DYNAMIC';

  type URL = Record<string, any>;

  interface UniversalComponent {
    /** 组件的唯一标识ID。 */
    componentId?: string;
    /** 标识该组件是否为触发点组件，用于特殊交互逻辑处理。 */
    triggerPoint?: boolean;
    /** 组件的关键键值，用于区分和识别不同组件，需在当前页面模型中唯一。 */
    componentKey?: string;
    /** 组件的展示名称，通常为中文，便于用户理解和配置。 */
    name?: string;
    /** 组件类型 */
    componentType?: string;
    /** 与该组件关联的事件列表，描述了组件在不同交互下的行为。 */
    events?: Array<ComponentEvent>;
    /** 关联id */
    relatedId?: string;
    /** 组件样式 */
    props?: string;
    /** 偏移量 */
    position?: string;
  }

  type UniversalComponentTypeEnum = 'WARING' | 'DIALOG';

  interface UniversalMatchRule {
    /** 生效链接 */
    domain?: string;
    /** 是否开启数据传输 */
    enable?: boolean;
  }

  interface UpdateLinkRequest {
    /** 页面模型id */
    webModelId?: string;
    /** 生效链接id */
    linkId?: string;
    /** 生效链接 */
    url?: string;
    /** 是否开启数据传输 */
    enable?: boolean;
    /** 评论信息 */
    remark?: string;
  }

  interface UpdatePluginAgentRequest {
    /** 同上 */
    id?: number;
    /** GMT 创建 */
    gmtCreate?: string;
    /** GMT修改 */
    gmtModified?: string;
    /** 代理 ID */
    agentId?: string;
    /** 代理名称 */
    agentName?: string;
    /** 头像 */
    avatar?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 提示语 */
    agentPrompt?: string;
    /** 代理类型 */
    agentType?: string;
    /** agent类型 */
    buildType?: string;
    /** 原来的source */
    oldSource?: string;
    /** 更新后的source */
    newSource?: string;
    /** 是否是前端agent */
    agentChat?: boolean;
    /** agent管理员 */
    owners?: string;
    /** 上次修改用户 */
    lastModifyUser?: string;
    /** 地位 */
    status?: string;
    /** 删除状态 */
    deleteStatus?: number;
    /** 注册 */
    registration?: string;
    /** 接口调用 */
    interfaceCall?: boolean;
    /** 聊天配置 */
    chatConfig?: Record<string, any>;
    /** 接口配置 */
    interfaceConfig?: Record<string, any>;
  }

  interface UpdateToolRequest {
    /** 同上 */
    id?: number;
    /** 用户域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
    /** 头像 */
    avatar?: string;
    /** 工具名称 */
    toolId?: string;
    /** 工具名称 */
    toolName?: string;
    /** 工具描述 */
    toolDesc?: string;
    /** 代理ID */
    agentId?: string;
    /** 工具栏是否显示 */
    toolbarDisplay?: boolean;
    /** 工具箱是否显示 */
    toolboxDisplay?: boolean;
    /** 是否私有 */
    toolType?: string;
    /** 来源 */
    source?: string;
    /** 彩色头像 */
    colorAvatar?: string;
    /** 工具栏头像 */
    toolbarAvatar?: string;
    /** 管理员 */
    owners?: string;
    /** 状态 */
    status?: string;
  }

  interface UpdateYuQueKnowledgeRequest {
    /** 知识库id */
    knowledgeBaseId?: string;
    /** 知识id */
    knowledgeId?: string;
    /** 问题 */
    questionContent?: string;
    /** 答案 */
    answerContent?: string;
  }

  interface UploadQAFileRequest {
    /** 知识库id */
    knowledgeBaseId?: string;
    /** 文件 */
    files?: Array<any>;
  }

  interface UpsertInjectionComponentRequest {
    /** 用户域账号 */
    userId?: string;
    /** 用户工号 */
    empId?: string;
    /** 页面模型id */
    webModelId?: string;
    /** 组件 ID */
    componentId?: string;
    /** 组件变量 */
    componentKey?: string;
    /** 组件名称 */
    name?: string;
    /** 父组件id */
    parentComponentKey?: string;
    /** 组件样式 */
    props?: string;
    /** 偏移量 */
    position?: Record<string, any>;
  }

  interface UpsertInteractionRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 触发点 ID */
    eventId?: string;
    /** 模型类型 ● UNIVERSAL：通用 ● SPECIFIC：特定 */
    modelType?: string;
    /** 父组件 ID */
    parentComponentId?: string;
    /** 触发方式 1:CLICK：点击 */
    triggerMethod?: string;
    /** 触发事件 1:InvokeBackend ：调用后端 2:InvokeFrontend：调用前端 */
    triggerEvent?: string;
    /** 触发服务 */
    service?: string;
    /** 服务实例 外部url */
    serviceInstance?: Record<string, any>;
    /** 参数 */
    payload?: Record<string, any>;
  }

  interface UpsertOriginComponentRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 页面模型id */
    webModelId?: string;
    /** 组件名称 */
    name?: string;
    /** 组件 ID */
    componentId?: string;
    /** 组件变量 */
    componentKey?: string;
    /** 页面元素选择器 */
    selector?: string;
  }

  interface UpsertPluginAgentRequest {
    /** 同上 */
    id?: number;
    /** GMT 创建 */
    gmtCreate?: string;
    /** GMT修改 */
    gmtModified?: string;
    /** 代理 ID */
    agentId?: string;
    /** 代理名称 */
    agentName?: string;
    /** 头像 */
    avatar?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 提示语 */
    agentPrompt?: string;
    /** 代理类型 */
    agentType?: string;
    /** agent类型 */
    buildType?: string;
    /** 源 */
    source?: string;
    /** 是否是前端agent */
    agentChat?: boolean;
    /** agent管理员 */
    owners?: string;
    /** 上次修改用户 */
    lastModifyUser?: string;
    /** 地位 */
    status?: string;
    /** 删除状态 */
    deleteStatus?: number;
    /** 注册 */
    registration?: string;
    /** 接口调用 */
    interfaceCall?: boolean;
    /** 聊天配置 */
    chatConfig?: Record<string, any>;
    /** 接口配置 */
    interfaceConfig?: Record<string, any>;
  }

  interface UpsertUniversalComponentRequest {
    /** 组件 ID */
    componentId?: string;
    /** Web 模型 ID */
    webModelId?: string;
    /** 组件类型 */
    componentType?: string;
    /** 关联id */
    relatedId?: string;
    /** 名字 */
    name?: string;
    /** 组件样式 */
    props?: string;
    /** 偏移量 */
    position?: string;
  }

  interface UpsertWebModelRequest {
    /** 域账号 */
    userId?: string;
    /** 工号 */
    empId?: string;
    /** 页面名称 */
    name?: string;
    /** 页面模型 ID */
    webModelId?: string;
    /** URL 匹配规则 */
    urlMatchRule?: UrlMatchRule;
    /** 管理员 */
    owners?: string;
    /** 模型类型 */
    modelType?: ModelTypeEnum;
  }

  interface UrlMatchRule {
    /** 域名列表 */
    domains?: Array<string>;
    /** 路径模式 */
    pathPattern?: string;
    /** 示例 URL */
    exampleUrl?: string;
  }

  interface User {
    name?: string;
    age?: number;
  }

  interface UserConfigVO {
    /** 工具栏配置 */
    toolbar?: string;
  }

  interface UserResponse {
    /** 用户分页信息 */
    userList?: Array<UserVO>;
    /** 部门信息 */
    deptList?: Array<Dept>;
  }

  interface UserScopeConfigVO {
    /** 生效范围 SPECIFIC：特定 ALL：所有 */
    scope?: string;
    /** 用户列表 */
    userList?: Array<UserVO>;
    /** 部门一览 */
    deptList?: Array<Dept>;
  }

  interface UserVO {
    /** 账号id */
    id?: number;
    /** 员工工号 */
    empId?: string;
    /** 员工姓名 */
    lastName?: string;
    /** 员工花名 */
    nickNameCn?: string;
    /** 员工类型：R,正式; O,外包; W,部门公共账号 */
    userType?: string;
    /** 部门编号 */
    depId?: string;
    /** 常用邮箱，一个人可以有多个邮箱，这里是常用邮箱 */
    email?: string;
    /** 登录账号名 */
    loginName?: string;
    /** 员工头像 */
    employeeAvatar?: string;
    /** 个人空间 id */
    spaceId?: string;
    /** 部门名称 */
    deptName?: string;
    /** 部门路径 */
    deptPath?: string;
    /** 个人空间 名称 */
    spaceName?: string;
    /** 是否有空间或者agent权限，默认没有 */
    authorized?: boolean;
    /** 是否为超级管理员 */
    superAdmin?: boolean;
    /** 是否为插件超级管理员 */
    pluginSuperAdmin?: boolean;
    /** 是否插件后台管理员 */
    pluginAdmin?: boolean;
    /** 服务管理白名单 */
    serviceWhiteList?: boolean;
  }

  type VersionStatusEnum =
    | 'PENDING'
    | 'CREATING'
    | 'PUBLISHED'
    | 'UPGRADING'
    | 'OFFLINE';

  type WebModelScopeEnum = 'SPECIFIC' | 'ALL';

  interface YuQue {
    /** 获取书籍标识符 */
    bookSlug?: string;
    /** 获取群组登录名 */
    groupLogin?: string;
    /** 获取群组名称 */
    groupName?: string;
    /** 获取知识库ID */
    knowledgeBaseId?: string;
    /** 获取名称 */
    name?: string;
    type?: string;
  }

  interface YuQueBookInfo {
    /** 文档库 id */
    bookSlug?: string;
    /** 文档库名称 */
    name?: string;
    /** 文档目录结构 */
    docs?: Array<YuQueDocInfo>;
  }

  interface YuQueBookRequest {
    /** 文档库 id */
    bookSlug?: string;
    /** 选中文档 id 列表 */
    docs?: Array<string>;
  }

  interface YuQueDocInfo {
    /** 文章 id */
    docSlug?: string;
    /** 文章标题 */
    title?: string;
    /** 类型 DOC:文档, LINK:外链, TITLE:分组 */
    type?: string;
    /** 父节点docSlug */
    parentDocSlug?: string;
    /** 第一个子节点docSlug */
    childDocSlug?: string;
    /** 同级前一个节点 */
    prevDocSlug?: string;
    /** 同级后一个节点 */
    siblingDocSlug?: string;
    /** 文章是否被选中 */
    selected?: boolean;
    /** 文章不可被选中原因 */
    invalidReason?: string;
    /** 同步状态 */
    syncStatus?: string;
    /** 上次同步成功时间 毫秒 */
    syncTimeMs?: number;
  }

  interface YuQueGroupInfo {
    /** 语雀团队 id */
    groupLogin?: string;
    /** 语雀团队名称 */
    name?: string;
    /** 授权类型，个人或者token */
    authorizeType?: GroupAuthorizeTypeEnum;
    /** 头像 */
    avatarUrl?: string;
  }

  interface YuQueGroupRequest {
    /** 选中语雀团队 id */
    groupLogin?: string;
    /** 团队名称 */
    groupName?: string;
    /** 选中语雀知识库列表 */
    books?: Array<YuQueBookRequest>;
  }

  interface YuQueKnowledgeBaseRequest {
    /** 要更新的知识库 id */
    knowledgeBaseId?: string;
    /** token */
    token?: string;
    /** 来源 */
    source?: string;
  }

  interface YuQueKnowledgeResponse {
    fileStatus?: string;
    knowledgebaseId?: string;
    knowledges?: Array<Knowledge>;
  }

  interface YuQueSpaceRequest {
    /** 要更新的知识库 id */
    knowledgeBaseId?: string;
    /** 选中的要更新的语雀团队列表 */
    groups?: Array<YuQueGroupRequest>;
  }
}
