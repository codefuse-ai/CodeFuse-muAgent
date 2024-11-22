/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import com.alipay.muagent.model.enums.tool.ToolProtocolEnum;
import lombok.Data;

import java.util.Date;

/**
 * @author renmao.rm
 * @version : Tool.java, v 0.1 2024年10月10日 下午9:25 renmao.rm Exp $
 */
@Data
public class Tool {

    private String id;

    /**
     * 创建时间
     */
    private Date gmtCreate;

    /**
     * 修改时间
     */
    private Date gmtModified;

    /**
     * tool类型标识，用于区分不同类型的task
     */
    private String toolKey;

    /**
     * tool的定义
     */
    private ToolDef toolDefinition;

    /**
     * tool的描述
     */
    private String description;

    /**
     * tool的名称
     */
    private String toolName;

    /**
     * 用于做request转化的Groovy脚本代码
     */
    private String requestGroovy;

    /**
     * 用于做response转化的Groovy脚本低吗
     */
    private String responseGroovy;

    /**
     * 描述Tool背后的API或者大模型调用的元数据
     */
    private ManifestSchema manifestSchema;

    /**
     * Tool使用API的协议类型，SOFA_RPC、HTTP、MAYA、LOCAL
     */
    private ToolProtocolEnum toolProtocol;

    /**
     * API的schema, Swagger的json格式
     */
    private ApiIvkSchema apiSchema;

    /**
     * 创建人
     */
    private String operatorCreate;

    /**
     * 修改人
     */
    private String operatorModified;

    /**
     * Tool的版本
     */
    private String version;

    /**
     * Tool的owner
     */
    private String owner;
}