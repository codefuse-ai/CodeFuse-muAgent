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
 * @version : Protocol.java, v 0.1 2024年10月11日 上午10:29 renmao.rm Exp $
 */
@Data
public class Protocol {

    /**
     * 请求的方法:
     *     GET,
     *     HEAD,
     *     POST,
     *     PUT,
     *     PATCH,
     *     DELETE,
     *     OPTIONS,
     *     TRACE;
     *
     */
    private String method;

    /**
     * 请求路径
     */
    private String path;

    /**
     * 请求参数
     */
    private List<ProtocolParameter> parameters;

    /**
     * responses 的结构暂时忽略
     */
    @JsonSerialize(using = JsonObjectSerializer.class)
    @JsonDeserialize(using = JsonObjectDeserializer.class)
    private JsonObject responses;
}