/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.connector;

import com.alipay.muagent.model.enums.tool.ToolProtocolEnum;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * @author renmao.rm
 * @version : ConnectorManager.java, v 0.1 2024年10月10日 下午10:11 renmao.rm Exp $
 */
@Component
public class ConnectorManager implements InitializingBean {

    @Autowired
    private List<Connector> connectors;

    private static Map<ToolProtocolEnum, Connector> p2Connector;

    @Override
    public void afterPropertiesSet() throws Exception {
        p2Connector = connectors.stream().collect(Collectors.toMap(Connector::register, c -> c));
    }

    public Connector getConnector(ToolProtocolEnum p) {
        return p2Connector.get(p);
    }
}