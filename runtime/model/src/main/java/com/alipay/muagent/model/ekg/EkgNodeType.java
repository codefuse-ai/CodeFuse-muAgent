/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Getter;

/**
 * @author jikong
 * @version EkgNodeType.java, v 0.1 2024年10月11日 19:44 jikong
 */
@Getter
public enum EkgNodeType {
    Intent("opsgptkg_intent", "意图节点"),
    Schedule("opsgptkg_schedule", "计划节点"),
    Task("opsgptkg_task", "任务节点"),
    Analysis("opsgptkg_analysis", "分析结论节点"),
    Phenomenon("opsgptkg_phenomenon", "实事现象节点");

    private final String code;
    private final String description;

    EkgNodeType(String code, String description) {
        this.code = code;
        this.description = description;
    }
}