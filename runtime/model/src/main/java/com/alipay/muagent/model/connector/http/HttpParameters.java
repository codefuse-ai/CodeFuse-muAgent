/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.connector.http;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

import java.util.Map;

/**
 * @author renmao.rm
 * @version : HttpParameters.java, v 0.1 2024年10月11日 下午1:40 renmao.rm Exp $
 */
@Data
@Builder
public class HttpParameters {

    private String url;

    private String requestMethod;

    /**
     * swagger的header类型参数
     */
    private Map<String, String> headerParameters;

    /**
     * swagger的path类型参数
     */
    private Map<String, String> pathParameters;

    /**
     * swagger的query类型参数
     */
    private Map<String, String> queryParameters;

    /**
     * swagger的body类型参数
     */
    private String requestBody;
}