/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web.interceptor;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * @author renmao.rm
 * @version : WebConfigure.java, v 0.1 2024年10月29日 16:44 renmao.rm Exp $
 */
@Configuration
public class WebConfigure implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {

        registry.addMapping("/**")
                .allowedOrigins("http://30.183.177.8","http://localhost:8000")
                .allowedMethods("GET","HEAD","PUT","POST","PATCH","DELETE","OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
}