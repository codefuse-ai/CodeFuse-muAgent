/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg.storage;

import lombok.Data;

import java.util.LinkedList;
import java.util.List;

/**
 * @author jikong
 * @version GraphGraph.java, v 0.1 2024年10月11日 19:34 jikong
 */
@Data
public class GraphGraph {
    /**
     * 路径上的节点
     */
    List<GraphNode> nodes = new LinkedList<>();

    /**
     * 路径上的边
     */
    List<GraphEdge> edges = new LinkedList<>();
}