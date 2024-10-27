/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web;

import com.alipay.muagent.model.agent.Agent;
import com.alipay.muagent.service.agent.AgentService;
import com.alipay.muagent.web.base.BaseController;
import com.alipay.muagent.web.model.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * @author renmao.rm
 * @version : AgentController.java, v 0.1 2024年10月11日 下午9:00 renmao.rm Exp $
 */
@RestController
@RequestMapping("/api/portal/agent")
public class AgentController extends BaseController {

    @Autowired
    private AgentService agentService;

    @RequestMapping(value = "/queryList", method = RequestMethod.GET)
    @ResponseBody
    public Result<List<Agent>> exeToolTest() {
        return executeTemplate(()->  agentService.queryAgentList());
    }
}