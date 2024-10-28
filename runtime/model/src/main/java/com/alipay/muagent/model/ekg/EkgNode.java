/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : EkgNode.java, v 0.1 2024年10月10日 上午11:29 renmao.rm Exp $
 */
@Data
public class EkgNode {

    /**
     * tool描述
     */
    private String toolDescription;

    /**
     * 当前节点id
     */
    private String currentNodeId;

    /**
     * 上下文
     */
    private String memory;

    /**
     * 节点类型
     */
    private String type;

    /**
     * 用户交互信息
     */
    private EkgQuestionDescription questionDescription;
}