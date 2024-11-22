/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.tool.loader.impl;

import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.mybatisplus.dto.ToolConverter;
import com.alipay.muagent.service.mybatisplus.dto.ToolDO;
import com.alipay.muagent.service.mybatisplus.mapper.TooDOlMapper;
import com.alipay.muagent.service.tool.loader.ToolLoader;
import com.google.common.collect.Lists;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ResourceLoader;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import java.util.List;

/**
 * @author renmao.rm
 * @version : LocalToolLoader.java, v 0.1 2024年10月11日 下午7:23 renmao.rm Exp $
 */
@Service
public class LocalToolLoader implements ToolLoader {

    @Autowired
    private ResourceLoader resourceLoader;

    @Autowired
    private TooDOlMapper   tooDOlMapper;

    @Override
    public Tool queryToolById(String id) {
        return queryToolByKey(id);
    }

    @Override
    public List<Tool> queryToolsByIdList(List<String> ids) {
        if (CollectionUtils.isEmpty(ids)) {
            return Lists.newArrayList();
        }
        return ids.stream().map(this::queryToolById).toList();
    }

    @Override
    public Tool queryToolByKey(String id) {
        try {
            ToolDO toolDO = tooDOlMapper.selectById(id);
            return new ToolConverter().convertFromDto(toolDO);
        } catch (Exception e) {
            throw new RuntimeException(String.format("loadToolFailed:%s", id), e);
        }
    }

    @Override
    public List<Tool> queryToolsByKeyList(List<String> keys) {
        if (CollectionUtils.isEmpty(keys)) {
            return Lists.newArrayList();
        }
        return keys.stream().map(this::queryToolByKey).toList();
    }
}