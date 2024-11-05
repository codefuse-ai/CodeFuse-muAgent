/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg.storage;

import lombok.Data;

import java.util.HashMap;
import java.util.Map;

/**
 * @author jikong
 * @version GraphNode.java, v 0.1 2024年10月11日 19:32 jikong
 */
@Data
public class GraphNode {
    /**
     * 节点ID
     */
    private String id;

    /**
     * 节点类型
     */
    private String type;

    /**
     * 节点属性
     */
    Map<String, Object> attributes = new HashMap<>();
}