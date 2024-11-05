/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.chat;

import com.alipay.muagent.model.enums.chat.ChatTypeEnum;
import com.google.gson.JsonObject;
import lombok.Data;

import javax.validation.constraints.NotNull;
import java.util.Map;

/**
 * @author renmao.rm
 * @version : ChatRequest.java, v 0.1 2024年10月09日 下午4:13 renmao.rm Exp $
 */
@Data
public class ChatRequest {

    /**
     * 会话ID
     */
    @NotNull(message = "sessionId不能为空")
    private String sessionId;

    /**
     * agent ID
     */
    @NotNull(message = "agentId不能为空")
    private String agentId;

    /**
     * 用户信息
     */
    private String userId;

    /**
     * 流式输出协议
     * 不填默认：false，流式输出必须传入 true
     */
    private Boolean stream;

    /**
     * 类型
     * text/card
     */
    private ChatTypeEnum type;

    /**
     * 内容
     */
    @NotNull(message = "content不能为空")
    private Map<String, Object> content;

    /**
     * 重试的时候需要带上提问id
     */
    private String msgId;

    /**
     * 扩展字段
     */
    private Map<String,Object> extendContext;


    /**
     * 接口调用来源
     */
    private String callSource;

    /**
     * 上一次submit chat返回的id
     */
    private String chatUniqueId;
}