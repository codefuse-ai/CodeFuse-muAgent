/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : ApiIvkSchemaInfo.java, v 0.1 2024年10月11日 上午10:24 renmao.rm Exp $
 */
@Data
public class ApiIvkSchemaInfo {

    /**
     * title
     */
    private String title;

    /**
     * description
     */
    private String description;

    /**
     * TODO version 是否有用
     */
    private String version = "0.0.1";
}