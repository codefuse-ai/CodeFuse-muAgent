/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : BaseEkgResponse.java, v 0.1 2024年10月16日 上午11:16 renmao.rm Exp $
 */
@Data
public class BaseEkgResponse {

    private int resultCode;

    private String errorMsg;
}