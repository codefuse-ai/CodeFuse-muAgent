/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.chat.content;

import com.alipay.muagent.model.chat.ChatContent;
import lombok.Builder;
import lombok.Data;

/**
 * @author renmao.rm
 * @version : TextContent.java, v 0.1 2024年10月10日 下午6:53 renmao.rm Exp $
 */
@Data
@Builder
public class TextContent extends ChatContent {

    /**
     * 大模型对话返回内容或用户提问内容
     */
    private String text;
}