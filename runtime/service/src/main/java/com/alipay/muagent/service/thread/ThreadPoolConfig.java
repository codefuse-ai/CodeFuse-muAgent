/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.thread;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

/**
 * @author renmao.rm
 * @version : ThreadPoolConfig.java, v 0.1 2024年10月09日 下午4:52 renmao.rm Exp $
 */
@Configuration
public class ThreadPoolConfig {

    /**
     * 会话线程池
     *
     * @return the thread pool
     */
    @Bean("chatSseEmitterPool")
    public ThreadPoolTaskExecutor threadPoolTaskExecutor() {
        ThreadPoolTaskExecutor threadPoolTaskExecutor = new ThreadPoolTaskExecutor();
        threadPoolTaskExecutor.setCorePoolSize(10);
        threadPoolTaskExecutor.setMaxPoolSize(2000);
        threadPoolTaskExecutor.setQueueCapacity(10000);
        return threadPoolTaskExecutor;
    }
}