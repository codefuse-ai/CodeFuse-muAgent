/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg.configuration;

import lombok.Data;

import java.util.List;

/**
 * @author renmao.rm
 * @version : Config.java, v 0.1 2024年10月10日 下午7:24 renmao.rm Exp $
 */
@Data
public class Config {

    private String ekgUrl;

    private List<String> toolKeys;
}