/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : ToolDef.java, v 0.1 2024年10月11日 上午10:46 renmao.rm Exp $
 */
@Data
public class ToolDef {

    private String name;

    /**
     * Tool的详细描述，描述Tool是用来做什么的，描述中包含接受什么样的参数，返回什么什么样的内容
     */
    private String description;

    /**
     * 入参定义
     */
    private ToolDefParam parameters;

    /**
     * 结果定义
     */
    private ToolDefParam result;
}