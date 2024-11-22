/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.util;

import com.alipay.muagent.model.trace.TraceThreadLocalContext;
import com.alipay.muagent.model.trace.TraceThreadLocalContextHolder;
import org.slf4j.Logger;
import org.slf4j.helpers.MessageFormatter;

/**
 * @author renmao.rm
 * @version : LoggerUtil.java, v 0.1 2024年10月10日 下午3:09 renmao.rm Exp $
 */
public class LoggerUtil {

    /**
     * 获取当前请求上下文的traceId
     * @return traceId
     */
    private static String getTraceId() {
        TraceThreadLocalContext traceThreadLocalContext = TraceThreadLocalContextHolder.getTraceThreadLocalContext();
        if (!traceThreadLocalContext.isEmpty()) {
            return traceThreadLocalContext.getCurrentTraceContext().getTraceId();
        }
        return null;
    }

    /**
     * info级别
     *
     * @param logger the logger
     * @param format the format
     * @param objs   the objs
     */
    public static void info(Logger logger, String format, Object... objs) {
        if (logger.isInfoEnabled()) {
            logger.info("[" + getTraceId() + "] " + format, objs);
        }
    }

    /**
     * warn级别
     *
     * @param logger the logger
     * @param format the format
     * @param objs   the objs
     */
    public static void warn(Logger logger, String format, Object... objs) {
        logger.warn("[" + getTraceId() + "][] " + format, objs);
    }

    /**
     * 用于出现异常时，记录异常堆栈信息。<br/> 注意，格式字符串中的占位符与slf4j一样。
     *
     * @param logger the logger
     * @param t      the t
     * @param format the format
     * @param args   the args
     */
    public static void warn(Logger logger, Throwable t, String format, Object... args) {
        String errorMsg = MessageFormatter.arrayFormat(format, args).getMessage();
        logger.warn("[" + getTraceId() + "][] " + errorMsg, t);
    }

    /**
     * error级别
     *
     * @param logger the logger
     * @param format the format
     * @param objs   the objs
     */
    public static void error(Logger logger, String format, Object... objs) {
        logger.error("[" + getTraceId() + "][] " + format, objs);
    }

    /**
     * 用于出现异常时，记录异常堆栈信息。<br/> 注意，格式字符串中的占位符与slf4j一样。
     *
     * @param logger the logger
     * @param t      the t
     * @param format the format
     * @param args   the args
     */
    public static void error(Logger logger, Throwable t, String format, Object... args) {
        String errorMsg = MessageFormatter.arrayFormat(format, args).getMessage();
        logger.error("[" + getTraceId() + "][] " + errorMsg, t);
    }

    /**
     * debug级别
     *
     * @param logger the logger
     * @param format the format
     * @param objs   the objs
     */
    public static void debug(Logger logger, String format, Object... objs) {
        if (logger.isDebugEnabled()) {
            logger.debug("[" + getTraceId() + "] " + format, objs);
        }
    }
}