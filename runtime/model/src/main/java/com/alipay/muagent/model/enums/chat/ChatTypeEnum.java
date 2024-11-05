/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.enums.chat;

import lombok.Getter;

import static com.alipay.muagent.model.enums.chat.ChatTypeBelongingTypeEnum.BOTH;
import static com.alipay.muagent.model.enums.chat.ChatTypeBelongingTypeEnum.RESPONSE;

/**
 * @author renmao.rm
 * @version : ChatTypeEnum.java, v 0.1 2024年10月09日 下午7:13 renmao.rm Exp $
 */
@Getter
public enum ChatTypeEnum {

    text("text", "文本类型", BOTH),
    role_response("role_response", "", RESPONSE),
    json("json", "json类型", BOTH),
    markdown("markdown", "markdown类型", RESPONSE),
    ;

    private String typeCode;

    private String description;

    private ChatTypeBelongingTypeEnum belongingTyp;

    ChatTypeEnum(String typeCode, String description, ChatTypeBelongingTypeEnum belongingTypeEnum) {
        this.typeCode = typeCode;
        this.description = description;
        this.belongingTyp = belongingTypeEnum;
    }
}