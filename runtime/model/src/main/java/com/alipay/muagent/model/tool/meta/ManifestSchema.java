/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import lombok.Data;

import java.util.Map;

/**
 * @author renmao.rm
 * @version : ManifestSchema.java, v 0.1 2024年10月11日 上午10:19 renmao.rm Exp $
 */
@Data
public class ManifestSchema {

    /**
     * schema_version
     */
    private String schema_version = "v1";

    /**
     * name_for_human
     */
    private String name_for_human ;

    /**
     * name_for_model
     */
    private String name_for_model;

    /**
     * description_for_human
     */
    private String description_for_human;

    /**
     * description_for_model
     */
    private String description_for_model;

    /**
     * auth
     */
    private Map<String, String> auth;

    /**
     * api
     */
    private Map<String, String> api;

    /**
     * headers
     */
    private Map<String, String> headers;
}