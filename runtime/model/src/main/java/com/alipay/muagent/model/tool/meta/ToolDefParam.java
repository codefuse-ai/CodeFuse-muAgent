/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import lombok.Data;

import java.util.Map;
import java.util.Set;

/**
 * @author renmao.rm
 * @version : ToolDefParam.java, v 0.1 2024年10月11日 上午10:46 renmao.rm Exp $
 */
@Data
public class ToolDefParam {

    /**
     * 类型枚举值
     */
    private String type;

    /**
     * 属性描述信息
     */
    private String description;

    /**
     * 枚举值，后续参数填充的信息只能从里面选择
     */
    private Set<String> enums;

    /**
     * 当 type = ToolDefParamTypeEnum.object 时需要设置
     */
    private Map<String, ToolDefParam> properties;

    /**
     * 当 type = ToolDefParamTypeEnum.array 时需要设置
     */
    private ToolDefParam items;

    /**
     * 必填参数
     */
    private Set<String> required;
}