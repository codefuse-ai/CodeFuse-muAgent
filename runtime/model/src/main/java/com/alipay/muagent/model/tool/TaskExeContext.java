/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool;

import com.alipay.muagent.model.scheduler.SubmitTaskRequest;
import com.alipay.muagent.model.tool.callback.CallBackConfig;
import com.alipay.muagent.model.tool.meta.Tool;
import lombok.Data;

/**
 * @author renmao.rm
 * @version : ToolExeContext.java, v 0.1 2024年10月10日 下午9:26 renmao.rm Exp $
 */
@Data
public class TaskExeContext {

    public TaskExeContext() {

    }

    public TaskExeContext(Tool tool, String intention) {
        this.tool = tool;
        this.taskRequest = SubmitTaskRequest.builder().intention(intention).build();
    }

    private Tool tool;

    private SubmitTaskRequest taskRequest;

    private ToolExeResponse toolExeResponse;

    private CallBackConfig callBackConfig;
}