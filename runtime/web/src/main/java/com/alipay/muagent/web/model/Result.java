/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web.model;

import com.alipay.muagent.model.enums.refactor.ResultCodeEnum;
import lombok.Data;

import java.net.InetAddress;
import java.net.UnknownHostException;

/**
 * @author renmao.rm
 * @version : Result.java, v 0.1 2024年10月11日 下午8:51 renmao.rm Exp $
 */
@Data
public class Result<T> {

    private boolean success;

    private String errorCode;

    private String errorMessage;

    private T data;

    private String host = getLocalHost();

    /**
     * 创建一个方法执行成功的Result对象
     *
     * @return Result<Void>
     */
    public static Result<Void> success() {
        Result<Void> result = new Result<>();
        result.setSuccess(true);
        result.setErrorCode(ResultCodeEnum.SUCCESS.getCode());
        return result;
    }

    /**
     * 创建一个方法执行成功并返回数据的Result对象
     *
     * @param data 返回数据
     * @param <T>  数据类型
     * @return Result<T>
     */
    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.setSuccess(true);
        result.setErrorCode(ResultCodeEnum.SUCCESS.getCode());
        result.setData(data);
        return result;
    }

    /**
     * 创建一个方法执行失败的Result对象
     *
     * @param msg 结果消息
     * @param <T> 数据类型
     * @return Result<T>
     */
    public static <T> Result<T> fail(String msg) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setErrorCode(ResultCodeEnum.BIZ_FAIL.getCode());
        result.setErrorMessage(msg);
        return result;
    }

    /**
     * 创建一个失败的Result对象
     *
     * @param msg  错误信息
     * @param code 错误码
     * @param <T>  Result对象的泛型
     * @return 失败的Result对象
     */
    public static <T> Result<T> fail(String msg, String code) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setErrorCode(code);
        result.setErrorMessage(msg);
        return result;
    }


    /**
     * 创建一个方法执行失败的Result对象
     *
     * @param msg 结果消息
     * @param <T> 数据类型
     * @return Result<T>
     */
    public static <T> Result<T> noPermission(String msg) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setErrorCode(ResultCodeEnum.PERMISSION_DENIED.getCode());
        result.setErrorMessage(msg);
        return result;
    }

    /**
     * 获取宿主机名
     *
     * @return 宿主机名
     */
    private static String getLocalHost() {
        try {
            return InetAddress.getLocalHost().getHostAddress();
        } catch (UnknownHostException ue) {
            return "UnknownHost";
        }
    }

    /**
     * 获取方法是否成功
     *
     * @return 是否成功
     */
    public boolean isSuccess() {
        return success;
    }

    /**
     * 获取错误码
     *
     * @return 错误码
     */
    public String getErrorCode() {
        return errorCode;
    }

    /**
     * 获取错误信息
     *
     * @return 错误信息
     */
    public String getErrorMessage() {
        return errorMessage;
    }

    /**
     * 获取返回数据
     *
     * @return 返回数据
     */
    public T getData() {
        return data;
    }

    public String getHost() {
        return host;
    }
}
