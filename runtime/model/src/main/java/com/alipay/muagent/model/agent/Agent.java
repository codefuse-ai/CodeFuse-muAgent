/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.agent;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import java.util.Date;

/**
 * @author renmao.rm
 * @version : Agent.java, v 0.1 2024年10月11日 下午8:47 renmao.rm Exp $
 */
@Data
public class Agent {
    /**
     * agentId
     */
    private Long id;

    /**
     * AI推荐
     */
    private boolean aiRecommend;

    /**
     * 下游agentId
     */
    private String agentId;

    /**
     * agent名称
     */
    @NotBlank(message = "agent名称不能为空")
    @Size(max = 255, message = "agent名称不能超过255个字符")
    private String agentName;

    /**
     * agent类型
     * ● PUBLIC：公共
     * ● PRIVATE：私有
     */
    private String agentType;

    /**
     * agent描述
     */
    @NotBlank(message = "agent描述不能为空")
    @Size(max = 255, message = "agent描述不能超过255个字符")
    private String agentDesc;

    /**
     * 头像
     */
    private String avatar;

    /**
     * 构建类型
     */
    private String buildType;

    /**
     * 构建类型信息
     */
    private String buildTypeInfo;

    /**
     * 来源
     */
    private String source;

    /**
     * agent属性
     */
    private String agentAttribute;

    /**
     * 插件状态
     */
    private String pluginStatus;

    /**
     * 空间id
     */
    private String spaceId;

    /**
     * 调试版本
     */
    private String debugVersion;

    /**
     * 发布版本
     */
    private String publishVersion;

    /**
     * 最后操作人
     */
    private String lastModifyUser;

    /**
     * 创建人
     */
    private String creator;

    /**
     * 修改时间
     */
    private Date gmtModified;

    /**
     * 最后操作人花名
     */
    private String lastModifyUserView;
}