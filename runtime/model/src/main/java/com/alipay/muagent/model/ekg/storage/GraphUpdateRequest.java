/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg.storage;

import lombok.Data;

/**
 * @author jikong
 * @version GraphUpdateRequest.java, v 0.1 2024年10月11日 19:36 jikong
 */
@Data
public class GraphUpdateRequest {
    /**
     * 团队ID
     */
    private String teamId;

    /**
     * 当前层级的根节点ID
     * 外层图谱: 团队根节点(开始节点)
     * 内层图谱: 计划节点
     */
    private String rootNodeId;

    /**
     * 更新前的图
     */
    private GraphGraph oldGraph = new GraphGraph();

    /**
     * 更新后的图
     */
    private GraphGraph newGraph = new GraphGraph();
}