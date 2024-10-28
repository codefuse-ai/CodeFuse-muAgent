/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web.base;

import java.io.IOException;

/**
 * @author renmao.rm
 * @version : ControllerProcessor.java, v 0.1 2024年10月11日 下午8:58 renmao.rm Exp $
 */
public interface ControllerProcessor<T> {

    T process() throws IOException;
}