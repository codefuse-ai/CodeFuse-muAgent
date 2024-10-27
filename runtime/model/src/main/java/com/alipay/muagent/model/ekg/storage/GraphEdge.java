/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg.storage;

import com.google.gson.annotations.SerializedName;
import lombok.Data;

import java.util.HashMap;
import java.util.Map;

/**
 * @author jikong
 * @version GraphEdge.java, v 0.1 2024年10月11日 19:32 jikong
 */
@Data
public class GraphEdge {
    /**
     * 起点节点ID
     */
    @SerializedName("start_id")
    private String startId;

    /**
     * 终点节点ID
     */
    @SerializedName("end_id")
    private String endId;

    /**
     * 属性
     */
    Map<String, Object> attributes = new HashMap<>();
}