/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.mybatisplus.dto;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.util.Date;

/**
 * @author chenjue.wwp
 * @version $Id: ToolDO.java, v 0.1 2024-11-22 14:35  Exp $$
 */
@Data
@TableName(value = "tool")
public class ToolDO {
    private Long id;

    /**
     * 创建时间
     */
    private Date   gmtCreate;

    /**
     * 修改时间
     */
    private Date   gmtModified;

    /**
     * tool类型标识，用于区分不同类型的task
     */
    private String toolKey;

    /**
     * tool的描述
     */
    private String description;

    /**
     * tool的名称
     */
    private String toolName;

    /**
     * 创建人
     */
    private String operatorCreate;

    /**
     * 修改人
     */
    private String operatorModified;

    /**
     * Tool的版本
     */
    private String version;

    /**
     * Tool的owner
     */
    private String owner;

    /**
     * JSON格式存放
     */
    private String toolJson;
}