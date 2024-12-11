/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web.configuration;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.converter.json.GsonHttpMessageConverter;

/**
 * 配置GSON前端解析。
 * @author chenjue.wwp
 * @version $Id: GsonHttpMessageConvertersConfiguration.java, v 0.1 2024-11-23 15:54  Exp $$
 */
@Configuration
public class GsonHttpMessageConvertersConfiguration {
    @Bean
    public HttpMessageConverter<?> gsonHttpMessageConverter() {
        return new GsonHttpMessageConverter();
    }
}