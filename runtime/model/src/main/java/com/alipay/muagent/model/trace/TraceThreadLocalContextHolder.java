package com.alipay.muagent.model.trace;

/**
 * @author Joshua
 * @version TraceThreadLocalContextHolder.java v1.0 2024-11-20 20:28
 **/
public class TraceThreadLocalContextHolder {

    /**
     * singleton SofaTraceContext
     */
    private static final TraceThreadLocalContext SINGLE_TRACE_CONTEXT = new TraceThreadLocalContext();

    /**
     * Get threadlocal trace context
     *
     * @return TraceThreadLocalContext
     */
    public static TraceThreadLocalContext getTraceThreadLocalContext() {
        return SINGLE_TRACE_CONTEXT;
    }

}
