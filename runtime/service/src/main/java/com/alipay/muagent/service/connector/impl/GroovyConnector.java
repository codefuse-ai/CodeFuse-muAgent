/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.connector.impl;

import com.alipay.muagent.model.enums.tool.ToolProtocolEnum;
import com.alipay.muagent.model.shell.ShellRequest;
import com.alipay.muagent.model.shell.ShellResponse;
import com.alipay.muagent.model.tool.TaskExeContext;
import com.alipay.muagent.model.tool.ToolExeResponse;
import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.connector.Connector;
import com.alipay.muagent.service.shell.ShellService;
import com.google.common.collect.Maps;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;

import static com.alipay.muagent.model.enums.tool.ToolProtocolEnum.GROOVY;

/**
 * @author renmao.rm
 * @version : GroovyConnector.java, v 0.1 2024年10月18日 20:31 renmao.rm Exp $
 */
@Service
public class GroovyConnector implements Connector {

    @Autowired
    private ShellService shellService;

    @Override
    public ToolExeResponse executeTool(TaskExeContext context) {
        String input = context.getTaskRequest().getIntention();
        Tool tool = context.getTool();
        String requestGroovy = tool.getRequestGroovy();

        ShellRequest shellRequest = buildShellRequest("request", input, requestGroovy);
        shellRequest.getArgs().put("stepMemory", context.getTaskRequest().getMemory());
        ShellResponse shellResponse = shellService.execute(shellRequest);

        return ToolExeResponse.builder().result(shellResponse.getResult()).build();
    }

    public static ShellRequest buildShellRequest(String inputKey, String input, String script) {
        Map<String, Object> args = Maps.newHashMap();
        args.put(inputKey, input);

        ShellRequest shellRequest = new ShellRequest();
        shellRequest.setScript(script);
        shellRequest.setArgs(args);
        return shellRequest;
    }


    @Override
    public ToolProtocolEnum register() {
        return GROOVY;
    }
}