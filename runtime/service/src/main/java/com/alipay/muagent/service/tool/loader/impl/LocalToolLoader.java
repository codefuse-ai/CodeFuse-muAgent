/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.tool.loader.impl;

import com.alipay.muagent.model.enums.tool.ToolDataTypeEnum;
import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.mybatisplus.dto.ToolConverter;
import com.alipay.muagent.service.mybatisplus.dto.ToolDO;
import com.alipay.muagent.service.mybatisplus.mapper.TooDOlMapper;
import com.alipay.muagent.service.tool.loader.ToolLoader;
import com.alipay.muagent.util.GsonUtils;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.google.common.collect.Lists;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
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
public class LocalToolLoader implements ToolLoader {

    @Autowired
    private ResourceLoader resourceLoader;

    @Value("${runtime.tool.datatype:local}")
    private String         toolType;
    
    @Autowired
    private TooDOlMapper   tooDOlMapper;

    /**
     * Query tool by id tool.
     *
     * @param id the id
     * @return the tool
     */
    @Override
    public Tool queryToolById(Long id) {
        ToolDataTypeEnum toolDataTypeEnum = ToolDataTypeEnum.getByName(toolType);
        return switch (toolDataTypeEnum) {
            case LOCAL -> queryLocalToolByKey(String.valueOf(id));
            case MYSQL -> queryMysqlToolById(id);
        };
    }

    /**
     * Query tools by id list list.
     *
     * @param ids the ids
     * @return the list
     */
    @Override
    public List<Tool> queryToolsByIdList(List<Long> ids) {
        if (CollectionUtils.isEmpty(ids)) {
            return Lists.newArrayList();
        }
        return ids.stream().map(this::queryToolById).toList();
    }

    /**
     * Query tool by key tool.
     *
     * @param id the id
     * @return the tool
     */
    @Override
    public Tool queryToolByKey(String id) {
        ToolDataTypeEnum toolDataTypeEnum = ToolDataTypeEnum.getByName(toolType);
        return switch (toolDataTypeEnum) {
            case LOCAL -> queryLocalToolByKey(id);
            case MYSQL -> queryMysqlToolByKey(id);
        };
    }

    private Tool queryMysqlToolById(Long id) {
        ToolDO toolDO = tooDOlMapper.selectById(id);
        return new ToolConverter().convertFromDto(toolDO);
    }

    private Tool queryMysqlToolByKey(String key) {
        QueryWrapper<ToolDO> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("tool_key", key);
        ToolDO toolDO = tooDOlMapper.selectOne(queryWrapper);
        return new ToolConverter().convertFromDto(toolDO);
    }

    private Tool queryLocalToolByKey(String key) {
        String fileName = String.format("tools/%s.json", key);
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
            throw new RuntimeException(String.format("loadToolFailed:%s", key), e);
        }
    }

    /**
     * Query tools by key list list.
     *
     * @param keys the keys
     * @return the list
     */
    @Override
    public List<Tool> queryToolsByKeyList(List<String> keys) {
        if (CollectionUtils.isEmpty(keys)) {
            return Lists.newArrayList();
        }
        return keys.stream().map(this::queryToolByKey).toList();
    }
}