/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.sheduler.impl;

import com.alipay.muagent.model.enums.scheduler.TaskSchedulerTypeEnum;
import com.alipay.muagent.model.exception.EkgToolNotFindException;
import com.alipay.muagent.model.scheduler.SubmitTaskRequest;
import com.alipay.muagent.model.scheduler.TaskExeResponse;
import com.alipay.muagent.model.tool.TaskExeContext;
import com.alipay.muagent.model.tool.ToolExeResponse;
import com.alipay.muagent.model.tool.callback.CallBackConfig;
import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.connector.impl.HttpConnector;
import com.alipay.muagent.service.sheduler.Scheduler;
import com.alipay.muagent.service.tool.loader.ToolLoader;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.LoggerUtil;
import com.alipay.muagent.util.StringUtils;
import lombok.Data;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @author renmao.rm
 * @version : BaseScheduler.java, v 0.1 2024年10月11日 下午3:07 renmao.rm Exp $
 */
@Service
public class BaseScheduler extends Scheduler implements InitializingBean {

    @Autowired
    private ToolLoader toolLoader;

    @Autowired
    private HttpConnector httpConnector;

    private Tool selectTool;

    @Override
    protected CallBackConfig buildCallBackConfig(SubmitTaskRequest request) {
        return null;
    }

    @Override
    protected TaskExeResponse summary(TaskExeContext context) {
        TaskExeResponse taskExeResponse = new TaskExeResponse();

        ToolExeResponse toolExeResponse = context.getToolExeResponse();

        taskExeResponse.setResponse(toolExeResponse.getResult());
        taskExeResponse.setToolKey(context.getTool().getToolKey());

        LoggerUtil.info(LOGGER, "taskExeResult:{}", taskExeResponse);
        return taskExeResponse;
    }

    @Override
    protected void callback(TaskExeContext context) {

    }

    @Override
    protected Tool selectTool(TaskExeContext request) {
        List<Tool> tools = toolLoader.queryToolsByKeyList(request.getTaskRequest().getTools());
        String prompt = generateSelectPrompt(tools, request.getTaskRequest().getIntention());
        LoggerUtil.info(LOGGER, "selectedPrompt:{}", prompt);

        TaskExeContext selectRequest = new TaskExeContext(selectTool, prompt);
        ToolExeResponse selectResponse = httpConnector.executeTool(selectRequest);
        LoggerUtil.info(LOGGER, "selectedTool:{}", GsonUtils.toString(selectResponse));
        String resultStr = selectResponse.getResult();
        try {
            if (StringUtils.equalNull(resultStr)) {
                return getTool(request);
            }
            SelectToolResult result = GsonUtils.fromString(SelectToolResult.class, resultStr);
            if (StringUtils.isEmpty(result.getToolKey()) || StringUtils.equalNull(resultStr)) {
                return getTool(request);
            }
            return toolLoader.queryToolByKey(result.getToolKey());
        } catch (EkgToolNotFindException e) {
           throw e;
        } catch (Exception e) {
            throw new RuntimeException("selectToolResponseInvalid:" + resultStr, e);
        }
    }

    private Tool getTool(TaskExeContext request) {
        if (request.getTaskRequest().isEkgRequest()) {
            // ekg 不能兜底，直接报错提示 tool 找不到
            //throw new EkgToolNotFindException("can not select a tool with intention " + request.getTaskRequest().getIntention());
            throw new EkgToolNotFindException("对不起，根据您的意图，无法找到对应的工具来帮助您，请添加相关工具后再使用图谱。");
        } else {
            // 闲聊大模型兜底
            Tool tool = toolLoader.queryToolByKey("system.llm_query");
            return tool;
        }
    }

    private String generateSelectPrompt(List<Tool> tools, String intention) {
        StringBuilder sb = new StringBuilder("你现在是一个插件选择助手，需要理解问题描述，然后从以下给出的插件中选择一个可以解决问题描述的插件").append("\n\n");
        sb.append("##插件列表：").append("\n");

        for (Tool toolInfo : tools) {
            sb.append("###插件名称：").append(toolInfo.getToolKey()).append("\n插件描述：").append(toolInfo.getToolName()).append("\n");
        }

        sb.append("\n").append("##约束条件：").append("\n")
                .append("-你必须按照以下JSON格式返回结果，并且不要给出问题分析的过程，{\"toolKey\":\"插件名称\"}\n")
                .append("-请尽可能从插件列表中选择合适的插件\n")
                .append("-如果插件列表中没有与问题描述匹配的插件请返回\"null\"\n")
                .append("-如果是模型不能回答的问题请返回\"null\"\n\n");

        sb.append("##问题描述：\n").append(intention);
        return sb.toString();
    }

    @Override
    protected TaskSchedulerTypeEnum register() {
        return TaskSchedulerTypeEnum.COMMON;
    }

    @Override
    public void afterPropertiesSet() throws Exception {
        selectTool = toolLoader.queryToolByKey("system.select_tool");
    }

    @Data
    class SelectToolResult {

        private String toolKey;
    }
}
