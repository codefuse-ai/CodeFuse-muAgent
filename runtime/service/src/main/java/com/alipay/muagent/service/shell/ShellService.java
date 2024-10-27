/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.shell;

import com.alipay.muagent.model.shell.ShellRequest;
import com.alipay.muagent.model.shell.ShellResponse;

/**
 * @author renmao.rm
 * @version : ShellService.java, v 0.1 2024年10月11日 上午10:57 renmao.rm Exp $
 */
public interface ShellService {

    ShellResponse execute(ShellRequest request);
}