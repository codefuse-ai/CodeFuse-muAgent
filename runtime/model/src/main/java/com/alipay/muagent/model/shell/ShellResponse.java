/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.shell;

import lombok.Builder;
import lombok.Data;

/**
 * @author renmao.rm
 * @version : ShellResponse.java, v 0.1 2024年10月11日 上午11:05 renmao.rm Exp $
 */
@Data
@Builder
public class ShellResponse {

    private String result;

    private String log;
}