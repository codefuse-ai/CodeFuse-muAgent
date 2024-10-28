/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web;

import com.alipay.muagent.model.scheduler.SubmitTaskRequest;
import com.alipay.muagent.model.scheduler.TaskExeResponse;
import com.alipay.muagent.service.sheduler.Scheduler;
import com.alipay.muagent.service.sheduler.SchedulerManager;
import com.alipay.muagent.web.base.BaseController;
import com.alipay.muagent.web.model.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author renmao.rm
 * @version : TaskController.java, v 0.1 2024年10月12日 下午5:07 renmao.rm Exp $
 */
@RestController
@RequestMapping("/task")
public class TaskController extends BaseController {

    @Autowired
    private SchedulerManager manager;

    @RequestMapping(method = RequestMethod.POST)
    @ResponseBody
    public Result<TaskExeResponse> submitTask(@RequestBody SubmitTaskRequest request) {
        return executeTemplate(() -> {
            Scheduler scheduler = manager.getScheduler(request.getSchedulerType());
            return scheduler.submitTask(request);
        });
    }
}