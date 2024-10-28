/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Data;

import java.util.List;

/**
 * @author renmao.rm
 * @version : EkgAlgorithmResult.java, v 0.1 2024年10月10日 上午11:28 renmao.rm Exp $
 */
@Data
public class EkgAlgorithmResult {

    /**
     * 对应总线的conversationId
     */
    private String sessionId;

    /**
     * 节点类型
     */
    private String type;

    /**
     * 下一步的ekg节点
     */
    private List<EkgNode> toolPlan;

    /**
     * 关键节点信息
     */
    private String userInteraction;

    /**
     * 如果是图执行的最后一个节点,做图总结
     */
    private String summary;

    /**
     * 意图指导
     */
    private String intentionRecognitionSituation;
}