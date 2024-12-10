/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.tool.loader.impl;

import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.tool.loader.ToolLoader;
import com.alipay.muagent.util.GsonUtils;
import com.google.common.collect.Lists;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.io.BufferedInputStream;
import java.util.List;

/**
 * @author renmao.rm
 * @version : LocalToolLoader.java, v 0.1 2024年10月11日 下午7:23 renmao.rm Exp $
 */
@Service
@ConditionalOnProperty(name = "runtime.tool.datatype", havingValue = "local")
public class LocalToolLoader implements ToolLoader {

    @Autowired
    private ResourceLoader resourceLoader;

    @Override
    public Tool queryToolById(Long id) {
        return queryToolByKey(String.valueOf(id));
    }

    @Override
    public List<Tool> queryToolsByIdList(List<Long> ids) {
        if (CollectionUtils.isEmpty(ids)) {
            return Lists.newArrayList();
        }
        return ids.stream().map(this::queryToolById).toList();
    }

    @Override
    public Tool queryToolByKey(String id) {
        String fileName = String.format("tools/%s.json", id);
        try {
            Resource resource = resourceLoader.getResource("classpath:" + fileName);
            BufferedInputStream bufferedReader = new BufferedInputStream(resource.getInputStream());
            byte[] buffer = new byte[1024]; // 设置缓冲区大小
            int bytesRead = 0;
            StringBuffer sBuffer = new StringBuffer();
            while ((bytesRead = bufferedReader.read(buffer)) != -1) {
                sBuffer.append(new String(buffer, 0, bytesRead));
            }
            bufferedReader.close();

            Tool tool = GsonUtils.fromString(Tool.class, sBuffer.toString());
            return tool;
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