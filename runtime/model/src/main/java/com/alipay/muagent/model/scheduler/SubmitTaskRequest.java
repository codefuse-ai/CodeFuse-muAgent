/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.scheduler;

import com.alipay.muagent.model.enums.scheduler.TaskSchedulerTypeEnum;
import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * @author renmao.rm
 * @version : SubmitTaskRequest.java, v 0.1 2024年10月10日 下午9:55 renmao.rm Exp $
 */
@Data
@Builder
public class SubmitTaskRequest {

    /**
     * user intention
     */
    private String intention;

    private String memory;

    private boolean ekgRequest;

    /**
     * the range of tools needed to execute
     */
    private List<String> tools;

    /**
     *
     */
    private TaskSchedulerTypeEnum schedulerType;
}