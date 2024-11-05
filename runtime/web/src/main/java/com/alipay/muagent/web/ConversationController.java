/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web;

import com.alipay.muagent.model.chat.ChatRequest;
import com.alipay.muagent.model.chat.SessionCreateRequest;
import com.alipay.muagent.model.ekg.EkgQueryRequest;
import com.alipay.muagent.model.ekg.EkgAlgorithmResult;
import com.alipay.muagent.service.chat.ChatService;
import com.alipay.muagent.web.base.BaseController;
import com.alipay.muagent.web.model.Result;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.MediaType;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * @author renmao.rm
 * @version : ConversationController.java, v 0.1 2024年10月08日 下午5:12 renmao.rm Exp $
 */
@RestController
@RequestMapping("/api/portal/conversation")
public class ConversationController extends BaseController {

    private final static Logger LOGGER = LoggerFactory.getLogger(ConversationController.class);

    private final CopyOnWriteArrayList<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    @Autowired
    private ThreadPoolTaskExecutor chatSseEmitterPool;

    @Qualifier(("ekgChatServiceImpl"))
    @Autowired
    private ChatService ekgChatService;

    @RequestMapping(value = "/chat", method = RequestMethod.POST)
    public SseEmitter chatPost(@RequestBody ChatRequest chatRequest, HttpServletRequest request, HttpServletResponse response) {
        return getSseEmitter(chatRequest, ekgChatService);
    }

    @RequestMapping(value = "/chatEkg", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chatEkgPostPost(@RequestBody ChatRequest chatRequest, HttpServletRequest request, HttpServletResponse response) {
        return getSseEmitter(chatRequest, ekgChatService);
    }

    private SseEmitter getSseEmitter(ChatRequest chatRequest, ChatService service) {
        long startTime = System.currentTimeMillis();

        // 创建一个SseEmitter实例，todo 可配置化
        SseEmitter emitter = new SseEmitter(1000000L);

        // 添加到客户端列表中
        this.emitters.add(emitter);

        // 当客户端断开连接时，从列表中移除
        emitter.onCompletion(() -> this.emitters.remove(emitter));
        emitter.onTimeout(() -> this.emitters.remove(emitter));
        chatSseEmitterPool.execute(() -> {
            try {
                Result.success();
                // 发送开始事件
                emitter.send(SseEmitter.event().data("start"));

                service.chat(emitter, chatRequest);

                // 超级插件对话（GOC）：插件对话（成功）
                LOGGER.info(String.format("[PluginConversationController#chatPost]-[super plugin chat]-[chat success!]"
                        + "-[success]-[cost time:]-[%s]-[%s]-[%s]", System.currentTimeMillis() - startTime, chatRequest.getAgentId(), chatRequest.getUserId()));
                // 发送结束事件
                emitter.send(SseEmitter.event().data("end"));
            } catch (Exception e) {
                // 超级插件对话（GOC）：插件对话（失败）
                LOGGER.error(String.format("[PluginConversationController#chatPost]-[super plugin chat]-[got an exception!]"
                        + "-[failed]-[cost time:]-[%s]-[%s]-[%s]-[%s]", System.currentTimeMillis() - startTime, chatRequest.getAgentId(), chatRequest.getUserId(), e.getMessage()), e);
                emitter.completeWithError(e);
            } finally {
                emitter.complete();
            }
        });

        return emitter;
    }

    @RequestMapping(value = "/ekgTask", method = RequestMethod.POST)
    public Result<EkgAlgorithmResult> ekgTask(@RequestBody EkgQueryRequest request) {
        return executeTemplate(() -> ekgChatService.sendRequestToEkgPlanner(request));
    }

    @RequestMapping(value = "/createSession", method = RequestMethod.POST)
    public Result<String> createSession(@RequestBody SessionCreateRequest sessionCreateRequest) {
        return executeTemplate(() -> UUID.randomUUID().toString().replaceAll("-", ""));
    }
}