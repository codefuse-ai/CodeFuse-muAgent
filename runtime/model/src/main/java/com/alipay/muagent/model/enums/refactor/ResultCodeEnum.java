/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.enums.refactor;

import lombok.Getter;

/**
 * @author renmao.rm
 * @version : ResultCodeEnum.java, v 0.1 2024年10月11日 下午8:53 renmao.rm Exp $
 */
@Getter
public enum ResultCodeEnum {

    /**
     * 成功
     */
    SUCCESS("000", "SUCCESS"),

    /**
     * 参数非法
     */
    ILLEGAL_ARGUMENT("101", "ILLEGAL_ARGUMENT"),

    /**
     * 无权限
     */
    PERMISSION_DENIED("102", "PERMISSION_DENIED"),

    /**
     * 用户未登录
     */
    USER_NOT_LOGIN("103", "USER_NOT_LOGIN"),

    /**
     * BIZ FAIL
     */
    BIZ_FAIL("104", "BIZ_FAIL"),

    /**
     * 调用SPI失败，没有接收到SPI返回结果
     */
    INVOKE_SPI_WITHOUT_RESPONSE("210", "INVOKE_SPI_WITHOUT_RESPONSE"),

    /**
     * 调用SPI成功，SPI内部错误
     */
    SPI_INNER_ERROR("211", "SPI_INNER_ERROR"),

    /**
     * common internal error from opscloud
     */
    SYSTEM_ERROR("998", "SYSTEM_ERROR"),
    ;

    private String code;

    private String description;

    /**
     * @param code
     */
    ResultCodeEnum(String code, String description) {
        this.code = code;
        this.description = description;
    }

    /**
     * @param code
     * @return
     */
    public static ResultCodeEnum getByCode(String code) {
        for (ResultCodeEnum e : ResultCodeEnum
                .values()) {
            if (e.getCode().equalsIgnoreCase(code)) {
                return e;
            }
        }
        return null;
    }
}