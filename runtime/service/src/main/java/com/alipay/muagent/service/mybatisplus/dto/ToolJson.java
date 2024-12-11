/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.mybatisplus.dto;

import com.alipay.muagent.model.enums.tool.ToolProtocolEnum;
import com.alipay.muagent.model.tool.meta.ApiIvkSchema;
import com.alipay.muagent.model.tool.meta.ManifestSchema;
import com.alipay.muagent.model.tool.meta.ToolDef;
import lombok.Data;

/**
 * 对应DB中的tool_json,用来存放tool的复杂属性，不在DB中存放多个字段
 * @author chenjue.wwp
 * @version $Id: ToolGson.java, v 0.1 2024-11-22 14:38  Exp $$
 */
@Data
public class ToolJson {
    /**
     * tool的定义
     */
    private ToolDef          toolDefinition;
    /**
     * 用于做request转化的Groovy脚本代码
     */
    private String           requestGroovy;

    /**
     * 用于做response转化的Groovy脚本低吗
     */
    private String           responseGroovy;
    /**
     * 描述Tool背后的API或者大模型调用的元数据
     */
    private ManifestSchema   manifestSchema;

    /**
     * Tool使用API的协议类型，SOFA_RPC、HTTP、MAYA、LOCAL
     */
    private ToolProtocolEnum toolProtocol;

    /**
     * API的schema, Swagger的json格式
     */
    private ApiIvkSchema     apiSchema;
}