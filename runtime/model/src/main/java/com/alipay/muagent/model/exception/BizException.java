/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.exception;

import com.alipay.muagent.model.enums.refactor.ResultCodeEnum;

/**
 * @author renmao.rm
 * @version : BizException.java, v 0.1 2024年10月11日 下午9:35 renmao.rm Exp $
 */
public class BizException extends RuntimeException {

    /**
     * 异常代码
     */
    private final ResultCodeEnum errorCode;
    /**
     * 巡检自定义异常
     * @param errorCode 错误码枚举
     */
    public BizException(ResultCodeEnum errorCode) {
        super(errorCode.getDescription());
        this.errorCode = errorCode;
    }

    /**
     * 巡检自定义异常
     * @param errorCode 错误码枚举
     * @param cause 异常
     */
    public BizException(ResultCodeEnum errorCode, Throwable cause) {
        super(cause.getMessage(),cause);
        this.errorCode = errorCode;
    }

    /**
     * 巡检自定义异常
     * @param errorCode 错误码枚举
     * @param cause 异常
     * @param message
     * @param params
     */
    public BizException(ResultCodeEnum errorCode, Throwable cause, String message, Object... params) {
        super(String.format(message, params), cause);
        this.errorCode = errorCode;
    }

    /**
     * 巡检自定义异常
     * @param errorCode 错误码枚举
     * @param errorMessage 错误码信息
     */
    public BizException(ResultCodeEnum errorCode,String errorMessage) {
        super(errorMessage);
        this.errorCode = errorCode;
    }

    /**
     * 获取错误码
     *
     * @return 错误码枚举值
     */
    public ResultCodeEnum getErrorCode() {
        return errorCode;
    }
}