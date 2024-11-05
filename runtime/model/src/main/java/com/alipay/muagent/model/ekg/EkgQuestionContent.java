/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Data;

import java.util.List;

/**
 * @author renmao.rm
 * @version : EkgQuestionContent.java, v 0.1 2024年10月10日 上午11:29 renmao.rm Exp $
 */
@Data
public class EkgQuestionContent {

    /**
     * 问题
     */
    private String question;

    /**
     * 可能的选项。
     * 注意此项在问答题的时候为None
     */
    private List<String> candidate;

}