/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Builder;
import lombok.Data;

/**
 * @author renmao.rm
 * @version : EkgToolResponse.java, v 0.1 2024年10月19日 19:45 renmao.rm Exp $
 */
@Data
@Builder
public class EkgToolResponse {

    private String toolResponse;

    private String toolKey;

    private String toolParam;
}