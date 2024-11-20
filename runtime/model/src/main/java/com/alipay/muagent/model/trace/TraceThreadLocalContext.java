package com.alipay.muagent.model.trace;

import java.util.EmptyStackException;

/**
 * @author Joshua
 * @version TraceThreadLocalContext.java v1.0 2024-11-20 20:24
 **/
public class TraceThreadLocalContext {

    private final ThreadLocal<TraceContext> traceContextThreadLocal = new ThreadLocal<>();

    public void push(TraceContext traceContext) {
        if (traceContext == null) {
            return;
        }
        traceContextThreadLocal.set(traceContext);
    }

    public TraceContext pop() throws EmptyStackException {
        if (this.isEmpty()) {
            return null;
        }
        TraceContext traceContext = traceContextThreadLocal.get();
        this.clear();
        return traceContext;
    }

    public TraceContext getCurrentTraceContext() throws EmptyStackException {
        if (this.isEmpty()) {
            return null;
        }
        return traceContextThreadLocal.get();
    }

    public boolean isEmpty() {
        TraceContext traceContext = traceContextThreadLocal.get();
        return traceContext == null;
    }

    public void clear() {
        traceContextThreadLocal.remove();
    }
}
