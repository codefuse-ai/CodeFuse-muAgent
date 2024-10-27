/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.agent;

import com.alipay.muagent.model.agent.Agent;

import java.util.List;

/**
 * @author renmao.rm
 * @version : AgentService.java, v 0.1 2024年10月11日 下午9:06 renmao.rm Exp $
 */
public interface AgentService {

    List<Agent> queryAgentList();
}