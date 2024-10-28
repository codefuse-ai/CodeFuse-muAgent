/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.chat.configuration;

import com.alipay.muagent.model.ekg.configuration.Config;
import com.google.common.collect.Lists;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * @author renmao.rm
 * @version : EkgConfiguration.java, v 0.1 2024年10月10日 下午9:02 renmao.rm Exp $
 */
@Configuration
public class EkgConfiguration {

    @Value("${ekg.chat.url}")
    private String ekgChatUrl;

    @Value("${ekg.candidate.tools}")
    private String ekgCadiDataTools;

    @Bean
    public Config getConfig() {
        Config config = new Config();
        config.setEkgUrl(ekgChatUrl);
        config.setToolKeys(Lists.newArrayList(ekgCadiDataTools.split(",")));
        return config;
    }
}