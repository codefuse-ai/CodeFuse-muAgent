/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.shell;

import lombok.Data;

import java.util.Map;

/**
 * @author renmao.rm
 * @version : ShellRequest.java, v 0.1 2024年10月11日 上午11:05 renmao.rm Exp $
 */
@Data
public class ShellRequest {

    private Map<String, Object> args;

    private String script;
}