/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import com.alipay.muagent.model.tool.meta.serilizer.JsonObjectDeserializer;
import com.alipay.muagent.model.tool.meta.serilizer.JsonObjectSerializer;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.google.gson.JsonObject;
import lombok.Data;

import java.util.List;

/**
 * @author renmao.rm
 * @version : ApiIvkSchema.java, v 0.1 2024年10月11日 上午10:22 renmao.rm Exp $
 */
@Data
public class ApiIvkSchema {

    /**
     * vesion
     */
    private String openapi = "3.0.0";

    /**
     * info
     */
    private ApiIvkSchemaInfo info;

    /**
     * servers
     */
    private List<ApiIvkSchemaServer> servers;

    /**
     * path
     */
    private Protocols paths;

    /**
     * model 定义
     */
    @JsonSerialize(using = JsonObjectSerializer.class)
    @JsonDeserialize(using = JsonObjectDeserializer.class)
    private JsonObject definitions;

    /**
     * 接口信息
     */
    @JsonSerialize(using = JsonObjectSerializer.class)
    @JsonDeserialize(using = JsonObjectDeserializer.class)
    private JsonObject apis;
}