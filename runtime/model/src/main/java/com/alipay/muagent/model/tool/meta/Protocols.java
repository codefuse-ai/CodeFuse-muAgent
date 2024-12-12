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

/**
 * @author renmao.rm
 * @version : Protocols.java, v 0.1 2024年10月11日 上午10:25 renmao.rm Exp $
 */
@Data
public class Protocols {

    /**
     * http
     */
    private Protocol http;

    /**
     * tr
     */
    @JsonSerialize(using = JsonObjectSerializer.class)
    @JsonDeserialize(using = JsonObjectDeserializer.class)
    private JsonObject tr;
}