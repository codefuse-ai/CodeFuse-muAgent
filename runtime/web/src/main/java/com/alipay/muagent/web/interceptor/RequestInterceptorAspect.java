package com.alipay.muagent.web.interceptor;

import com.alipay.muagent.model.trace.TraceContext;
import com.alipay.muagent.model.trace.TraceThreadLocalContext;
import com.alipay.muagent.model.trace.TraceThreadLocalContextHolder;
import com.alipay.muagent.util.TraceUtil;
import com.alipay.muagent.web.model.Result;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.*;
import org.springframework.stereotype.Component;

/**
 * @author Joshua
 * @version RequestInterceptorAspect.java v1.0 2024-11-20 20:52
 **/
@Aspect
@Component
public class RequestInterceptorAspect {

    @Pointcut("@annotation(org.springframework.web.bind.annotation.RequestMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.GetMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.PostMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.PutMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.DeleteMapping)")
    public void requestMappingMethods() {
    }

    @Before("requestMappingMethods()")
    public void doBeforeRequestHandle() {
        TraceContext traceContext = new TraceContext();
        traceContext.setTraceId(TraceUtil.generateTraceId());
        TraceThreadLocalContext traceThreadLocalContext = TraceThreadLocalContextHolder.getTraceThreadLocalContext();
        traceThreadLocalContext.push(traceContext);
    }

    @AfterReturning(pointcut = "requestMappingMethods()", returning = "result")
    public void handleAfterReturning(JoinPoint joinPoint, Object result) {
        try {
            TraceContext traceContext = TraceThreadLocalContextHolder.getTraceThreadLocalContext().getCurrentTraceContext();
            ((Result<?>) result).setTraceId(traceContext.getTraceId());
        } catch (Exception e) {
            /*
            * empty catch
             */
        } finally {
            TraceThreadLocalContextHolder.getTraceThreadLocalContext().clear();
        }
    }

    @AfterThrowing(pointcut = "requestMappingMethods()", throwing = "error")
    public void handleAfterThrowing(JoinPoint joinPoint, Throwable error) {
        TraceThreadLocalContextHolder.getTraceThreadLocalContext().clear();
    }


}
