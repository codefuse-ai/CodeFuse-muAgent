/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.sheduler;

import com.alipay.muagent.model.enums.scheduler.TaskSchedulerTypeEnum;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * @author renmao.rm
 * @version : SchedulerManager.java, v 0.1 2024年10月11日 下午2:59 renmao.rm Exp $
 */
@Component
public class SchedulerManager implements InitializingBean {

    @Autowired
    private List<Scheduler> connectors;

    private static Map<TaskSchedulerTypeEnum, Scheduler> p2Connector;

    @Override
    public void afterPropertiesSet() throws Exception {
        p2Connector = connectors.stream().collect(Collectors.toMap(Scheduler::register, c -> c));
    }

    public Scheduler getScheduler(TaskSchedulerTypeEnum p) {
        return p2Connector.get(p);
    }
}