/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.chat;

import com.alipay.muagent.model.chat.ChatRequest;
import com.alipay.muagent.model.ekg.EkgQueryRequest;
import com.alipay.muagent.model.ekg.EkgAlgorithmResult;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/**
 * @author renmao.rm
 * @version : ChatService.java, v 0.1 2024年10月09日 上午10:57 renmao.rm Exp $
 */
public interface ChatService {

    /**
     * 流式对话
     *
     * @param emitter
     * @param request
     */
    void chat(SseEmitter emitter, ChatRequest request);

    /**
     * 提交 ekg 任务
     *
     * @param request
     * @return
     */
    EkgAlgorithmResult sendRequestToEkgPlanner(EkgQueryRequest request);
}