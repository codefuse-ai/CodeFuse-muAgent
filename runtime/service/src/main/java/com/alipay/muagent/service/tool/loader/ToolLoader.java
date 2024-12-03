/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.tool.loader;

import com.alipay.muagent.model.tool.meta.Tool;

import java.util.List;

/**
 * @author renmao.rm
 * @version : ToolLoader.java, v 0.1 2024年10月11日 下午7:22 renmao.rm Exp $
 */
public interface ToolLoader {

    Tool queryToolById(Long id);

    List<Tool> queryToolsByIdList(List<Long> id);

    Tool queryToolByKey(String toolKey);

    List<Tool> queryToolsByKeyList(List<String> keys);
}