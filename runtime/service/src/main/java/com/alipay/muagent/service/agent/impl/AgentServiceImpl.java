/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.agent.impl;

import com.alipay.muagent.model.agent.Agent;
import com.alipay.muagent.service.agent.AgentService;
import com.alipay.muagent.util.GsonUtils;
import com.google.common.collect.Lists;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @author renmao.rm
 * @version : AgentServiceImpl.java, v 0.1 2024年10月11日 下午9:16 renmao.rm Exp $
 */
@Service
public class AgentServiceImpl implements AgentService {

    @Override
    public List<Agent> queryAgentList() {
        String agentStr = "{\"id\":\"9400019\",\"aiRecommend\":false,\"agentId\":\"20240905000110000000000455769\",\"agentName\":\"智能画布EKG演示Agent\",\"agentType\":\"PRIVATE\",\"agentDesc\":\"智能画布EKG演示Agent\",\"avatar\":\"http://localhost:8080/avatar/nex.png\",\"buildType\":\"TEMPLATE\",\"buildTypeInfo\":\"SRE_TEMPLATE\",\"source\":\"OPSGPT\",\"agentAttribute\":\"BIZ\",\"pluginStatus\":\"OFF\",\"spaceId\":\"8400002\",\"debugVersion\":null,\"publishVersion\":null,\"lastModifyUser\":\"jikong.tp\",\"creator\":\"jikong.tp\",\"gmtModified\":\"2024-09-05T06:42:37.000+00:00\",\"lastModifyUserView\":\"济空\",\"relationshipList\":null,\"agentRelationshipList\":null,\"knowledgeBaseRelationshipList\":null,\"skillRelationshipList\":null}";
        Agent agent = GsonUtils.fromString(Agent.class, agentStr);

        List<Agent> agents = Lists.newArrayList();
        agents.add(agent);
        return agents;
    }
}