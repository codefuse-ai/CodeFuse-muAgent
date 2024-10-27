/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.sheduler;

import com.alipay.muagent.model.enums.scheduler.TaskSchedulerTypeEnum;
import com.alipay.muagent.model.scheduler.SubmitTaskRequest;
import com.alipay.muagent.model.scheduler.TaskExeResponse;
import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.model.tool.TaskExeContext;
import com.alipay.muagent.model.tool.ToolExeResponse;
import com.alipay.muagent.model.tool.callback.CallBackConfig;
import com.alipay.muagent.service.connector.Connector;
import com.alipay.muagent.service.connector.ConnectorManager;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.LoggerUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.Objects;

/**
 * @author renmao.rm
 * @version : Scheduler.java, v 0.1 2024年10月10日 下午9:57 renmao.rm Exp $
 */
public abstract class Scheduler {

    protected static final Logger LOGGER = LoggerFactory.getLogger(Scheduler.class);

    @Autowired
    private ConnectorManager manager;

    public TaskExeResponse submitTask(SubmitTaskRequest request) {
        LoggerUtil.info(LOGGER, "receiveTask:{}", GsonUtils.toString(request));
        TaskExeContext context = buildContext(request);

        Tool tool = selectTool(context);
        context.setTool(tool);

        ToolExeResponse toolExeResponse = executeTool(context);
        context.setToolExeResponse(toolExeResponse);

        if (Objects.nonNull(context.getCallBackConfig())) {
            callback(context);
        }
        return summary(context);
    }

    protected TaskExeContext buildContext(SubmitTaskRequest request) {
        TaskExeContext context = new TaskExeContext();
        context.setTaskRequest(request);
        context.setCallBackConfig(buildCallBackConfig(request));
        return context;
    }

    protected abstract CallBackConfig buildCallBackConfig(SubmitTaskRequest request);

    protected abstract TaskExeResponse summary(TaskExeContext context);

    protected abstract void callback(TaskExeContext context);

    protected ToolExeResponse executeTool(TaskExeContext context) {
        LoggerUtil.info(LOGGER, "executeTool:{}", GsonUtils.toString(context.getTool()));
        Connector connector = manager.getConnector(context.getTool().getToolProtocol());
        ToolExeResponse toolExeResponse = connector.executeTool(context);
        LoggerUtil.info(LOGGER, "toolExeResponse:{}", GsonUtils.toString(toolExeResponse));
        return toolExeResponse;
    }

    protected abstract Tool selectTool(TaskExeContext request);

    protected abstract TaskSchedulerTypeEnum register();
}