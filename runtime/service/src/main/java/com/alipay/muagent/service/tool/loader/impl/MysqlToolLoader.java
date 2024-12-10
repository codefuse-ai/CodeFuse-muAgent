/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.tool.loader.impl;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.mybatisplus.dto.ToolConverter;
import com.alipay.muagent.service.mybatisplus.dto.ToolDO;
import com.alipay.muagent.service.mybatisplus.mapper.ToolDoMapper;
import com.alipay.muagent.service.tool.loader.ToolLoader;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.LoggerUtil;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.google.common.collect.Lists;

import jakarta.annotation.PostConstruct;

/**
 * @author chenjue.wwp
 * @version : LocalToolLoader.java, v 0.1 2024年12月10日 下午7:23 chenjue.wwp Exp $
 */
@Service
@ConditionalOnProperty(name = "runtime.tool.datatype", havingValue = "mysql")
public class MysqlToolLoader implements ToolLoader {

    private static final Logger LOGGER = LoggerFactory.getLogger(MysqlToolLoader.class);

    @Autowired
    private ResourceLoader resourceLoader;


    @Autowired
    private ToolDoMapper   toolDoMapper;

    /**
     * Query tool by id tool.
     *
     * @param id the id
     * @return the tool
     */
    @Override
    public Tool queryToolById(Long id) {
        return queryMysqlToolById(id);
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
        return queryMysqlToolByKey(id);
    }

    private Tool queryMysqlToolById(Long id) {
        ToolDO toolDO = toolDoMapper.selectById(id);
        return new ToolConverter().convertFromDto(toolDO);
    }

    private Tool queryMysqlToolByKey(String key) {
        QueryWrapper<ToolDO> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("tool_key", key);
        ToolDO toolDO = toolDoMapper.selectOne(queryWrapper);
        return new ToolConverter().convertFromDto(toolDO);
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


    @PostConstruct
    public void initTools() {
        PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        try {
            // 注意：这里的路径以斜杠开头，并且需要包含双星号 ** 来匹配子目录
            Resource[] resources = resolver.getResources("classpath:/tools/**");
            for (Resource resource : resources) {
                if (resource.isReadable()) {  // 确保资源可读
                    String filename = resource.getFilename();
                    insertToMysql(filename);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void insertToMysql(String fileName) throws IOException {
        StringBuilder sBuffer;
        Resource resource = resourceLoader.getResource("classpath:tools/" + fileName);
        BufferedInputStream bufferedReader = new BufferedInputStream(resource.getInputStream());
        byte[] buffer = new byte[1024];
        int bytesRead = 0;
        sBuffer = new StringBuilder();
        while ((bytesRead = bufferedReader.read(buffer)) != -1) {
            sBuffer.append(new String(buffer, 0, bytesRead));
        }
        bufferedReader.close();

        Tool tool = GsonUtils.fromString(Tool.class, sBuffer.toString());
        ToolDO toolDO = new ToolConverter().convertFromEntity(tool);
        toolDO.setId(null);
        try {
            toolDoMapper.insert(toolDO);
        } catch (DataIntegrityViolationException e) {
            LoggerUtil.info(LOGGER, "insert tool failed, tool key: {}", toolDO.getToolKey());
        }

    }
}