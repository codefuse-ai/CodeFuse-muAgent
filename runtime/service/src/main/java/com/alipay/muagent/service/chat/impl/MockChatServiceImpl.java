/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.chat.impl;

import com.alipay.muagent.model.chat.ChatRequest;
import com.alipay.muagent.model.chat.ChatResponse;
import com.alipay.muagent.model.ekg.EkgAlgorithmResult;
import com.alipay.muagent.model.ekg.EkgQueryRequest;
import com.alipay.muagent.service.chat.ChatService;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.LoggerUtil;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;
import java.util.Map;

import static com.alipay.muagent.model.chat.ChatResponse.buildRoleResponse;
import static com.alipay.muagent.model.chat.content.RoleResponseContent.buildLijing;
import static com.alipay.muagent.model.chat.content.RoleResponseContent.buildReferee;
import static com.alipay.muagent.model.chat.content.RoleResponseContent.buildWangpeng;
import static com.alipay.muagent.model.chat.content.RoleResponseContent.buildZhangwei;

/**
 * @author renmao.rm
 * @version : MockChatServiceImpl.java, v 0.1 2024年10月17日 上午10:25 renmao.rm Exp $
 */
@Slf4j
@Service("mockChatServiceImpl")
public class MockChatServiceImpl implements ChatService {

    private static final List<List<ChatResponse>> roles = Lists.newArrayList();

    static {
        roles.add(Lists.newArrayList(buildRoleResponse(buildReferee("你好，我是主持人。"))));
        roles.add(Lists.newArrayList(buildRoleResponse(buildWangpeng("你好，我是王鹏。"))));
        roles.add(Lists.newArrayList(buildRoleResponse(buildLijing("你好，我是李静。"))));
        ChatResponse zhangwei = buildRoleResponse(buildZhangwei("你好，我是张伟。"));
        Map<String, Object> context = Maps.newHashMap();
        context.put("test", "hi");
        context.put("test1", "hi11");
        zhangwei.setExtendContext(context);
        roles.add(Lists.newArrayList(zhangwei));
    }

    @Override
    public void chat(SseEmitter emitter, ChatRequest request) {
        int count = 0;
        while (count < 4) {
            try {
                List<ChatResponse> role = roles.get(count);
                emitter.send(SseEmitter.event().data(GsonUtils.toString(role)));
                count ++;
                Thread.sleep(1000L);
            } catch (Exception e) {
                LoggerUtil.error(log, e, "Mock chat service error");
            }
        }
    }

    @Override
    public EkgAlgorithmResult sendRequestToEkgPlanner(EkgQueryRequest request) {
        return null;
    }
}