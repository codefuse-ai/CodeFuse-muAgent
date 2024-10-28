/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web.base;

import com.alipay.muagent.model.exception.BizException;
import com.alipay.muagent.web.model.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @author renmao.rm
 * @version : BaseController.java, v 0.1 2024年10月11日 下午8:56 renmao.rm Exp $
 */
public class BaseController {

    protected static final Logger                      LOGGER = LoggerFactory.getLogger(BaseController.class);

    public <T> Result<T> executeTemplate(ControllerProcessor<T> processor) {
        try {
            T result = processor.process();
            return Result.success(result);
        } catch (BizException ne) {
            // 记录异常日志并返回失败结果
            String errorMessage = String.format("[%s#%s]-[Exception occurred in executing]: [%s]", this.getClass().getSimpleName(),
                    getCallingMethodName(), ne.getMessage());
            LOGGER.error(errorMessage, ne);
            return Result.fail("Exception occurred in executing: " + ne.getMessage(), ne.getErrorCode().getCode());
        } catch (Exception e) {
            String errorMessage = String.format("[%s#%s]-[Unexpected error in executing]: [%s]", this.getClass().getSimpleName(),
                    getCallingMethodName(), e.getMessage());
            LOGGER.error(errorMessage, e);
            return Result.fail("Unexpected error in executing: " + e.getMessage());
        }
    }

    /**
     * 获取调用当前方法的方法名
     *
     * @return 调用当前方法的方法名，如果无法获取则返回"Unknown Method"
     */
    private String getCallingMethodName() {
        // 获取当前线程的堆栈信息
        StackTraceElement[] stackTraceElements = Thread.currentThread().getStackTrace();
        for (int i = 0; i < stackTraceElements.length; i++) {
            // 查找调用 processWithTemplate 方法的堆栈信息
            if ("processWithTemplate".equals(stackTraceElements[i].getMethodName())) {
                // 返回调用 processWithTemplate 方法的方法名
                return stackTraceElements[i + 1].getMethodName();
            }
        }
        // 无法获取调用当前方法的方法名，返回"Unknown Method"
        return "Unknown Method";
    }
}