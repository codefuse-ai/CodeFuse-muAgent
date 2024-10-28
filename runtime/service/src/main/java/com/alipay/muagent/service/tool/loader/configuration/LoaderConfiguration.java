/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.tool.loader.configuration;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ResourceLoader;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

/**
 * @author renmao.rm
 * @version : Configuration.java, v 0.1 2024年10月16日 下午10:05 renmao.rm Exp $
 */
@Configuration
public class LoaderConfiguration {

    @Bean
    public ResourceLoader resourceLoader() {
        return new PathMatchingResourcePatternResolver();
    }
}