/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.chat;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : SessionCreateRequest.java, v 0.1 2024年10月11日 下午9:47 renmao.rm Exp $
 */
@Data
public class SessionCreateRequest {

    /**
     * session 过期时间
     */
    private String expireTime;

    /**
     * 标题摘要
     */
    private String summary;
}