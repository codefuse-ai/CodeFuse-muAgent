/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Data;

import java.util.List;

/**
 * @author renmao.rm
 * @version : EkgRequest.java, v 0.1 2024年10月10日 上午11:01 renmao.rm Exp $
 */
@Data
public class EkgQueryRequest extends EkgSceneSessionRequest {

    private String startRootNodeId;

    /**
     * 为意图识别所用，意图识别时所采用的规则
     */
    private List<String> intentionRule;

    /**
     * 为意图识别所用，意图识别时所采用的数据
     */
    private List<String> intentionData;

    /**
     * 当前节点的id,第一次输入null
     */
    private String currentNodeId;

    /**
     * 当前节点的类型
     */
    private String type;

    /**
     * tool执行结果
     */
    private String observation;

    /**
     * 用户回答
     */
    private String userAnswer;
}