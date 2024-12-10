/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.mybatisplus.dto;

import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.util.GsonUtils;

/**
 * @author chenjue.wwp
 * @version $Id: ToolConverter.java, v 0.1 2024-11-22 14:43  Exp $$
 */
public class ToolConverter extends Converter<ToolDO, Tool> {

    private static final ToolConverter INSTANCE = new ToolConverter();
    public static ToolConverter getInstance() {
        return INSTANCE;
    }

    /**
     * Constructor.
     */
    public ToolConverter() {
        super(toolDO -> {
            ToolJson toolJson = GsonUtils.fromString(ToolJson.class, toolDO.getToolJson());
            Tool tool = new Tool();
            tool.setId(toolDO.getId());
            tool.setGmtCreate(toolDO.getGmtCreate());
            tool.setGmtModified(toolDO.getGmtModified());
            tool.setToolKey(toolDO.getToolKey());
            tool.setDescription(toolDO.getDescription());
            tool.setToolName(toolDO.getToolName());
            tool.setOperatorCreate(toolDO.getOperatorCreate());
            tool.setGmtModified(toolDO.getGmtModified());
            tool.setVersion(toolDO.getVersion());
            tool.setOwner(toolDO.getOwner());
            if (toolJson != null) {
                tool.setToolDefinition(toolJson.getToolDefinition());
                tool.setRequestGroovy(toolJson.getRequestGroovy());
                tool.setResponseGroovy(toolJson.getResponseGroovy());
                tool.setManifestSchema(toolJson.getManifestSchema());
                tool.setToolProtocol(toolJson.getToolProtocol());
                tool.setApiSchema(toolJson.getApiSchema());
            }
            return tool;
        }, tool -> {
            ToolDO toolDO = new ToolDO();
            toolDO.setId(tool.getId());
            toolDO.setGmtCreate(tool.getGmtCreate());
            toolDO.setGmtModified(tool.getGmtModified());
            toolDO.setToolKey(tool.getToolKey());
            toolDO.setDescription(tool.getDescription());
            toolDO.setToolName(tool.getToolName());
            toolDO.setToolName(tool.getToolName());
            toolDO.setOperatorCreate(tool.getOperatorCreate());
            toolDO.setGmtModified(tool.getGmtModified());
            toolDO.setVersion(tool.getVersion());
            toolDO.setOwner(tool.getOwner());
            ToolJson toolJson = new ToolJson();
            toolJson.setToolDefinition(tool.getToolDefinition());
            toolJson.setRequestGroovy(tool.getRequestGroovy());
            toolJson.setResponseGroovy(tool.getResponseGroovy());
            toolJson.setManifestSchema(tool.getManifestSchema());
            toolJson.setToolProtocol(tool.getToolProtocol());
            toolJson.setApiSchema(tool.getApiSchema());
            toolDO.setToolJson(GsonUtils.toString(toolJson));
            return toolDO;
        });
    }
}