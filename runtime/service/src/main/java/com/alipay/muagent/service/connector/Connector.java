/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.connector;

import com.alipay.muagent.model.enums.tool.ToolProtocolEnum;
import com.alipay.muagent.model.tool.TaskExeContext;
import com.alipay.muagent.model.tool.ToolExeResponse;

/**
 * @author renmao.rm
 * @version : Connector.java, v 0.1 2024年10月10日 下午9:13 renmao.rm Exp $
 */
public interface Connector {

    ToolExeResponse executeTool(TaskExeContext context);

    ToolProtocolEnum register();
}