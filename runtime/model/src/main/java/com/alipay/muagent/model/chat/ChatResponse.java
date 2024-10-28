/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.chat;

import com.alipay.muagent.model.chat.content.RoleResponseContent;
import com.alipay.muagent.model.chat.content.TextContent;
import com.alipay.muagent.model.enums.chat.ChatTypeEnum;
import lombok.Builder;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static com.alipay.muagent.model.enums.chat.ChatTypeEnum.role_response;
import static com.alipay.muagent.model.enums.chat.ChatTypeEnum.text;

/**
 * @author renmao.rm
 * @version : ChatResponse.java, v 0.1 2024年10月17日 上午10:36 renmao.rm Exp $
 */
@Data
@Builder
public class ChatResponse {

    private ChatTypeEnum type;

    private ChatContent content;

    private Map<String, Object> extendContext;

    public static ChatResponse buildTextResponse(String content) {
        return ChatResponse.builder().type(text).content(TextContent.builder().text(content).build()).build();
    }

    public static List<ChatResponse> buildTextResponses(String content) {
        List<ChatResponse> responses = new ArrayList<>();
        responses.add(buildTextResponse(content));
        return responses;
    }

    public static ChatResponse buildRoleResponse(RoleResponseContent role) {
        return ChatResponse.builder().type(role_response).content(role).build();
    }

    public static List<ChatResponse> buildRoleResponses(RoleResponseContent role) {
        List<ChatResponse> responses = new ArrayList<>();
        responses.add(buildRoleResponse(role));
        return responses;
    }
}