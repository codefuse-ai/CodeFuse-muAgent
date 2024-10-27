/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : EkgQuestionDescription.java, v 0.1 2024年10月10日 上午11:30 renmao.rm Exp $
 */
@Data
public class EkgQuestionDescription {


    /**
     * 问题类型
     * "multipleChoice", # or "essayQuestion"
     */
    private String questionType;

    /**
     * 问题内容
     */
    private EkgQuestionContent questionContent;

    /**
     * 给用户展示的额外信息
     */
    private String extraMessage;
}