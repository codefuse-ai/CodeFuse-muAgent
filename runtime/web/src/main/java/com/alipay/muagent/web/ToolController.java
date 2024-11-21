/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web;

import com.alipay.muagent.model.scheduler.SubmitTaskRequest;
import com.alipay.muagent.model.tool.TaskExeContext;
import com.alipay.muagent.model.tool.ToolExeResponse;
import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.connector.Connector;
import com.alipay.muagent.service.connector.ConnectorManager;
import com.alipay.muagent.service.tool.loader.ToolLoader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author renmao.rm
 * @version : ToolController.java, v 0.1 2024年10月11日 下午7:44 renmao.rm Exp $
 */
@RestController
@RequestMapping("/tool")
public class ToolController {

    @Autowired
    private ToolLoader toolLoader;

    @Autowired
    private ConnectorManager connectorManager;

    @RequestMapping(method = RequestMethod.GET)
    @ResponseBody
    public Tool queryToolById(@RequestParam Long id) {
        return toolLoader.queryToolById(id);
    }

    @RequestMapping(value = "/exe", method = RequestMethod.POST)
    @ResponseBody
    public ToolExeResponse exeToolDirect(@RequestBody SubmitTaskRequest taskRequest) {

        Tool tool =  toolLoader.queryToolByKey(taskRequest.getTools().get(0));
        Connector connector = connectorManager.getConnector(tool.getToolProtocol());

        TaskExeContext ctx = new TaskExeContext();
        ctx.setTool(tool);
        ctx.setTaskRequest(taskRequest);

       return connector.executeTool(ctx);
    }
}