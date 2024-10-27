/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.enums.ekg;

import lombok.Getter;

/**
 * @author renmao.rm
 * @version : ToolPlanTypeEnum.java, v 0.1 2024年10月21日 10:27 renmao.rm Exp $
 */
@Getter
public enum ToolPlanTypeEnum {
    USER_PROBLEM("userProblem"),

    ;

    private String code;

    ToolPlanTypeEnum(String code) {
        this.code = code;
    }
}