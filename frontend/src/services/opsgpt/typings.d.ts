/* eslint-disable */
// 该文件由 OneAPI 自动生成，请勿手动修改！

declare namespace OPSGPT_API {
  type ActionButtonStyle = 'HORIZONTAL' | 'VERTICAL';

  interface AddAgentScenarioGroupRequest {
    /** 父分组 id */
    parent?: number;
    /** 分组名称 */
    name?: string;
    /** 节点类型，分组、场景、预设分组、预设场景@see com.alipay.opsgpt.model.enums.agent.ScenarioTypeEnum */
    nodeType?: string;
    /** 绑定的 agentId */
    agentId?: string;
    /** 场景集合 */
    agentScenario?: Array<AgentScenarioRequest>;
    /** 操作人 */
    operator?: string;
    /** 预置分组 id */
    pregroup?: string;
    /** 描述信息 */
    instruction?: string;
  }

  interface AdvancedApiMeta {
    /** request 转换脚本 */
    requestGroovy?: string;
    /** response 转换脚本 */
    responseGroovy?: string;
    /** tool 出入参结构定义 */
    toolDef?: string;
    /** api 定义路径 */
    apiPath?: string;
    /** api 定义 schema */
    apiSchema?: string;
    /** api 调用 schema */
    manifestSchema?: string;
    /** tag 信息 */
    toolTag?: string;
  }

  interface AdvancedConfig {
    /** 指定执行任务类型 */
    specificType?: TaskTypeEnum;
    /** 指定执行的任务 id */
    specificKey?: string;
  }

  interface AdvancedInfo {
    /** 输出类型 */
    outputType?: string;
    /** 暂停策略，需要暂停的阶段要等待用户确认后才继续执行 */
    suspendStages?: Array<string>;
  }

  interface Agent {
    /** 主键 */
    id?: number;
    /** agent唯一主键 */
    agentId?: string;
    /** agent类型，私有，公共，官方 */
    agentType?: string;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** agent名称 */
    name?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 修改者 */
    operatorModified?: string;
    /** 是否已删除(0表示未删除) */
    deleted?: boolean;
    /** 头像 */
    avatar?: string;
    /** 开场白 */
    prologue?: string;
    /** 提问示例 */
    questionSample?: string;
    /** 选择Tool的分数阈值 */
    toolSelectScore?: string;
    /** Tool进行总结时的Summary Prompt模板 */
    toolSummaryPromptTmpl?: string;
    /** 知识库Tool */
    knowledgeBaseTool?: string;
    /** 高级配置 */
    advancedConfig?: AgentAdvancedConfig;
    /** 内部配置，用来存储一些不需要展示给用户的自动生成的配置@see AgentInnerConfig */
    innerConfig?: AgentInnerConfig;
    /** debug版本 */
    debugVersion?: number;
    /** online版本 */
    onlineVersion?: number;
    /** 状态 */
    status?: string;
  }

  interface AgentAdvancedConfig {
    /** Tool选择的模式@see ToolSelectMethodEnum */
    selectMethod?: string;
    /** 利用大模型进行Tool选择时候的prompt */
    selectPrompt?: string;
    /** 是否在对话框展示场景树，灵思用 */
    showScenario?: boolean;
    /** 是否在对话框展示开场白，灵思用 */
    showPrologue?: boolean;
    /** 是否展示上传文件 button，灵思用 */
    showUploadFileButton?: boolean;
    /** 是否定时更新语雀文档 1-开启; 其他-不开启 */
    updateDocs?: number;
    /** 通用问答模型 */
    commonQaModel?: string;
  }

  interface AgentChatServiceImplOpsgptInstruction {
    /** 指令类型，AGENT，SINGLE_TOOL */
    instructionType?: string;
    /** 指令 id, agentId，toolKey */
    instructionKey?: string;
  }

  interface AgentDetailInfo {
    /** agentId */
    agentId?: string;
    /** 创建人 */
    creator?: string;
    /** agent name */
    name?: string;
    /** 描述 */
    description?: string;
    /** 头像 */
    avatarUrl?: string;
    /** 来源系统 */
    platform?: string;
    /** 创建时间（用于排序） */
    gmtCreate?: string;
    /** 扩展信息 */
    extendContext?: Record<string, any>;
    /** agent配置 */
    agentConfig?: Record<string, any>;
  }

  interface AgentFullInfo {
    /** 主键 */
    id?: number;
    /** agent唯一主键 */
    agentId?: string;
    /** agent类型，私有，公共，官方 */
    agentType?: string;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** agent名称 */
    name?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 修改者 */
    operatorModified?: string;
    /** 是否已删除(0表示未删除) */
    deleted?: boolean;
    /** 头像 */
    avatar?: string;
    /** 开场白 */
    prologue?: string;
    /** 提问示例 */
    questionSample?: Array<string>;
    /** 选择Tool的分数阈值 */
    toolSelectScore?: string;
    /** Tool进行总结时的Summary Prompt模板 */
    toolSummaryPromptTmpl?: string;
    /** 用户列表
key: domainName, value: role */
    userRoleMap?: Record<string, any>;
    /** Tool列表 */
    toolBriefInfoList?: Array<ToolBriefInfo>;
    /** 知识库Tool */
    knowledgeBaseTool?: string;
    /** 高级配置 */
    advancedConfig?: AgentAdvancedConfig;
    /** 内部配置，用来存储一些不需要展示给用户的自动生成的配置@see AgentInnerConfig */
    innerConfig?: AgentInnerConfig;
    /** 正在编辑Debug的版本号 */
    debugVersion?: number;
    /** 线上版本号 */
    onlineVersion?: number;
    /** 状态 */
    status?: string;
    /** 详细的用户授权关系@return  */
    fullRoleUserInfo?: Array<AgentRoleUserInfo>;
  }

  interface AgentInfo {
    /** agentId */
    agentId?: string;
    /** 创建人 */
    creator?: string;
    /** agent name */
    name?: string;
    /** 描述 */
    description?: string;
    /** 头像 */
    avatarUrl?: string;
    /** 来源系统 */
    platform?: string;
    /** 创建时间（用于排序） */
    gmtCreate?: string;
  }

  interface AgentInnerConfig {
    /** Dima平台的项目ID */
    dimaProjectId?: string;
    /** 绑定的知识库ID */
    knowledgeBaseList?: Array<KnowledgeBase>;
    /** 知识库查询配置 */
    knowledgeBaseQueryConfig?: string;
  }

  interface AgentLLMModel {
    /** 模型头像 */
    avatar?: string;
    /** 模型名称 */
    name?: string;
    /** 模型 code */
    code?: string;
  }

  interface AgentModel {
    /** 未选中场景时，对话框默认的类型 GPT: 大模型，普通对话框， SINGLE_TOOL: 单 tool 调用，普通对话框 CODE_INTERPRETER:
code+，文件上传，intention 的格式为 json */
    defaultType?: string;
    /** 未选中场景时，对话框默认传该 model */
    defaultModel?: Model;
  }

  interface AgentObject {
    id?: string;
    name?: string;
    description?: string;
    metadata?: Record<string, any>;
  }

  interface AgentQueryRequest {
    /** 批量查询的 agentId */
    agentIds?: Array<string>;
    /** 查询用户域账号 */
    domainAccount?: string;
  }

  interface AgentRoleUserInfo {
    /** 花名 */
    nickName?: string;
    /** 工号 */
    staffNo?: string;
    /** 域账号 */
    loginAccount?: string;
    /** 真名 */
    name?: string;
    /** user 的类型 */
    role?: string;
  }

  interface AgentScenarioDO {
    /** This property corresponds to db column <tt>id</tt>. */
    id?: number;
    /** This property corresponds to db column <tt>gmt_create</tt>. */
    gmtCreate?: string;
    /** This property corresponds to db column <tt>gmt_modified</tt>. */
    gmtModified?: string;
    /** This property corresponds to db column <tt>name</tt>. */
    name?: string;
    /** This property corresponds to db column <tt>parent</tt>. */
    parent?: number;
    /** This property corresponds to db column <tt>node_type</tt>. */
    nodeType?: string;
    /** This property corresponds to db column <tt>task_type</tt>. */
    taskType?: string;
    /** This property corresponds to db column <tt>agent_id</tt>. */
    agentId?: string;
    /** This property corresponds to db column <tt>binding_key</tt>. */
    bindingKey?: string;
    /** This property corresponds to db column <tt>templates</tt>. */
    templates?: string;
    /** This property corresponds to db column <tt>operator</tt>. */
    operator?: string;
    /** This property corresponds to db column <tt>is_show</tt>. */
    isShow?: string;
    /** This property corresponds to db column <tt>pregroup</tt>. */
    pregroup?: string;
    /** This property corresponds to db column <tt>instruction</tt>. */
    instruction?: string;
    /** This property corresponds to db column <tt>version</tt>. */
    version?: number;
  }

  interface AgentScenarioRequest {
    /** 场景 id */
    id?: number;
    /** 节点名称 */
    name?: string;
    /** 父节点 id */
    parent?: number;
    /** 节点类型，分组、场景、预设分组、预设场景@see com.alipay.opsgpt.model.enums.agent.ScenarioTypeEnum */
    nodeType?: string;
    /** 任务类型@see com.alipay.opsconvobus.model.enums.TaskModeEnum，本期仅支持 SINGLE_TOOL */
    taskType?: string;
    /** 绑定的 agentId */
    agentId?: string;
    /** 绑定的 key，SINGLE_TOOL 绑定 toolKey */
    bindingKey?: string;
    /** 问题模板 */
    templates?: Array<string>;
    /** 预置分组 id */
    pregroup?: string;
    /** 操作人 */
    operator?: string;
    /** 描述信息 */
    instruction?: string;
  }

  interface AgentScenarioResponse {
    /** 场景 id */
    id?: number;
    /** 节点名称 */
    name?: string;
    /** 父节点 id */
    parent?: number;
    /** 节点类型，分组、场景、预设分组、预设场景@see com.alipay.opsgpt.model.enums.agent.ScenarioTypeEnum */
    nodeType?: string;
    /** 任务类型@see com.alipay.opsconvobus.model.enums.TaskModeEnum，本期仅支持 SINGLE_TOOL */
    taskType?: string;
    /** 绑定的 key，SINGLE_TOOL 绑定 toolKey */
    bindingKey?: string;
    /** 预分组 id */
    pregroup?: string;
    /** 问题模板 */
    templates?: string;
    /** 子节点 */
    childList?: Array<AgentScenarioResponse>;
    /** 是否隐藏指令 0：隐藏；1：显示 */
    isShow?: string;
    /** 额外信息 */
    extra?: Record<string, any>;
    /** 介绍信息 */
    instruction?: string;
  }

  interface AgentToolOpsRequest {
    /** agentId */
    agentId?: string;
    /** Tool Map key: toolId, value: toolKey */
    toolMap?: Record<string, any>;
    /** 操作者 */
    operator?: string;
  }

  interface AgentUserOpsRequest {
    /** agentId */
    agentId?: string;
    /** 用户Map key: userId, value: role */
    userRoleMap?: Record<string, any>;
    /** 操作者 */
    operator?: string;
  }

  interface AgentYuQueBookInfo {
    /** bookSlug */
    bookSlug?: string;
    /** book name */
    name?: string;
    /** docs */
    docs?: Array<AgentYuQueDocInfo>;
  }

  interface AgentYuQueDocInfo {
    /** docSlug */
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

  type AlipayCommonErrorCode = '10000' | 'SUCCESS' | '40004' | 'BIZ_FAILED';

  type AlipayOpsgptErrorCode =
    | 'SYSTEM_ERROR'
    | 'UNKNOWN_ERROR'
    | 'INVALID_PARAMETER'
    | 'TIMEOUT'
    | 'TASK_NOT_FINISH'
    | '40001'
    | 'ILLEGAL_TYPE_PARAM'
    | '40002'
    | 'MISSING_AGENT_ID'
    | '40003'
    | 'ILLEGAL_AGENT_ID'
    | '40005'
    | 'MISSING_OPERATOR'
    | '40006'
    | 'MISSING_TASK_SOURCE'
    | '40007'
    | 'ILLEGAL_TASK_SOURCE'
    | '40008'
    | 'ILLEGAL_INTENTION';

  interface AlipayResponse {
    /** Getter method for property <tt>code</tt>. */
    code?: string;
    msg?: string;
    subCode?: string;
    subMsg?: string;
    body?: string;
    params?: Record<string, any>;
  }

  interface AntCIComponentRestRequest {
    /** 对应任务执行单id */
    executionTaskId?: string;
    /** 对应声明的输入信息 */
    inputs?: Record<string, any>;
    /** 异步回调的restUrl */
    submitResultUrl?: string;
    /** 异步回调的header信息 */
    submitResultHeaders?: Record<string, any>;
    /** 之前已经渲染的组件输出信息 */
    renderedOutputs?: Record<string, any>;
  }

  interface AntCIComponentRestResponse {
    type?: string;
    executionTaskId?: string;
    status?: string;
    statusMsg?: string;
    statusHtml?: string;
    logUrl?: string;
    artifacts?: Record<string, any>;
    outputs?: Record<string, any>;
    date?: string;
  }

  type ApiCreateTypeEnum =
    | 'GPT_ONE_API'
    | 'GPT_ONE_API_AUTO'
    | 'GPT_ONE_API_TR_AUTO'
    | 'GPT_ISP_AUTO'
    | 'GPT_MANUAL'
    | 'CVBS_ADVANCED';

  interface ApiMeta {
    /** 当前 tool 的创建类型 oneApi，手动接入，opsconvobus 自定义方式接入 */
    createType?: ApiCreateTypeEnum;
    /** meta 元数据信息 根据 createType 不同，meta 的结构不同 createType = GPT_ONE_API ：对应结构 GPTOneApiApiMeta，前端
oneapi 方式创建时 createType = GPT_MANUAL ： 对应结构 GPTManualApiMeta createType = CVBS_ADVANCED ：对应结构
AdvancedApiMeta */
    meta?: Record<string, any>;
    /** 业务唯一键，表明该 tool 的具体业务，一般设置为 interfaceMethodName，即服务.方法 */
    uniqueKey?: string;
    /** 接口所属产品，即来源平台 */
    product?: string;
  }

  interface ApiMeta_AdvancedApiMeta_ {
    /** 当前 tool 的创建类型 oneApi，手动接入，opsconvobus 自定义方式接入 */
    createType?: ApiCreateTypeEnum;
    /** meta 元数据信息 根据 createType 不同，meta 的结构不同 createType = GPT_ONE_API ：对应结构 GPTOneApiApiMeta，前端
oneapi 方式创建时 createType = GPT_MANUAL ： 对应结构 GPTManualApiMeta createType = CVBS_ADVANCED ：对应结构
AdvancedApiMeta */
    meta?: AdvancedApiMeta;
    /** 业务唯一键，表明该 tool 的具体业务，一般设置为 interfaceMethodName，即服务.方法 */
    uniqueKey?: string;
    /** 接口所属产品，即来源平台 */
    product?: string;
  }

  interface ApiMeta_GPTManualApiMeta_ {
    /** 当前 tool 的创建类型 oneApi，手动接入，opsconvobus 自定义方式接入 */
    createType?: ApiCreateTypeEnum;
    /** meta 元数据信息 根据 createType 不同，meta 的结构不同 createType = GPT_ONE_API ：对应结构 GPTOneApiApiMeta，前端
oneapi 方式创建时 createType = GPT_MANUAL ： 对应结构 GPTManualApiMeta createType = CVBS_ADVANCED ：对应结构
AdvancedApiMeta */
    meta?: GPTManualApiMeta;
    /** 业务唯一键，表明该 tool 的具体业务，一般设置为 interfaceMethodName，即服务.方法 */
    uniqueKey?: string;
    /** 接口所属产品，即来源平台 */
    product?: string;
  }

  interface ApiMeta_GPTOneApiApiMeta_ {
    /** 当前 tool 的创建类型 oneApi，手动接入，opsconvobus 自定义方式接入 */
    createType?: ApiCreateTypeEnum;
    /** meta 元数据信息 根据 createType 不同，meta 的结构不同 createType = GPT_ONE_API ：对应结构 GPTOneApiApiMeta，前端
oneapi 方式创建时 createType = GPT_MANUAL ： 对应结构 GPTManualApiMeta createType = CVBS_ADVANCED ：对应结构
AdvancedApiMeta */
    meta?: GPTOneApiApiMeta;
    /** 业务唯一键，表明该 tool 的具体业务，一般设置为 interfaceMethodName，即服务.方法 */
    uniqueKey?: string;
    /** 接口所属产品，即来源平台 */
    product?: string;
  }

  interface ApiMeta_T_ {
    /** 当前 tool 的创建类型 oneApi，手动接入，opsconvobus 自定义方式接入 */
    createType?: ApiCreateTypeEnum;
    /** meta 元数据信息 根据 createType 不同，meta 的结构不同 createType = GPT_ONE_API ：对应结构 GPTOneApiApiMeta，前端
oneapi 方式创建时 createType = GPT_MANUAL ： 对应结构 GPTManualApiMeta createType = CVBS_ADVANCED ：对应结构
AdvancedApiMeta */
    meta?: any;
    /** 业务唯一键，表明该 tool 的具体业务，一般设置为 interfaceMethodName，即服务.方法 */
    uniqueKey?: string;
    /** 接口所属产品，即来源平台 */
    product?: string;
  }

  interface AppToolUpsert {
    /** 来源 */
    source?: string;
    /** 应用名 */
    appName?: string;
    /** 分支 */
    branch?: string;
    /** 白名单，正则表达式，严格匹配大小写，匹配的值为 ${interface}.${method}，如 TestController.hello，SampleFacade.test
可以不传，不传则同步所有 */
    whiteList?: Array<string>;
    /** 黑名单，正则表达式，严格匹配大小写，匹配的值为 ${interface}.${method}，如 TestController.hello，SampleFacade.test
优先级高于白名单，即黑名单匹配到的一定会被过滤 */
    blackList?: Array<string>;
    /** 预发请求域名 */
    preEndpoint?: string;
    /** 线上请求域名 */
    prodEndpoint?: string;
  }

  interface Artifact {
    name?: string;
    type?: string;
    url?: string;
    path?: string;
    size?: number;
  }

  interface AsyncRecordRequest {
    /** task中stepId */
    stepId?: string;
    /** 执行是否成功 */
    success?: boolean;
    /** tool执行结果或报错信息 */
    toolResponse?: string;
  }

  interface AtUser {
    /** Gets get dingtalk id. */
    dingtalkId?: string;
  }

  interface Attachment {
    file_id?: string;
  }

  interface BaseGroovyScripts {
    /** 自定义import 信息 */
    importsScript?: string;
    /** 自定义预处理脚本 */
    preScript?: string;
    /** 自定义后处理脚本 */
    postScript?: string;
  }

  interface BasePageRequest {
    /** 分页数 */
    pageNum?: number;
    /** 每页大小 */
    pageSize?: number;
    /** 起始位置 */
    startIndex?: number;
  }

  interface BasePageResult {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Record<string, any>;
    /** 当前页码 */
    pageNo?: number;
    /** 每页条数 */
    pageSize?: number;
    /** 总条目数 */
    totalCount?: number;
  }

  interface BasePageResult_List_MsgRecord__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<MsgRecord>;
    /** 当前页码 */
    pageNo?: number;
    /** 每页条数 */
    pageSize?: number;
    /** 总条目数 */
    totalCount?: number;
  }

  interface BasePageResult_List_SessionRecord__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<SessionRecord>;
    /** 当前页码 */
    pageNo?: number;
    /** 每页条数 */
    pageSize?: number;
    /** 总条目数 */
    totalCount?: number;
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

  interface BaseResult_AgentFullInfo_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: AgentFullInfo;
  }

  interface BaseResult_AgentModel_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: AgentModel;
  }

  interface BaseResult_AgentScenarioResponse_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: AgentScenarioResponse;
  }

  interface BaseResult_Boolean_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: boolean;
  }

  interface BaseResult_BuserviceUser_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: BuserviceUser;
  }

  interface BaseResult_ExcelData_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: ExcelData;
  }

  interface BaseResult_FeedBack_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: FeedBack;
  }

  interface BaseResult_GGraph_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: GGraph;
  }

  interface BaseResult_GNode_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: GNode;
  }

  interface BaseResult_GPTOneApiApiMeta_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: GPTOneApiApiMeta;
  }

  interface BaseResult_GroovyScripts_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: GroovyScripts;
  }

  interface BaseResult_Integer_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: number;
  }

  interface BaseResult_JSONArray_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: JSONArray;
  }

  interface BaseResult_KnowledgeBaseCreateResponse_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: KnowledgeBaseCreateResponse;
  }

  interface BaseResult_List_AgentLLMModel__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<AgentLLMModel>;
  }

  interface BaseResult_List_AgentScenarioResponse__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<AgentScenarioResponse>;
  }

  interface BaseResult_List_AgentYuQueBookInfo__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<AgentYuQueBookInfo>;
  }

  interface BaseResult_List_Agent__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<Agent>;
  }

  interface BaseResult_List_ConvoRFile__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<ConvoRFile>;
  }

  interface BaseResult_List_FeedBack__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<FeedBack>;
  }

  interface BaseResult_List_GNode__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<GNode>;
  }

  interface BaseResult_List_GraphImportTaskDetail__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<GraphImportTaskDetail>;
  }

  interface BaseResult_List_MasterDataDepartment__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<MasterDataDepartment>;
  }

  interface BaseResult_List_MasterDataUser__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<MasterDataUser>;
  }

  interface BaseResult_List_Model__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<Model>;
  }

  interface BaseResult_List_MsgRecord__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<MsgRecord>;
  }

  interface BaseResult_List_String__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<string>;
  }

  interface BaseResult_List_Tool__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<Tool>;
  }

  interface BaseResult_List_YuQueGroupInfoWithoutDoc__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<YuQueGroupInfoWithoutDoc>;
  }

  interface BaseResult_List_YuQueGroupInfo__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<YuQueGroupInfo>;
  }

  interface BaseResult_Long_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: number;
  }

  interface BaseResult_Map_String_BuserviceUser__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Record<string, any>;
  }

  interface BaseResult_Map_String_MasterDataUser__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Record<string, any>;
  }

  interface BaseResult_Map_String_String__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Record<string, any>;
  }

  interface BaseResult_ModelNode_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: ModelNode;
  }

  interface BaseResult_MsgRecord_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: MsgRecord;
  }

  interface BaseResult_Object_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Record<string, any>;
  }

  interface BaseResult_PaginationResult_Agent__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: PaginationResult_Agent_;
  }

  interface BaseResult_PaginationResult_Tool__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: PaginationResult_Tool_;
  }

  interface BaseResult_SessionRecord_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: SessionRecord;
  }

  interface BaseResult_Set_String__ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Array<string>;
  }

  interface BaseResult_String_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: string;
  }

  interface BaseResult_SubmitTaskResponse_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: SubmitTaskResponse;
  }

  interface BaseResult_SystemConfig_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: SystemConfig;
  }

  interface BaseResult_ToolProductStructDef_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: ToolProductStructDef;
  }

  interface BaseResult_ToolResponse_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: ToolResponse;
  }

  interface BaseResult_Tool_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: Tool;
  }

  interface BaseResult_User_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: User;
  }

  interface BaseResult_YuQueGroupInfoWithoutDoc_ {
    /** 操作结果 默认false */
    success?: boolean;
    /** 操作结果码 */
    resultCode?: string;
    /** 提示信息 */
    resultMsg?: string;
    /** 对象 */
    data?: YuQueGroupInfoWithoutDoc;
  }

  interface BasicInfo {
    /** 所属租户 */
    tenant?: string;
    /** tool 名称 */
    name?: string;
    /** tool 描述 */
    description?: string;
    /** tool开放类型，默认 open, 即对外开放 */
    type?: string;
    /** tool 调用类型 */
    toolInvokeType?: string;
    /** 协议 */
    protocol?: string;
    /** tool 的创建类型，对应快速接入 */
    toolCreateType?: ToolCreateTypeEnum;
    /** tool 使用说明书，描述 tool 的使用方法和限制 */
    instruction?: string;
  }

  interface BatchAddPreGroupsRequest {
    /** agent id */
    agentId?: string;
    /** 操作人，后端填写 */
    operator?: string;
    /** 需要添加的预分组信息 */
    pregroups?: Record<string, any>;
  }

  interface BuserviceLoginUser {
    /** 返回基本信息 */
    id?: string;
    channel?: string;
    staffNo?: string;
    workNo?: string;
    nickName?: string;
    tntInstId?: string;
    operatorName?: string;
    authType?: Array<string>;
    tokenCreateTime?: string;
  }

  interface BuserviceUser {
    /** 返回基本信息 */
    id?: string;
    channel?: string;
    staffNo?: string;
    workNo?: string;
    nickName?: string;
    tntInstId?: string;
    operatorName?: string;
    authType?: Array<string>;
    tokenCreateTime?: string;
    /** 用户部门 */
    deptName?: string;
    /** 用户类型 */
    userType?: string;
    /** 用户状态 */
    status?: string;
    /** 真实姓名，可能为空，且不唯一 */
    realName?: string;
    email?: string;
    managerId?: string;
    outUserNo?: string;
    /** 创建记录时间 */
    createTime?: string;
    /** 修改记录时间 */
    modifyTime?: string;
    /** 最近一次成功登陆时间 */
    lastLoginTime?: string;
    /** 创建该记录用户ID */
    createId?: string;
    /** 创建该记录用户名 */
    createName?: string;
    /** 修改该记录ID */
    modifyId?: string;
    /** 修改该记录的用户名 */
    modifyName?: string;
    extProperty?: Record<string, any>;
    mobileNumber?: string;
    userChannel?: string;
  }

  interface CallBackObj {
    /** 用户系统中自己实现的回调接口，回调的 url */
    url?: string;
    /** 请求 header，如果用户的接口需要鉴权，请在提交任务时透传鉴权信息，灵思会使用此处的 headers 调用回调接口 */
    headers?: Record<string, any>;
  }

  type CannedAccessControlList =
    | 'Default'
    | 'Private'
    | 'PublicRead'
    | 'PublicReadWrite';

  interface ChatAsyncResponse {
    /** 返回聊天结果的类型 */
    type?: ComAlipayNexaFrameworkSdkAgentApiResponseEnumsChatTypeEnum;
    /** 大模型对话返回内容
type为text，返回TextContent
type为card，返回CardContent */
    content?: ChatContent;
    /** 对话角色 */
    role?: ChatRoleEnum;
  }

  interface ChatCompletionRequest {
    /** 模型名称 */
    model?: string;
    /** Message上下文 */
    messages?: Array<ChatCompletionRequestMessage>;
    /** Tool列表 */
    tools?: Array<ChatCompletionRequestToolDef>;
    /** 控制哪个（如果有的话）工具被模型调用。有四种模式，默认是null，如果tools不为空，默认是auto

null 不调用任何Tool，直接生成消息
auto 模型选择一个工具，如果决策不使用工具，则生成消息
required 必须使用一个工具，不能直接生成消息
上述三个模式该字段都是String类型，如果指定指定工具，则是Object类型，对应的Json结构如下
{"type": "function", "function": {"name": "my_function"}} */
    toolChoice?: Record<string, any>;
    /** 默认为true，是否允许并发调用Tool */
    parallelToolCalls?: boolean;
    /** 默认为 0.2。要使用的采样温度(temperature)，介于 0 和 2 之间。较高的值（如 0.8）会使输出更随机，而较低的值（如 0.2）则会使其更加专注和确定 */
    temperature?: number;
    /** 默认为 0.9。一种称为“核心采样”的采样替代方法，其中模型考虑概率质量值在前 top_p 的标记的结果。因此，0.1 意味着仅考虑概率质量值前 10% 的标记 */
    topP?: number;
    /** 默认为40。较小的topK值会使生成的文本更准确，较大的topK值则会增加生成文本的多样性 */
    topK?: number;
    /** 默认为1.0。频率惩罚度 */
    repetitionPenalty?: string;
    /** 默认为 null。stop words */
    stop?: Array<string>;
    /** 默认为 false。阻塞式输出，设置true，以流式输出。 */
    stream?: boolean;
    /** 默认为1024。要生成的最大token数。 */
    maxTokens?: number;
    /** 默认为true。当do_sample=true时，生成器方法将使用随机采样的方式生成文本。这意味着在每个时间步，模型将从词汇表中随机选择一个词作为模型的输出。
当do_sample=false时，生成器方法将使用一种称为贪婪采样的方式生成文本。这意味着在每个时间步，模型将选择概率最大的单词作为输出。 */
    doSample?: boolean;
  }

  interface ChatCompletionRequestFunctionDef {
    /** 函数名称 */
    name?: string;
    /** 函数描述 */
    description?: string;
    /** 参数 */
    parameters?: Record<string, any>;
    /** 严格模式，默认false，设为true的时候，模型按照parameters中定义的结构进行生成。 */
    strict?: boolean;
    /** 是否对生成的参数按照parameters指定的结构进行严格校验和纠正 */
    validation?: boolean;
  }

  interface ChatCompletionRequestMessage {
    /** 消息类型 */
    role?: string;
    /** 消息内容 */
    content?: string;
  }

  interface ChatCompletionRequestToolDef {
    /** 类型 */
    type?: string;
    /** 函数定义 */
    function?: ChatCompletionRequestFunctionDef;
  }

  interface ChatCompletionResponse {
    /** chat completion的可选择列表 */
    choices?: Array<ChatCompletionResponseChoice>;
    /** 创建聊天完成的Unix时间戳(秒) */
    created?: number;
    /** 请求的唯一标识符 */
    id?: string;
    /** 推理模型名称，内部对应maya集群 ${sceneName}-${chainName} */
    model?: string;
    /** 对象类型,总是 chat.completion */
    object?: string;
    /** 完成请求的使用统计信息 */
    usage?: ChatCompletionResponseUsage;
  }

  interface ChatCompletionResponseChoice {
    /** ● stop: API 返回完整的模型输出
● length: 因为 max_tokens 参数或 token 限制，导致不完整的模型输出
● content_filter: 因为我们的内容过滤的标记，删掉了内容
● null: API 响应还在进行中或未完成 */
    finishReason?: string;
    /** 整数类型(int)	choices结果选项索引 */
    index?: number;
    /** 推理响应消息 */
    message?: ChatCompletionResponseResponseMsg;
  }

  interface ChatCompletionResponseFunction {
    /** 需要调用的function的名称 */
    name?: string;
    /** 模型生成的，JSON格式的函数调用的参数 */
    arguments?: string;
  }

  interface ChatCompletionResponseResponseMsg {
    /** 字符串类型	推理响应消息内容 */
    content?: string;
    /** 响应消息的角色，assistant */
    role?: string;
    /** 模型生成的工具调用的列表，例如函数调用 */
    toolCalls?: Array<ChatCompletionResponseToolCall>;
  }

  interface ChatCompletionResponseToolCall {
    /** 工具调用的ID */
    id?: string;
    /** Tool的类型，目前只支持function */
    type?: string;
    /** 模型决定调用的函数 */
    function?: ChatCompletionResponseFunction;
  }

  interface ChatCompletionResponseUsage {
    /** 完成请求的token数 */
    completionTokens?: number;
    /** 提示中的token数 */
    promptTokens?: number;
    /** 总共的token数 */
    totalTokens?: number;
  }

  type ChatContent = Record<string, any>;

  interface ChatRequest {
    /** agentId（必填） */
    agentId?: string;
    /** 域账号（必填） */
    domainAccount?: string;
    /** 最后一次提问内容（必填） */
    lastQuestionContent?: string;
    /** 扩展信息（必填）
已知Aitor的apiKey */
    extendContext?: Record<string, any>;
    /** sessionId，用于用户通过openapi查询portal这边的历史对话记录
与historyChatContentList互斥，只能存在一个 */
    sessionId?: string;
    /** 历史对话，用于直接传历史对话（lastQuestionContent也需要加上）
与sessionId互斥，只能存在一个 */
    historyChatContents?: Array<ChatAsyncResponse>;
    /** 对话类型 */
    chatRequestTypeEnum?: ChatRequestTypeEnum;
    /** 最后一次提问返回的唯一id，用于中断恢复等场景 */
    lastChatUniqueId?: string;
  }

  type ChatRequestTypeEnum = 'NORMAL_CHAT' | 'INTERRUPT_RECOVERY';

  type ChatRoleEnum = 'system' | 'bot' | 'user';

  type ChatTypeEnum = 'text';

  interface Choice {
    /** ● stop: API 返回完整的模型输出
● length: 因为 max_tokens 参数或 token 限制，导致不完整的模型输出
● content_filter: 因为我们的内容过滤的标记，删掉了内容
● null: API 响应还在进行中或未完成 */
    finishReason?: string;
    /** 整数类型(int)	choices结果选项索引 */
    index?: number;
    /** 推理响应消息 */
    message?: ChatCompletionResponseResponseMsg;
  }

  interface CodeSimpleRequest {
    /** 用户意图 */
    intention?: string;
  }

  interface CodeSimpleResult {
    /** 最后一次成功的代码 */
    code?: string;
    /** 代码执行结果 */
    exeResult?: string;
  }

  type ComAlipayNexaFrameworkSdkAgentApiResponseEnumsChatTypeEnum =
    | 'text'
    | 'card'
    | 'json';

  interface ComAlipayOpsconvobusModelAgentAgentFullInfo {
    /** 主键 */
    id?: number;
    /** agent唯一主键 */
    agentId?: string;
    /** agent类型，私有，公共，官方 */
    agentType?: string;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** agent名称 */
    name?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 修改者 */
    operatorModified?: string;
    /** 是否已删除(0表示未删除) */
    deleted?: boolean;
    /** 头像 */
    avatar?: string;
    /** 开场白 */
    prologue?: string;
    /** 提问示例 */
    questionSample?: Array<string>;
    /** 选择Tool的分数阈值 */
    toolSelectScore?: string;
    /** Tool进行总结时的Summary Prompt模板 */
    toolSummaryPromptTmpl?: string;
    /** 用户列表
key: domainName, value: role */
    userRoleMap?: Record<string, any>;
    /** Tool列表 */
    toolBriefInfoList?: Array<ToolBriefInfo>;
    /** 知识库Tool */
    knowledgeBaseTool?: string;
    /** 高级配置 */
    advancedConfig?: AgentAdvancedConfig;
    /** 内部配置，用来存储一些不需要展示给用户的自动生成的配置@see AgentInnerConfig */
    innerConfig?: AgentInnerConfig;
    /** 正在编辑Debug的版本号 */
    debugVersion?: number;
    /** 线上版本号 */
    onlineVersion?: number;
    /** 状态 */
    status?: string;
  }

  type ComAlipayOpsgptModelOpenapiAlipayChatContent = Record<string, any>;

  interface ComAlipayOpsgptModelPojoOpenapiV1Parameter {
    /** 参数名 */
    name?: string;
    /** 参数值 */
    value?: string;
    /** 必填 本节点的类型: string，object，array，number，integer，boolean */
    type?: string;
    /** 描述信息 */
    desc?: string;
    /** 是否必填 */
    required?: boolean;
    /** type = object 时，描述 object 的属性 */
    objectField?: Array<ComAlipayOpsgptModelPojoOpenapiV1Parameter>;
    /** type = array 时，描述 array 列表元素 */
    arrayField?: ComAlipayOpsgptModelPojoOpenapiV1Parameter;
  }

  interface ComAlipayOpsgptModelPojoOpenapiV1Tool {
    /** tool 名称 */
    name?: string;
    /** tool 描述 */
    desc?: string;
    /** tool 元数据 */
    meta?: Meta;
    /** tool 出入参结构定义 */
    schema?: Schema;
  }

  interface ComAlipayOpsgptWebUser {
    /** getName */
    name?: string;
    /** getAge */
    age?: number;
  }

  interface ConFileRenameRequest {
    /** 会话id */
    conversationId?: string;
    /** 文件url */
    fileUrl?: string;
    /** 文件新名称 */
    newName?: string;
    /** 修改人 */
    operatorModified?: string;
  }

  type ConFileTypeEnum = 'DATASOURCE' | 'ATTACHMENT';

  interface ConvoDataSourceRequest {
    /** 关联的会话ID(可为空) */
    conversationId?: string;
    /** 文件url list */
    fileUrlList?: Array<string>;
    /** 创建者 */
    operatorCreate?: string;
    /** 修改者 */
    operatorModified?: string;
    /** 文件来源类型,上传还是附件生成 */
    fileSourceType?: string;
    /** 文件属于数据源还是普通附件 */
    fileType?: string;
  }

  interface ConvoRFile {
    /** 主键 */
    id?: number;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** conversationId */
    conversationId?: string;
    /** 文件路径 */
    fileUrl?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 修改者 */
    operatorModified?: string;
    /** 重命名后的文件名称@See ConFileSourceType */
    fileName?: string;
    /** 文件属于数据源还是普通附件 */
    fileType?: ConFileTypeEnum;
    fileSourceType?: FileSourceTypeEnum;
    /** 是否已删除(0表示未删除) */
    deleted?: boolean;
  }

  interface CreateAgentBaseRequest {
    /** 头像，Base64编码 */
    avatar?: string;
    /** agent名称 */
    name?: string;
    /** agent描述 */
    agentDesc?: string;
    /** agent 类型，默认 PRIVATE */
    agentType?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 开场白 */
    prologue?: string;
    /** 提问示例 */
    questionSample?: Array<string>;
    /** 选择Tool的分数阈值 */
    toolSelectScore?: string;
  }

  interface CreateAgentRequest {
    /** 头像，Base64编码 */
    avatar?: string;
    /** agent名称 */
    name?: string;
    /** agent描述 */
    agentDesc?: string;
    /** agent 类型，默认 PRIVATE */
    agentType?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 开场白 */
    prologue?: string;
    /** 提问示例 */
    questionSample?: Array<string>;
    /** 选择Tool的分数阈值 */
    toolSelectScore?: string;
    /** 修改者 */
    operatorModified?: string;
    /** Tool进行总结时的Summary Prompt模板 */
    toolSummaryPromptTmpl?: string;
    /** Tool列表 key: toolId, value: toolKey */
    toolMap?: Record<string, any>;
    /** 用户列表， key: 域账号, value: 角色 */
    userRoleMap?: Record<string, any>;
    /** 知识库Tool */
    knowledgeBaseTool?: string;
    /** 高级配置 */
    advancedConfig?: AgentAdvancedConfig;
    /** 内部配置 */
    innerConfig?: AgentInnerConfig;
  }

  interface CreateAgentSimplifyRequest {
    /** 头像，Base64编码 */
    avatar?: string;
    /** agent名称 */
    name?: string;
    /** agent描述 */
    agentDesc?: string;
    /** agent 类型，默认 PRIVATE */
    agentType?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 开场白 */
    prologue?: string;
    /** 提问示例 */
    questionSample?: Array<string>;
    /** 选择Tool的分数阈值 */
    toolSelectScore?: string;
    /** dima workSpace */
    dimaWrokSpace?: string;
    /** yuque 用户选择知识库与授权信息 */
    yuque?: YuqueSelectInfo;
  }

  type DataWithMediaType = Record<string, any>;

  type DefaultCallback = Record<string, any>;

  interface Definition {
    /** toolId */
    toolId?: string;
    /** 入参描述 */
    inputs?: Array<ComAlipayOpsgptModelPojoOpenapiV1Parameter>;
    /** 出参描述 */
    outputs?: Array<ComAlipayOpsgptModelPojoOpenapiV1Parameter>;
  }

  interface DeleteYuQueTokenRequest {
    /** agentId */
    agentId?: string;
    /** groupLogin */
    groupLogin?: string;
  }

  interface DeleteYuqueDocRequest {
    /** agentId */
    agentId?: string;
    /** 英文大写，删除哪个维度的数据: * BOOK - 删除整个知识库 * DOC - 删除单篇文档 */
    deleteType?: string;
    /** group login 必填，待删除数据所属的语雀groupLogin */
    groupLogin?: string;
    /** book slug 必填，待删除数据所属的语雀bookSlug */
    bookSlug?: string;
    /** doc slug deleteType = DOC时必填 */
    docSlug?: string;
  }

  type DingTalkChannel = 'OPSGPT' | 'ANTEMC' | 'NEXA';

  type EditableOutputTypeEnum = 'TEXT' | 'CODE' | 'SQL';

  interface EditableParam {
    /** 结果项参数的类型，决定如何进行字段渲染 */
    outputType?: EditableOutputTypeEnum;
    /** 结果的展示名称 */
    title?: string;
    /** 结果的别名，如果该参数 retryRequired = true
则需要在重新提交任务的时候，将 alias 作为 key，content 作为 value 拼成入参提交到后端 */
    alias?: string;
    /** editable	String	是否可编辑，
如果可编辑，则要将 content 渲染到编辑框，
如果用户进行了编辑，则需要在重新提交任务的时候，将用户新编辑的内容替换为 content 的内容作为 alias 的 value 再提交。 */
    editable?: boolean;
    /** 该结果是否默认隐藏 */
    hide?: boolean;
    /** 重新提交任务的时候，该值是否需要作为新任务的参数进行提交 */
    retryRequired?: boolean;
    /** conte */
    content?: string;
  }

  interface EditableResponse {
    /** 非必填，按钮名称，默认值为「重试」 */
    button?: string;
    /** parm 参数是否隐藏，有交互需求可以设置为「false」
非必填，默认值为「true」 */
    parmasHide?: boolean;
    /** 非必填，params 对外展示的名字，默认 「思考过程」 */
    paramsName?: string;
    /** 参数项，参数项需要进行指定方式的渲染，同时要指定该项是否可编辑，重试提交任务时是否需要 */
    params?: Array<EditableParam>;
    /** 非必填，执行结果的对外展示名字，默认 「查询结果」 */
    resultsName?: string;
    /** 结果项，用于 tool 静态结果的展示 */
    results?: Array<Result>;
    /** 用户点击确认后，具体执行的 tool 信息和策略 */
    nextTool?: NextTool;
  }

  type EditableResultOutputTypeEnum = 'MARKDOWN' | 'MARKDOWN_TABLE' | 'TEXT';

  interface EkgEdgeVo {
    startNodeId?: string;
    endNodeId?: string;
  }

  interface EkgGraphInfoVo {
    /** 节点map<nodeId,> */
    nodes?: Record<string, any>;
    /** 边map<edgeId,> */
    edges?: Record<string, any>;
    /** 内部上下文信息透传 */
    innerExtra?: Record<string, any>;
  }

  interface EkgGraphRequest {
    /** 对应总线的taskSource */
    scene?: string;
    sessionId?: string;
  }

  type EkgNodeType =
    | 'opsgptkg_intent'
    | 'Intent'
    | 'opsgptkg_schedule'
    | 'Schedule'
    | 'opsgptkg_task'
    | 'Task'
    | 'opsgptkg_analysis'
    | 'Analysis'
    | 'opsgptkg_phenomenon'
    | 'Phenomenon';

  interface EkgNodeVo {
    name?: string;
    description?: string;
    toolResponse?: Record<string, any>;
    toolParam?: string;
    startTime?: string;
    /** 耗时,ms */
    costMs?: number;
    stepId?: string;
    nodeType?: string;
    /** List<StepStageContext>
实际在opsgpt组装 */
    stepExeContext?: Array<Record<string, any>>;
    status?: EkgNodeVoStatusEnum;
  }

  type EkgNodeVoStatusEnum =
    | 'WAIT_EXECUTE'
    | 'EXECUTING'
    | 'EXECUTED_SUCCESS'
    | 'EXECUTED_FAIL';

  interface EkgSceneSessionRequest {
    /** 对应总线的taskSource */
    scene?: string;
    sessionId?: string;
  }

  type EmcUserDataType =
    | 'antmonitor'
    | 'ANTMONITOR'
    | 'antemc'
    | 'ANTEMC'
    | 'alter'
    | 'ALTER'
    | 'antlogs'
    | 'ANTLOGS'
    | 'odc'
    | 'ODC'
    | 'antshell'
    | 'ANTSHELL'
    | 'yuntu'
    | 'YUNTU'
    | 'origin'
    | 'ORIGIN';

  interface EmcUserFeedbackRequest {
    /** 反馈类型 */
    type?: string;
    /** SRE语雀文档gen id */
    docGenId?: string;
    /** 应急事件id */
    emergencyId?: string;
    /** 应急路径全部内容 */
    emcContent?: string;
    /** 反馈项列表 */
    items?: Array<EmcUserProxyEventItem>;
  }

  interface EmcUserProxyEventItem {
    /** 数据MD5 */
    dataMd5?: string;
    /** 数据类型 */
    dataType?: EmcUserDataType;
    /** 操作时间 */
    operateTime?: string;
    /** 操作人 */
    operator?: string;
    /** 操作平台 */
    platform?: string;
    /** 是否关单人 */
    isCloseName?: boolean;
    /** 标题 */
    title?: string;
    /** 变更应用 */
    alterApp?: string;
    /** 操作url */
    url?: string;
    /** 操作路径描述 */
    content?: string;
  }

  interface EndSessionRequest {
    /** agentId（必填） */
    agentId?: string;
    /** 域账号（必填） */
    domainAccount?: string;
    /** 扩展信息（必填）
已知Aitor的apiKey */
    extendContext?: Record<string, any>;
  }

  type ErrorCallback = Record<string, any>;

  interface ExcelData {
    /** 多个sheet的数据 */
    sheetDatas?: Array<SheetData>;
  }

  interface ExcelDataRequest {
    /** 文件url */
    fileUrl?: string;
    /** 当前sheet名称 */
    curSheetName?: string;
    pageSize?: number;
    curPageNum?: number;
    conversationId?: string;
  }

  interface ExecuteToolRequest {
    toolId?: string;
    params?: Record<string, any>;
  }

  interface FeedBack {
    /** 主键 */
    id?: number;
    /** 创建时间 */
    gmtCreate?: string;
    /** 更新时间 */
    gmtModified?: string;
    /** 消息id */
    msgId?: string;
    /** 打标类型 */
    type?: MsgSubmitTypeEnum;
    /** 打标结果 */
    mark?: FeedBackMarkEnum;
    /** 反馈详情 */
    detail?: string;
    /** 反馈人 */
    operator?: string;
  }

  type FeedBackMarkEnum =
    | 'POSITIVE'
    | 'NEGATIVE'
    | 'BETTER'
    | 'WORSE'
    | 'SAME'
    | 'CONFIRM';

  interface FieldNode {
    /** 必填，用于描述该属性的唯一键，用于区分所有层级属性的唯一键，建议使用所有父节点的属性名串联保证唯一性 { "a": { "b": "c", "d": "e" } } 如，属性 b 的 id
建议设置为 a.b，属性 d 的 id 建议设置为 a.d 属性的 id，与 GPTManualApiMeta.protocols.http.parameters.schema.$ref
保持一致 二者相互关联，从 id 可以找到对应属性在 protocol 中的关联属性，最重要的属性是这个属性节点的实际的参数类型 path,query,body */
    id?: string;
    /** 必填 节点赋值类型，指明该节点是通过哪种方式赋值的，用户指定的默认值/算法提取注入值获/其他的赋值方式 */
    fieldTypeEnum?: FieldTypeEnum;
    /** 必填，重要 参数的名称，即为请求参数的名称 */
    title?: string;
    /** 必填，重要 属性的描述信息，描述该属性的作用，描述该属性的拼装规则 例如 ： 一般来说简单描述信息就够了 appName : 应用名称，例如：帮我查询一下应用xxx 的基本信息 env :
环境，例如：xxx 应用在 xxx 环境有几台机器 project : 仓库，例如：xxx 仓库有哪些成员 如果发现该字段本身非常特殊，算法翻译该字段的表现不好，可以增加描述信息
prizeIds : 奖品id列表，用英文逗号分隔(PZ12344,PZ37898764),例如：帮我部署一个奖品PZ12344和PZ37898764的互斥布放策略 apps :
app列表，帮我拼装成一个list(["opsgpt","paycore"]), 例如：帮我查询一下 opsgpt 和 paycore 最近的 error 数量 */
    description?: string;
    /** 非必填 枚举信息，key 为中文，value 为英文 给一些枚举 sample，帮助算法理解如何将中文转换为英文 有一些枚举可以给一部分，算法即可帮助翻译 比如说，问题中需要翻译
月日年一类的参数，可以直接提问，如果返现翻译效果不好，可以提供部分帮助算法理解问题并翻译 { "周": "WEEK", "月": "MONTH", "年": "YEAR" }
当然如涉及到专业性或者和系统特有的一些枚举时，必须要要完全给出答案算法的才能完成参数翻译的工作 { "主站": "主站", "蚂蚁集团": "ANTGW4CN", "蚂蚁支付宝":
"AZFBW3CN", "支付宝": "MZFBW3CN", "支付宝科技": "ZFBTW4CN", "国际": "USA" } */
    enums?: Record<string, any>;
    /** 必填 本节点的类型: string，object，array，number，integer，boolean */
    type?: string;
    /** 非必填，仅 object 存在子属性时需要设置 object 对象的子属性，key 为属性名称，value 为递归的 FieldNode 对象 */
    properties?: Record<string, any>;
    /** 分必填，仅 array 类型的属性需要对子属性进行描述 array 类型的元素属性，属性用 FieldNode 对象描述 */
    items?: FieldNode;
    /** 非必填 该属性是否为必选值，填充为必选值则去当问题中没有改属性描述时，算法会尝试给出一个猜测值 */
    required?: boolean;
    /** 非必填 用户设置的默认值，用户设置了该值则在请求时会直接使用配置的默认值对属性进行赋值 */
    defaultValue?: Record<string, any>;
    /** 必填 该节点是否被用户选择，只有该值为 true，才会在构造请求参数的时候使用该参数，否则不会使用该参数 */
    selected?: boolean;
    /** 非必填 该节点是否允许算法填充，为 true 时用户可以选择 list object 和没有子属性的 object 叶子节点算法填充效果差，不允许用户选择
FieldTypeEnum.INJECT_VALUE */
    allowToInject?: boolean;
    /** 非必填 本节点是否被从 oneapi 接口元数据中删除 */
    deletedFromOneApi?: boolean;
  }

  type FieldTypeEnum = 'DEFAULT_VALUE' | 'INJECT_VALUE';

  type FileSourceTypeEnum =
    | 'OPSGPT_ATTACHMENT'
    | 'OPSGPT_UPLOAD'
    | 'OPSGPT_OPEN_URL';

  interface GEdge {
    /** 起点节点ID */
    startId?: string;
    /** 终点节点ID */
    endId?: string;
    /** 属性 */
    attributes?: Record<string, any>;
  }

  interface GGraph {
    /** 路径上的节点 */
    nodes?: Array<GNode>;
    /** 路径上的边 */
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

  interface GPTManualApiMeta {
    /** 必填 请求参数，由 FieldNode 来描述参数的结构 */
    requests?: Array<FieldNode>;
    /** 非必填 返回参数，由 FieldNode 来描述参数的结构 */
    response?: FieldNode;
    /** 必填 http 请求协议信息，用来描述请求入参的参数位置 该参数的逻辑根据不同的 ApiMeta.createType 取值而不同 ApiMeta.createType =
GPT_ONE_API，one api 接口可以直接拿到 ApiMeta.createType = GPT_MANUAL，前端根据用户的输入生成 */
    protocols?: Protocols;
    /** 非必填 request 发送请求自定义脚本 */
    reqCusScripts?: BaseGroovyScripts;
    /** 非必填 response 响应结果自定义解析脚本 */
    respCusScripts?: BaseGroovyScripts;
    /** model 定义 */
    definitions?: Record<string, any>;
    /** 接口信息 */
    apis?: Record<string, any>;
  }

  interface GPTOneApiApiMeta {
    /** 必填 请求参数，由 FieldNode 来描述参数的结构 */
    requests?: Array<FieldNode>;
    /** 非必填 返回参数，由 FieldNode 来描述参数的结构 */
    response?: FieldNode;
    /** 必填 http 请求协议信息，用来描述请求入参的参数位置 该参数的逻辑根据不同的 ApiMeta.createType 取值而不同 ApiMeta.createType =
GPT_ONE_API，one api 接口可以直接拿到 ApiMeta.createType = GPT_MANUAL，前端根据用户的输入生成 */
    protocols?: Protocols;
    /** 非必填 request 发送请求自定义脚本 */
    reqCusScripts?: BaseGroovyScripts;
    /** 非必填 response 响应结果自定义解析脚本 */
    respCusScripts?: BaseGroovyScripts;
    /** model 定义 */
    definitions?: Record<string, any>;
    /** 接口信息 */
    apis?: Record<string, any>;
    /** one api 接口的 hash，用于判断接口是否发生了变化 TODO */
    oneApiHash?: string;
    /** 接口在 one api 上的 url */
    url?: string;
    /** 方法的描述信息 */
    methodDesc?: string;
    /** 接口方法 */
    interfaceMethod?: string;
    /** 是否去除路径后缀 有的系统在路径最后定义了 .json, .html 等后缀定义 在较新版本的 spring boot 中默认禁止了后置模式匹配 如果存在系统无法更改的情况下，将该值设为
true，手动帮用户去做后缀去除 */
    removePathSuffix?: boolean;
  }

  interface GenerateAgentPromptRequest {
    /** dima workSpace */
    dimaWrokSpace?: string;
    /** yuque 用户选择知识库与授权信息 */
    yuque?: YuqueSelectInfo;
    /** 关键提示词，生成提问模板时需要传该字段 */
    keyPrompt?: string;
  }

  interface GenerateInfoByPromptRequest {
    /** 关键提示词，文档目录或者需求目录 */
    keyPrompt?: string;
  }

  interface GraphImportByYuqueRequest {
    /** 团队ID */
    teamId?: string;
    /** 导入哪个意图节点ID下 */
    intentNodeId?: string;
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

  interface GroovyScripts {
    /** 自定义import 信息 */
    importsScript?: string;
    /** 自定义预处理脚本 */
    preScript?: string;
    /** 自定义后处理脚本 */
    postScript?: string;
    /** 最终自动生成的脚本 */
    finalGroovy?: string;
  }

  type Handler = Record<string, any>;

  type HttpServletRequest = Record<string, any>;

  type HttpServletResponse = Record<string, any>;

  type InteractiveModeEnum = 'STREAM' | 'BATCH';

  interface IspInfo {
    /** 接口对应的请求类全类名 */
    className?: string;
  }

  type JSONArray = Record<string, any>;

  interface KnowledgeBase {
    /** 创建渠道来源 OPSGPT/AITOR */
    createSource?: PortalChannelEnum;
    /** 知识库ID */
    knowledgeBaseId?: string;
  }

  interface KnowledgeBaseCreateRequest {
    /** 空间ID */
    spaceId?: string;
    /** 创建人域账号 */
    operatorCreate?: string;
    /** 知识库名 */
    name?: string;
    /** 知识库描述 */
    description?: string;
    /** 知识库类型 */
    type?: string;
  }

  interface KnowledgeBaseCreateResponse {
    /** 知识库ID */
    knowledgeBaseId?: string;
  }

  interface KnowledgeBaseDeleteRequest {
    /** space id */
    spaceId?: string;
    /** 知识库类型 */
    type?: string;
    /** 知识库ID */
    knowledgeBaseId?: string;
  }

  interface KnowledgeInfo {
    /** 问题内容 */
    qContent?: string;
    /** 问题答案 */
    aContent?: string;
    /** 得分范围[0,1] */
    score?: number;
    /** 知识库id */
    knowledgeBaseId?: string;
    /** 文档id */
    fileId?: string;
    /** 文档title */
    fileName?: string;
    /** 知识id */
    knowledgeId?: string;
    /** 知识创建时间 */
    createTime?: string;
    /** 知识修改时间 */
    modifiedTime?: string;
    /** 文件来源类型(user_upload,oss_file,yuque_file,web_page) */
    sourceType?: string;
    /** 语雀文档链接 */
    yuqueDocLink?: string;
  }

  interface KnowledgeSearchRequest {
    /** 知识库id列表 */
    knowledgeBaseIdList?: Array<string>;
    /** 召回数量 */
    recallQuantity?: number;
    /** 文档召回相关性（0-1） */
    documentRecallDependencies?: number;
    /** 单个知识库返回结果数 */
    singleKnowledgeBaseReturnNum?: number;
    /** 是否重排 */
    rerankFlag?: boolean;
    /** 搜索优化 */
    searchOptimizationFlag?: boolean;
    /** 查询内容 */
    queryContent?: string;
    /** 域账号 */
    domainAccount?: string;
    /** 召回结果再剔除一部分开关，true打开 */
    rejectorFlag?: boolean;
    /** 必须包含的关键词列表 */
    forceKeyWorkList?: Array<string>;
    /** 格式化输出的表达式 */
    formatExpr?: string;
    /** 外部平台名称 */
    platformName?: string;
  }

  interface LLMToolScenarioParam {
    /** tool 的描述信息 */
    description?: string;
    /** 场景的名称 */
    name?: string;
    /** 提示词 */
    prompt?: string;
  }

  interface ListAgentRequest {
    /** 分页数 */
    pageNum?: number;
    /** 每页大小 */
    pageSize?: number;
    /** 起始位置 */
    startIndex?: number;
    /** agentId */
    agentId?: string;
    /** agentId列表 */
    agentIds?: Array<string>;
    /** agent名称 */
    agentName?: string;
    /** 模糊查询agent名称 */
    fuzzyName?: string;
    /** 创建者 */
    operatorCreate?: string;
    /** 用户域账号 */
    user?: string;
    /** 操作者域账号 */
    operator?: string;
  }

  interface ListSessionPageRequest {
    /** 查询条件 */
    condition?: ListSessionRequest;
    /** 页面大小 */
    pageSize?: number;
    /** 页数 */
    pageNo?: number;
  }

  interface ListSessionRequest {
    /** 会话 id */
    sessionId?: string;
    /** 会话人 */
    operator?: string;
    /** agentId */
    agentId?: string;
    /** 当前的交互 id */
    currentConversationId?: string;
  }

  interface ListToolFuzzyRequest {
    /** 分页数 */
    pageNum?: number;
    /** 每页大小 */
    pageSize?: number;
    /** 起始位置 */
    startIndex?: number;
    /** tool的全局唯一key */
    toolKey?: string;
    /** tool的全局唯一ID */
    toolId?: string;
    /** tool的类型 */
    type?: string;
    /** tool的状态 */
    status?: string;
    /** 模糊查询的toolKey */
    fuzzyToolKey?: string;
    /** 模糊查询配置名称 */
    fuzzyToolName?: string;
    /** 模糊查询 key，模糊查询 toolKey 或者 toolName */
    fuzzyKey?: string;
    /** 负责人 */
    owner?: string;
    /** 协议 */
    toolProtocol?: string;
    /** 状态列表 */
    statusList?: Array<string>;
    /** ToolId列表 */
    toolIdList?: Array<string>;
    /** toolKey 列表 */
    toolKeyList?: Array<string>;
    /** 租户 */
    tenant?: string;
    /** 方法模糊查询 */
    fuzzyMethod?: string;
    /** 模糊产品 */
    fuzzyProduct?: string;
    /** 是否查询我创建的 */
    owned?: boolean;
  }

  interface ListToolPageRequest {
    /** 页码 */
    pageNum?: number;
    /** 页的大小 */
    pageSize?: number;
    /** tool 负责人 */
    owner?: string;
    /** tool 名称 */
    name?: string;
    /** toolId */
    toolId?: string;
  }

  interface ListToolRequest {
    /** 分页数 */
    pageNum?: number;
    /** 每页大小 */
    pageSize?: number;
    /** 起始位置 */
    startIndex?: number;
    /** tool的全局唯一key */
    toolKey?: string;
    /** tool的全局唯一ID */
    toolId?: string;
    /** tool的类型 */
    type?: string;
    /** tool的状态 */
    status?: string;
    /** 模糊查询的toolKey */
    fuzzyToolKey?: string;
    /** 模糊查询配置名称 */
    fuzzyToolName?: string;
    /** 模糊查询 key，模糊查询 toolKey 或者 toolName */
    fuzzyKey?: string;
    /** 负责人 */
    owner?: string;
    /** 协议 */
    toolProtocol?: string;
    /** 状态列表 */
    statusList?: Array<string>;
    /** ToolId列表 */
    toolIdList?: Array<string>;
    /** toolKey 列表 */
    toolKeyList?: Array<string>;
  }

  type List_Object_ = any;

  type List_StudentDO_ = StudentDO[];

  interface LoginAccountsRequest {
    /** Gets get login accounts. */
    loginAccounts?: Array<string>;
  }

  type Map_String_Boolean_ = Record<string, any>;

  type Map_String_String_ = Record<string, any>;

  interface MasterDataDepartment {
    /** 部门名称 */
    deptName?: string;
    /** 部门编号 */
    deptNo?: string;
  }

  interface MasterDataUser {
    /** 花名 */
    nickName?: string;
    /** 工号 */
    staffNo?: string;
    /** 域账号 */
    loginAccount?: string;
    /** 真名 */
    name?: string;
  }

  interface Message {
    /** 消息类型 */
    role?: string;
    /** 消息内容 */
    content?: string;
  }

  interface MessageContent {
    type?: MessageContentMessageType;
    value?: string;
    index?: number;
  }

  type MessageContentMessageType = 'TEXT' | 'IMAGE_URL' | 'IMAGE_FILE';

  interface MessageObject {
    role?: MessageObjectRole;
    content?: MessageContent;
    metadata?: Record<string, any>;
    attachments?: Array<MessageObjectAttachment>;
  }

  interface MessageObjectAttachment {
    file_id?: string;
  }

  type MessageObjectRole = 'USER' | 'ASSISTANT';

  type MessageType =
    | 'ActionCard'
    | 'DING_ACTIONCARD'
    | 'Markdown'
    | 'DING_MARKDOWN'
    | 'DingText'
    | 'DING_TEXT'
    | 'EmptyMessage'
    | 'EMPTY_MSG';

  interface Meta {
    /** 类型 */
    type?: string;
    /** 提供方 */
    provider?: string;
  }

  interface Model {
    /** 业务场景描述 */
    desc?: string;
    /** 模型编码 */
    code?: string;
    /** 业务模型一级，允许空 */
    onelevel?: string;
    /** 业务模型一级，允许空 */
    twolevel?: string;
    /** 业务模型一级，允许空 */
    threelevel?: string;
    /** 业务编码 */
    bizCode?: string;
    /** 任务类型：单步骤、多步骤、其他 */
    taskType?: string;
    /** 问题例子 */
    questionSamples?: Array<string>;
    /** 当前节点绑定的 key，tool、chain 或者其他对象的唯一键 */
    bindingKey?: string;
  }

  type ModelMap = Record<string, any>;

  interface ModelNode {
    /** 下游节点 */
    children?: Array<ModelNode>;
    /** 名称 */
    title?: string;
    /** 描述 */
    desc?: string;
    /** key */
    key?: string;
    /** bizcode */
    bizCode?: string;
    /** 提问模板 */
    templates?: Array<string>;
    /** 提问示例 */
    samples?: Array<string>;
    /** 当前节点绑定的 key，tool、chain 或者其他对象的唯一键 */
    bindingKey?: string;
    /** 使用说明 */
    instruction?: string;
  }

  interface MsgRecord {
    /** 主键 */
    id?: number;
    /** 创建时间 */
    gmtCreate?: number;
    /** 更新时间 */
    gmtModified?: number;
    /** 会话id */
    sessionId?: string;
    /** 消息id */
    msgId?: string;
    /** 消息类型 */
    msgType?: MsgTypeEnum;
    /** 交流模型 */
    interactiveMode?: InteractiveModeEnum;
    /** 模型 */
    model?: Model;
    /** 发送者 */
    sender?: string;
    /** 提交模式 */
    submitType?: MsgSubmitTypeEnum;
    /** 发送时间 */
    sendTime?: string;
    /** 回复的消息id */
    replyMsgId?: string;
    /** 消息内容

<p>消息为提问时，内容为 String 消息为回答时，内容参见@see MsgContent */
    content?: string;
    /** 业务类型 */
    bizCode?: string;
    /** 会话id */
    conversationId?: string;
    /** 任务id */
    taskId?: string;
    /** 任务状态 */
    taskStatus?: TaskStatusEnum;
    /** 任务开始时间 */
    taskStartTime?: number;
    /** 任务结束时间 */
    taskEndTime?: number;
    /** 重试需要提供重试的msgID */
    onceMoreMsgId?: string;
    /** 反馈模型 */
    feedBacks?: Array<FeedBack>;
    /** 透传信息 */
    transparentInfo?: Record<string, any>;
    /** 任务最近一次更新时间 */
    taskLastUpdateTime?: number;
    /** 任务来源 */
    taskSource?: string;
    /** 回调系统的endpoint */
    callBackUrl?: string;
    /** 回调使用的header */
    callBackHeader?: Record<string, any>;
    /** 通过Agent产生的消息 */
    agentId?: string;
  }

  interface MsgRecordRequest {
    /** 会话 id，必填 */
    sessionId?: string;
    /** 请求的业务类型，必填 code+ : CODE_INTERPRETER tool : COMMON_SINGLE_TOOL */
    bizType?: string;
    /** 发送的消息，必填 key : intention value : 用户意图

<p>code + 参见文档示例 */
    contents?: Record<string, any>;
    /** 再来一次关联的 msgId，非必填 */
    onceMoreMsgId?: string;
    /** 提交任务类型，用户仅需要关注：NORMAL(普通请求)，ONCE_MORE(再来一次) */
    submitType?: MsgSubmitTypeEnum;
    /** 操作人域账号，必填 */
    operatorName?: string;
    /** 请求关联的 agentId，必填 */
    agentId?: string;
    /** 高阶参数 */
    advancedConfig?: AdvancedConfig;
    /** 回调对象，不希望轮询数据，希望通过回调接口的系统需要配置该值 用户需要实现自己的 回调接口 非必填 */
    callBack?: CallBackObj;
    /** 额外信息 */
    extra?: Record<string, any>;
  }

  type MsgStructTypeEnum =
    | 'SIMPLE_TEXT'
    | 'MULTI_STEPS'
    | 'CUSTOM_STEPS'
    | 'JSON';

  type MsgSubmitTypeEnum =
    | 'NORMAL'
    | 'ONCE_MORE'
    | 'DEBUG'
    | 'DEGBUG'
    | 'DIRECT_EXE_AFTER_MODIFY'
    | 'CLEAR_MEMORY';

  type MsgTypeEnum = 'QUESTION' | 'REPLY' | 'OPERATION';

  type MultipartHttpServletRequest = Record<string, any>;

  interface NexExtraInfo {
    /** 当前 tool 的关键信息 hash，辅助判断 tool 是否发生了改变 */
    hash?: number;
    /** nex 的 toolId */
    toolId?: string;
    /** nex 的 toolType */
    nexToolType?: string;
    /** tool 的来源 */
    nexToolSource?: string;
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

  interface NexaResult_List_AgentDetailInfo__ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: Array<AgentDetailInfo>;
  }

  interface NexaResult_List_AgentFullInfo__ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: Array<AgentFullInfo>;
  }

  interface NexaResult_List_ChatAsyncResponse__ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: Array<ChatAsyncResponse>;
  }

  interface NexaResult_Object_ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: Record<string, any>;
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

  interface NexaResult_ToolProtocolResponse_ {
    /** 是否成功过 */
    success?: boolean;
    /** 接口返回码 */
    resultCode?: string;
    /** 接口信息 */
    msg?: string;
    /** 接口数据 */
    data?: ToolProtocolResponse;
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

  interface NextTool {
    /** 用户点击确认，继续执行的 tool 的 toolKey */
    nextToolKey?: string;
  }

  type OneApiResult_boolean_ = Record<string, any>;

  type OneApiResult_object_ = Record<string, any>;

  type OneApiResult_string_ = Record<string, any>;

  interface OpenToolProductStructDef {
    /** tool 基本信息，对应 tool 接入流程：填写 tool 基本信息 */
    basicInfo?: BasicInfo;
    /** api 定义相关信息，对应 tool 接入流程： api 定义 */
    apiMeta?: ApiMeta_AdvancedApiMeta_;
    /** 构建请求信息，对应 tool 接入流程：构建请求 */
    toolReqDef?: ToolReqDef;
    /** 高级配置信息 */
    advancedInfo?: AdvancedInfo;
    /** 训练样本，对应 tool 接入流程：提供训练样本 */
    trainingSamples?: TrainingSamples;
    /** 开放接口请求参数 */
    openParam?: OpenToolProductStructDefOpenParam;
  }

  interface OpenToolProductStructDefOpenParam {
    /** 操作人 */
    operator?: string;
    /** 需要绑定的 agentId，指定 agentId 会将创建的 tool 自动创建一个场景并绑定到 agent 上 */
    bindAgentId?: string;
  }

  interface OpenToolProductStructDef_AdvancedApiMeta_ {
    /** tool 基本信息，对应 tool 接入流程：填写 tool 基本信息 */
    basicInfo?: BasicInfo;
    /** api 定义相关信息，对应 tool 接入流程： api 定义 */
    apiMeta?: ApiMeta_AdvancedApiMeta_;
    /** 构建请求信息，对应 tool 接入流程：构建请求 */
    toolReqDef?: ToolReqDef;
    /** 高级配置信息 */
    advancedInfo?: AdvancedInfo;
    /** 训练样本，对应 tool 接入流程：提供训练样本 */
    trainingSamples?: TrainingSamples;
    /** 开放接口请求参数 */
    openParam?: OpenToolProductStructDefOpenParam;
  }

  interface OpsgptAlipayResponse {
    code?: string;
    msg?: string;
    subCode?: string;
    subMsg?: string;
    body?: string;
    params?: Record<string, any>;
    /** 模型输出内容 */
    response?: Record<string, any>;
  }

  interface OpsgptAlipayResponse_ResponseMsg_ {
    code?: string;
    msg?: string;
    subCode?: string;
    subMsg?: string;
    body?: string;
    params?: Record<string, any>;
    /** 模型输出内容 */
    response?: ResponseMsg;
  }

  interface OpsgptAlipayResponse_SubmitTaskAsyncResponse_ {
    code?: string;
    msg?: string;
    subCode?: string;
    subMsg?: string;
    body?: string;
    params?: Record<string, any>;
    /** 模型输出内容 */
    response?: SubmitTaskAsyncResponse;
  }

  type OssBusinessEnum =
    | 'TEST'
    | 'OPSGPT_ATTACHMENT'
    | 'OPSGPT_UPLOAD'
    | 'OPSGPT_QA_YUQUE_DOC'
    | 'OPSGPT_QA_YUQUE_SPLIT';

  interface OutGoingMsg {
    /** 目前只支持text */
    msgtype?: string;
    /** 消息文本 */
    text?: OutGoingMsgMsgContext;
    /** 消息文本 */
    content?: OutGoingMsgMsgContent;
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
    atUsers?: Array<OutGoingMsgAtUser>;
    /** 会话钩子 */
    sessionWebhook?: string;
    /** 会话钩子有效期 */
    sessionWebhookExpiredTime?: number;
  }

  interface OutGoingMsgAtUser {
    /** Gets get dingtalk id. */
    dingtalkId?: string;
  }

  interface OutGoingMsgMsgContent {
    /** Getter method for property <tt>downloadCode</tt>. */
    downloadCode?: string;
    /** Getter method for property <tt>recognition</tt>. */
    recognition?: string;
    /** Getter method for property <tt>duration</tt>. */
    duration?: number;
  }

  interface OutGoingMsgMsgContext {
    debug?: boolean;
    /** Gets get content. */
    content?: string;
  }

  interface OutputItem {
    /** 输出类型 com.alipay.opsconvobus.facade.enums.OutputTypeEnum */
    outputType?: string;
    /** 输出的具体内容 */
    content?: string;
    /** 输出调用的tool的唯一标识 */
    toolKey?: string;
    /** tool名称 */
    toolName?: string;
    /** 参数填充的结果 */
    param?: string;
    /** Step Id */
    stepId?: string;
  }

  interface PaginationResult {
    /** 当前页 */
    current?: number;
    /** 数据总量 */
    total?: number;
    /** 结果 */
    result?: Array<Record<string, any>>;
    /** 每页数量 */
    size?: number;
  }

  interface PaginationResult_Agent_ {
    /** 当前页 */
    current?: number;
    /** 数据总量 */
    total?: number;
    /** 结果 */
    result?: Array<Agent>;
    /** 每页数量 */
    size?: number;
  }

  interface PaginationResult_ComAlipayOpsgptModelPojoOpenapiV1Tool_ {
    /** 当前页 */
    current?: number;
    /** 数据总量 */
    total?: number;
    /** 结果 */
    result?: Array<ComAlipayOpsgptModelPojoOpenapiV1Tool>;
    /** 每页数量 */
    size?: number;
  }

  interface PaginationResult_Tool_ {
    /** 当前页 */
    current?: number;
    /** 数据总量 */
    total?: number;
    /** 结果 */
    result?: Array<Tool>;
    /** 每页数量 */
    size?: number;
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

  type PortalChannelEnum = 'OPSGPT' | 'AITOR';

  interface Protocol {
    /** 请求的方法: GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS, TRACE; */
    method?: string;
    /** 请求路径 */
    path?: string;
    /** 请求参数 */
    parameters?: Array<ProtocolParameter>;
    /** responses 的结构暂时忽略 */
    responses?: Record<string, any>;
  }

  interface ProtocolParameter {
    /** 参数位置，body/path/query */
    in?: string;
    /** schema */
    schema?: ProtocolSchema;
  }

  interface ProtocolSchema {
    /** $ref，参数的引用 id，与 FieldNode.id 是同一个值，该值将二者关联起来 即可以通过 FieldNode.id 找到对应的 schema 参数，进而确定这个参数实际的参数位置 */
    $ref?: string;
  }

  interface Protocols {
    /** http */
    http?: Protocol;
    /** tr */
    tr?: Record<string, any>;
  }

  interface PutYuQueGroupLoginRequest {
    /** agentId */
    agentId?: string;
    /** token */
    token?: string;
    /** 语雀团队 */
    groupLogin?: string;
  }

  interface PutYuQueTokenRequest {
    /** agentId */
    agentId?: string;
    /** token */
    token?: string;
  }

  interface QueryApiMetaRequest {
    /** api 对应的 one api url */
    url?: string;
    /** 用户已经配置好的 meta 信息，用于和最新查询的配置进行比较，筛选被删除的配置 */
    oldMeta?: GPTOneApiApiMeta;
  }

  interface QueryTaskRequest {
    /** Gets get task id. */
    task_id?: string;
  }

  type RemoteAgentStatus =
    | 'QUEUED'
    | 'IN_PROGRESS'
    | 'COMPLETED'
    | 'REQUIRES_ACTION'
    | 'FAILED'
    | 'CANCELLED';

  interface ResponseBodyEmitter {
    /** Return the configured timeout value, if any. */
    timeout?: number;
    handler?: ResponseBodyEmitterHandler;
    /** Store send data before handler is initialized. */
    earlySendAttempts?: Array<ResponseBodyEmitterDataWithMediaType>;
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

  type ResponseBodyEmitterDataWithMediaType = Record<string, any>;

  type ResponseBodyEmitterDefaultCallback = Record<string, any>;

  type ResponseBodyEmitterErrorCallback = Record<string, any>;

  type ResponseBodyEmitterHandler = Record<string, any>;

  interface ResponseMsg {
    /** 消息内容类型 */
    type?: ChatTypeEnum;
    /** 消息内容 */
    content?: ComAlipayOpsgptModelOpenapiAlipayChatContent;
  }

  interface ResponseObject {
    success?: boolean;
    error_code?: number;
    error_message?: string;
    data?: Record<string, any>;
  }

  interface ResponseObject_AgentObject_ {
    success?: boolean;
    error_code?: number;
    error_message?: string;
    data?: AgentObject;
  }

  interface ResponseObject_Map_String_Object__ {
    success?: boolean;
    error_code?: number;
    error_message?: string;
    data?: Record<string, any>;
  }

  interface ResponseObject_PaginationResult_ComAlipayOpsgptModelPojoOpenapiV1Tool__ {
    success?: boolean;
    error_code?: number;
    error_message?: string;
    data?: PaginationResult_ComAlipayOpsgptModelPojoOpenapiV1Tool_;
  }

  interface ResponseObject_SessionDeleteResponse_ {
    success?: boolean;
    error_code?: number;
    error_message?: string;
    data?: SessionDeleteResponse;
  }

  interface ResponseObject_SessionObject_ {
    success?: boolean;
    error_code?: number;
    error_message?: string;
    data?: SessionObject;
  }

  interface Result {
    /** content 的展示类型 */
    outputType?: EditableResultOutputTypeEnum;
    /** 具体要展示的内容 */
    content?: string;
  }

  type ResultCodeEnum =
    | '000'
    | 'SUCCESS'
    | '001'
    | 'UNKNOWN_ERROR'
    | '002'
    | 'HTTP_INVOKE_EXCEPTION'
    | '003'
    | 'EXCEPTION'
    | '004'
    | 'TIME_OUT'
    | '100'
    | 'PARAM_IS_NULL'
    | '101'
    | 'PARAM_INVALID'
    | '103'
    | 'OPSCVBS_TOOL_KEY_DUPLICATED'
    | '104'
    | 'SESSION_ERROR'
    | '200'
    | 'SESSION_ID_GENERATE_FAILED'
    | '201'
    | 'GET_LOGGING_USER_FAILED'
    | '202'
    | 'DATA_NOT_FOUND'
    | '203'
    | 'OPSCONVOBUS_API_ERROR'
    | '204'
    | 'OPSCONVOBUS_DATA_ERROR'
    | '205'
    | 'OPSCONVOBUS_API_RESPONSE_DATA_NULL'
    | '206'
    | 'STATUS_NOT_ALLOWED_TO_UPDATE'
    | '207'
    | 'ONE_API_EXCEPTION'
    | '208'
    | 'OSS_EXCEPTION'
    | '209'
    | 'DIMA_API_ERROR'
    | '210'
    | 'AMAX_API_ERROR'
    | '211'
    | 'EXTERNAL_PLATFORM_UNAUTHORIZED'
    | '212'
    | 'UNSUPPORTED_OP'
    | '213'
    | 'DATA_FILTERED';

  type RobotQuestionType = 'CHOICE' | 'ESSAY';

  type ScenarioNodeTypeEnum = 'NODE' | 'LEAF';

  type ScenarioTaskTypeEnum =
    | 'SINGLE_TOOL'
    | 'AGENT'
    | 'OPSGPT_AGENT'
    | 'AITOR_SCRIPT'
    | 'AITOR_PLUGIN'
    | 'AITOR_AGENT';

  type ScenarioTypeEnum = 'GROUP' | 'PRE_GROUP' | 'SCENARIO' | 'PRE_SCENARIO';

  interface Schema {
    /** 版本号 */
    version?: string;
    /** ? */
    schemaUrl?: string;
    /** 结构定义 */
    data?: Definition;
  }

  interface SendGroupMsgByChannelRequest {
    dingChannel?: string;
    openConversationId?: string;
    msgKey?: string;
    msgParam?: string;
  }

  interface ServiceResult {
    /** 处理结果 */
    data?: Record<string, any>;
    /** 是否成功 */
    success?: boolean;
    /** 结果码 */
    resultCode?: ResultCodeEnum;
    /** 错误信息描述 */
    errorMsg?: string;
  }

  interface ServiceResult_EkgGraphInfoVo_ {
    /** 处理结果 */
    data?: EkgGraphInfoVo;
    /** 是否成功 */
    success?: boolean;
    /** 结果码 */
    resultCode?: ResultCodeEnum;
    /** 错误信息描述 */
    errorMsg?: string;
  }

  interface ServiceResult_List_KnowledgeInfo__ {
    /** 处理结果 */
    data?: Array<KnowledgeInfo>;
    /** 是否成功 */
    success?: boolean;
    /** 结果码 */
    resultCode?: ResultCodeEnum;
    /** 错误信息描述 */
    errorMsg?: string;
  }

  interface ServiceResult_String_ {
    /** 处理结果 */
    data?: string;
    /** 是否成功 */
    success?: boolean;
    /** 结果码 */
    resultCode?: ResultCodeEnum;
    /** 错误信息描述 */
    errorMsg?: string;
  }

  interface SessionCreateRequest {
    metadata?: Record<string, any>;
  }

  interface SessionDeleteResponse {
    id?: string;
    deleted?: boolean;
  }

  interface SessionObject {
    id?: string;
    created_at?: number;
    metadata?: Record<string, any>;
  }

  interface SessionRecord {
    /** 主键 */
    id?: number;
    /** 创建时间 */
    gmtCreate?: string;
    /** 更新时间 */
    gmtModified?: string;
    /** 会话id */
    sessionId?: string;
    /** 会话总结 */
    summary?: string;
    /** 操作人,域账号 */
    operator?: string;
    /** 用户选择的模型 */
    model?: Model;
    /** 开始时间 */
    startTime?: string;
    /** 当前最新的总线会话id */
    currentConversationId?: string;
    /** 关联的 agentId */
    agentId?: string;
  }

  interface SheetData {
    /** 本sheet的名字 */
    sheetName?: string;
    /** excel的文件列名,按顺序填写 */
    columnNames?: Array<string>;
    /** 二维数据表格,Excel从第二行开始的内容,列数必须与columnNames对齐 */
    datas?: Array<Array<string>>;
    /** 内容总行数(排除第一行) */
    totalNum?: number;
    /** 一页的行数 */
    pageSize?: number;
    /** 当前第一页(从1开始) */
    curPageNum?: number;
    /** 总共有多少页 */
    totalPageNum?: number;
  }

  interface SseEmitter {
    timeout?: number;
    handler?: ResponseBodyEmitterHandler;
    /** Store send data before handler is initialized. */
    earlySendAttempts?: Array<ResponseBodyEmitterDataWithMediaType>;
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

  interface StudentDO {
    id?: number;
    number?: string;
    name?: string;
    score?: string;
    delStatus?: number;
    gmtCreate?: string;
    gmtModified?: string;
  }

  interface SubmitTaskAsyncResponse {
    task_id?: string;
  }

  interface SubmitTaskResponse {
    /** 会话ID，用于标识多组对话，一个conversion包含多个task */
    conversionId?: string;
    /** 任务的唯一标识 */
    taskId?: string;
    /** 任务的全量输出，tool 的返回结果在本字段展示 */
    fullOutput?: Array<OutputItem>;
    /** 增量的输出，对于planner任务，返回每一步的结果 */
    incrementalOutput?: string;
    /** 任务的状态 */
    taskStatus?: string;
    /** 任务透传参数, 提交任务/查询结果/回调时透传 */
    transparentInfo?: string;
    /** 总线任务关联的外部任务的ID */
    refId?: string;
    /** 当前Step的输出 */
    currentStepOutput?: OutputItem;
  }

  interface SystemConfig {
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** 配置名称 */
    name?: string;
    /** 配置值 */
    value?: string;
    /** 配置描述 */
    cfgDesc?: string;
    /** 是否对value进行编码 */
    encode?: boolean;
  }

  interface TaskRequestObject {
    agent_id?: string;
    messages?: Array<MessageObject>;
    session?: SessionCreateRequest;
    metadata?: Record<string, any>;
    cancel?: boolean;
  }

  type TaskStatusEnum =
    | 'SUBMITTED'
    | 'TIMEOUT'
    | 'FAILED'
    | 'PLANNER'
    | 'SELECT'
    | 'PARAM_FILL'
    | 'EXECUTING'
    | 'SUMMARY'
    | 'FINISHED'
    | 'STOP'
    | 'PLANNER_FINISH'
    | 'SELECT_FINISH'
    | 'PARAM_FILL_FINISH'
    | 'EXECUTING_FINISH'
    | 'EXECUTE_FINISH'
    | 'SUMMARY_FINISH'
    | 'CLOSE'
    | 'PLANNER_FAILED'
    | 'SELECT_FAILED'
    | 'PARAM_FILL_FAILED'
    | 'EXECUTING_FAILED'
    | 'EXECUTE_FAILED'
    | 'SUMMARY_FAILED'
    | 'INFOSEC_QUESTION'
    | 'INFOSEC_ANSWER'
    | 'EXECUTING_SUSPEND';

  type TaskTypeEnum = 'SINGLE_TOOL';

  type Throwable = Record<string, any>;

  interface Tool {
    /** 自增ID */
    id?: number;
    /** 创建时间 */
    gmtCreate?: string;
    /** 修改时间 */
    gmtModified?: string;
    /** tool类型标识，用于区分不同类型的task */
    toolKey?: string;
    /** tool的定义 */
    toolDefinition?: string;
    /** tool的唯一ID */
    toolId?: string;
    /** tool的描述 */
    description?: string;
    /** tool的名称 */
    toolName?: string;
    /** 控制 tool 的暂停阶段，在配置中的阶段都是执行暂停的逻辑，用户选择 */
    pauseStatus?: string;
    /** 任务透传参数, 提交任务/查询结果/回调时透传 */
    transparentInfo?: string;
    /** 当前步骤意图 */
    intention?: string;
    /** 输入 */
    input?: string;
    /** 输出 */
    output?: string;
    /** tool是否执行正常 */
    exeNormal?: boolean;
    /** Tool执行的额外信息 */
    message?: string;
    /** 用于做request转化的Groovy脚本代码 */
    requestGroovy?: string;
    /** 用于做response转化的Groovy脚本低吗 */
    responseGroovy?: string;
    /** 用于做response转化的Groovy脚本代码 */
    summaryGroovy?: string;
    /** 描述Tool背后的API或者大模型调用的元数据 */
    manifestSchema?: string;
    /** Tool对应的api的定义路径，通过该路径能找到2.2中API详细定义的具体API，格式为 */
    toolApiPath?: string;
    /** Tool使用API的协议类型，SOFA_RPC、HTTP、MAYA、LOCAL */
    toolProtocol?: string;
    /** 请求的地址 */
    serverUrl?: string;
    /** API的schema, Swagger的json格式 */
    apiSchema?: string;
    /** 创建人 */
    operatorCreate?: string;
    /** 修改人 */
    operatorModified?: string;
    /** Tool的版本 */
    version?: string;
    /** Tool的owner */
    owner?: string;
    /** 是否删除 */
    deleted?: boolean;
    /** Tool类型@see com.alipay.opsconvobus.model.enums.ToolTypeEnum */
    type?: string;
    /** Tool状态@see com.alipay.opsconvobus.model.enums.ToolStatusEnum */
    status?: string;
    /** Tool对应的向量数据库的主键 */
    vdbPk?: string;
    /** select触发指令训练样本 */
    selectSamples?: string;
    /** select触发指令宏变量样本 */
    selectVars?: string;
    /** 调用类型@see ToolInvokeTypeEnum */
    invokeType?: string;
    /** 产品化 tool 定义结构化数据，主要保存用户在 opsgpt 页面上注册的 tool 结构信息 */
    structureDef?: string;
    /** 标签 */
    tag?: string;
    /** Tool的额外信息 */
    toolExtraInfo?: ToolExtraInfo;
    /** Gets get pause status list. */
    pauseStatusList?: Array<string>;
    configMap?: Record<string, any>;
  }

  interface ToolBriefInfo {
    /** tool唯一标识 */
    toolId?: string;
    /** tool名称 */
    toolKey?: string;
    /** tool描述 */
    description?: string;
    /** tool的owner */
    owner?: string;
    /** tool创建人 */
    operatorCreate?: string;
    /** tool修改人 */
    operatorModified?: string;
    /** tool的更新时间 */
    gmtModified?: string;
    /** tool的名称 */
    toolName?: string;
    /** 问法模板 */
    templates?: Array<string>;
  }

  interface ToolCall {
    /** 工具调用的ID */
    id?: string;
    /** Tool的类型，目前只支持function */
    type?: string;
    /** 模型决定调用的函数 */
    function?: ChatCompletionResponseFunction;
  }

  type ToolCreateTypeEnum = 'QUICK_INSTALL' | 'CUSTOM_INSTALL';

  interface ToolDef {
    /** 类型 */
    type?: string;
    /** 函数定义 */
    function?: ChatCompletionRequestFunctionDef;
  }

  type ToolDefParamTypeEnum =
    | 'string'
    | 'number'
    | 'integer'
    | 'object'
    | 'array'
    | 'boolean_';

  interface ToolDeleteRequest {
    /** 操作人，域账号，必填 */
    operator?: string;
    /** toolKey，必填 */
    toolKey?: string;
  }

  interface ToolExecuteRequest {
    /** 工具 id */
    toolId?: string;
    /** 发起人域账号 */
    domainAccount?: string;
    /** 工具入参 */
    toolParamMap?: Record<string, any>;
  }

  interface ToolExtraInfo {
    /** Tool增删改查过程汇总的错误信息 */
    errMessage?: string;
    /** Tool在向量数据库开发Collection主键 */
    devVdbPk?: string;
    /** Tool在向量数据库生产Collection主键 */
    prodVdbPk?: string;
    /** Tool执行结果Summary的方式 */
    summaryModel?: string;
    /** Tool的步骤列表
PARAM_FILL -> TOOL_EXECUTE -> TOOL_SUMMARY */
    stepConfigList?: Array<string>;
    /** 从 nex 创建的其他平台 tool 需要保存的额外信息 */
    nexExtraInfo?: NexExtraInfo;
    /** 从 nex 平台创建的 tool 需要保存的额外信息 */
    ispInfo?: IspInfo;
    /** Sofa RPC类型的Tool用于标识唯一的 tool */
    rpcUniqueId?: string;
  }

  interface ToolKeyCheckRequest {
    /** 产品，必须参数 */
    product?: string;
    /** 租户，必须参数 */
    tenant?: string;
    /** tool key，必须参数 */
    uniqKey?: string;
    /** toolId，更新 tool 时必需传该参数 */
    toolId?: string;
  }

  interface ToolProductStructDef {
    /** tool 基本信息，对应 tool 接入流程：填写 tool 基本信息 */
    basicInfo?: BasicInfo;
    /** api 定义相关信息，对应 tool 接入流程： api 定义 */
    apiMeta?: ApiMeta_T_;
    /** 构建请求信息，对应 tool 接入流程：构建请求 */
    toolReqDef?: ToolReqDef;
    /** 高级配置信息 */
    advancedInfo?: AdvancedInfo;
    /** 训练样本，对应 tool 接入流程：提供训练样本 */
    trainingSamples?: TrainingSamples;
  }

  interface ToolProductStructDef_AdvancedApiMeta_ {
    /** tool 基本信息，对应 tool 接入流程：填写 tool 基本信息 */
    basicInfo?: BasicInfo;
    /** api 定义相关信息，对应 tool 接入流程： api 定义 */
    apiMeta?: ApiMeta_AdvancedApiMeta_;
    /** 构建请求信息，对应 tool 接入流程：构建请求 */
    toolReqDef?: ToolReqDef;
    /** 高级配置信息 */
    advancedInfo?: AdvancedInfo;
    /** 训练样本，对应 tool 接入流程：提供训练样本 */
    trainingSamples?: TrainingSamples;
  }

  interface ToolProductStructDef_GPTManualApiMeta_ {
    /** tool 基本信息，对应 tool 接入流程：填写 tool 基本信息 */
    basicInfo?: BasicInfo;
    /** api 定义相关信息，对应 tool 接入流程： api 定义 */
    apiMeta?: ApiMeta_GPTManualApiMeta_;
    /** 构建请求信息，对应 tool 接入流程：构建请求 */
    toolReqDef?: ToolReqDef;
    /** 高级配置信息 */
    advancedInfo?: AdvancedInfo;
    /** 训练样本，对应 tool 接入流程：提供训练样本 */
    trainingSamples?: TrainingSamples;
  }

  interface ToolProductStructDef_GPTOneApiApiMeta_ {
    /** tool 基本信息，对应 tool 接入流程：填写 tool 基本信息 */
    basicInfo?: BasicInfo;
    /** api 定义相关信息，对应 tool 接入流程： api 定义 */
    apiMeta?: ApiMeta_GPTOneApiApiMeta_;
    /** 构建请求信息，对应 tool 接入流程：构建请求 */
    toolReqDef?: ToolReqDef;
    /** 高级配置信息 */
    advancedInfo?: AdvancedInfo;
    /** 训练样本，对应 tool 接入流程：提供训练样本 */
    trainingSamples?: TrainingSamples;
  }

  interface ToolProtocolRequest {
    /** 工具 id */
    toolId?: string;
    /** 请求用户域账号 */
    domainAccount?: string;
  }

  interface ToolProtocolResponse {
    /** 工具协议信息 */
    protocol?: NexaToolProtocol;
    /** 调用工具透传 header */
    headers?: Record<string, any>;
  }

  interface ToolReqDef {
    /** http 请求域名 */
    domain?: string;
    /** http 请求域名，预发 */
    preDomain?: string;
    /** http headers */
    headers?: Record<string, any>;
  }

  interface ToolResponse {
    /** object 对象 */
    object?: Record<string, any>;
    /** jsonObject 对象 */
    request?: Record<string, any>;
    /** map 对象 */
    path?: Record<string, any>;
    /** 结构化数据 */
    response?: EditableResponse;
    /** 结构化数据列表 */
    responseList?: Array<EditableResponse>;
  }

  interface TrainingSamples {
    /** select 触发指令训练样本 */
    selectSamples?: Array<string>;
    /** select 触发指令宏变量样本 */
    selectVars?: Array<Record<string, any>>;
  }

  interface UpdateAgentRequest {
    /** agent唯一主键 */
    agentId?: string;
    /** agent名称 */
    name?: string;
    /** agent类型 */
    agentType?: string;
    /** agent描述 */
    agentDesc?: string;
    /** 修改者 */
    operatorModified?: string;
    /** 头像，Base64编码 */
    avatar?: string;
    /** 开场白 */
    prologue?: string;
    /** 提问示例 */
    questionSample?: Array<string>;
    /** 选择Tool的分数阈值 */
    toolSelectScore?: string;
    /** Tool进行总结时的Summary Prompt模板 */
    toolSummaryPromptTmpl?: string;
    /** Tool列表 key: toolId, value: toolKey */
    toolMap?: Record<string, any>;
    /** 用户列表 key: domainName, value: role */
    userRoleMap?: Record<string, any>;
    /** 知识库Tool */
    knowledgeBaseTool?: string;
    /** 高级配置 */
    advancedConfig?: AgentAdvancedConfig;
    /** 内部配置 */
    innerConfig?: AgentInnerConfig;
  }

  interface UpdateAgentScenarioIsShowRequest {
    /** 场景 id */
    id?: number;
    /** 是否隐藏指令 显示：1 隐藏 0 */
    isShow?: string;
    /** 操作人 */
    operator?: string;
  }

  interface UpdateAgentScenarioNameRequest {
    /** 场景 id */
    id?: number;
    /** 节点名称 */
    name?: string;
    /** 节点类型 */
    nodeType?: string;
    /** 操作人 */
    operator?: string;
  }

  interface UpdateAgentScenarioParentRequest {
    /** 场景 id */
    id?: number;
    /** 父节点 id */
    parent?: number;
    /** 操作人 */
    operator?: string;
  }

  interface UrlCheckRequest {
    /** 访问路径 */
    url?: string;
  }

  interface User {
    /** 工号 */
    workNo?: string;
    /** 花名 */
    nickName?: string;
    /** 用户名 */
    operatorName?: string;
    /** 真名 */
    realName?: string;
  }

  interface YuQueAgentAndDocSlug {
    /** group login */
    agentId?: string;
    /** book and doc slug */
    groups?: Array<YuQueGroupLoginAndDocSlug>;
  }

  interface YuQueBookAndDocSlug {
    /** book slug */
    bookSlug?: string;
    /** doc slug */
    docs?: Array<string>;
  }

  interface YuQueBookInfoWithoutDoc {
    /** book slug */
    bookSlug?: string;
    /** book name */
    name?: string;
  }

  type YuQueDocSyncState = 'DOING' | 'SUCCESS' | 'FAILED';

  interface YuQueGroupInfo {
    /** groupLogin */
    groupLogin?: string;
    /** name */
    name?: string;
    /** token */
    token?: string;
    /** 头像 */
    avatarUrl?: string;
  }

  interface YuQueGroupInfoWithoutDoc {
    /** groupLogin */
    groupLogin?: string;
    /** name */
    name?: string;
    /** token */
    token?: string;
    /** books */
    books?: Array<YuQueBookInfoWithoutDoc>;
  }

  interface YuQueGroupLoginAndDocSlug {
    /** group login */
    groupLogin?: string;
    /** book and doc slug */
    books?: Array<YuQueBookAndDocSlug>;
  }

  interface YuQuePreHandleTriggerMessage {
    /** agent id */
    agentId?: string;
    /** 团队 */
    groupLogin?: string;
    /** 知识库 */
    bookSlug?: string;
    /** 文档 */
    docSlug?: string;
  }

  interface YuqueSelectInfo {
    /** token */
    token?: string;
    /** 用户的团队 */
    group?: string;
    /** 用户选中的知识库 */
    bookSlug?: string;
  }

  interface YuqueUserTokenDO {
    /** This property corresponds to db column <tt>id</tt>. */
    id?: number;
    /** This property corresponds to db column <tt>gmt_create</tt>. */
    gmtCreate?: string;
    /** This property corresponds to db column <tt>gmt_modified</tt>. */
    gmtModified?: string;
    /** This property corresponds to db column <tt>owner</tt>. */
    owner?: string;
    /** This property corresponds to db column <tt>token</tt>. */
    token?: string;
    /** This property corresponds to db column <tt>scope</tt>. */
    scope?: string;
  }
}
