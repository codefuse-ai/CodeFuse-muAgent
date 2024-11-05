/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : ProtocolParameter.java, v 0.1 2024年10月11日 上午10:35 renmao.rm Exp $
 */
@Data
public class ProtocolParameter {

    /**
     * 参数位置，body/path/query
     */
    private String in;

    /**
     * schema
     */
    private ProtocolSchema schema;
}