/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Builder;
import lombok.Data;

/**
 * @author renmao.rm
 * @version : ExeNodeResponse.java, v 0.1 2024年10月10日 下午8:31 renmao.rm Exp $
 */
@Data
@Builder
public class ExeNodeResponse {

    private String output;

    private String toolKey;
}