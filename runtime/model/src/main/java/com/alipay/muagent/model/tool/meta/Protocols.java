/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

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
    private JsonObject tr;
}