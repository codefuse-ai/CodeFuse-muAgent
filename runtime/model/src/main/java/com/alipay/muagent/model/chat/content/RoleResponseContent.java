/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.chat.content;

import com.alipay.muagent.model.chat.ChatContent;
import com.alipay.muagent.model.chat.ChatResponse;
import lombok.Data;

/**
 * @author renmao.rm
 * @version : RoleResponseContent.java, v 0.1 2024年10月10日 下午7:30 renmao.rm Exp $
 */
@Data
public class RoleResponseContent extends ChatContent {

    private String url;

    private String name;

    private ChatResponse response;

    public static RoleResponseContent buildReferee(String rsp) {
        RoleResponseContent rrc = getRoleResponseContent(rsp);
        rrc.setName("主持人");
        rrc.setUrl("http://localhost:8080/avatar/referee.png");

        return rrc;
    }

    public static RoleResponseContent buildLijing(String rsp) {
        RoleResponseContent rrc = getRoleResponseContent(rsp);
        rrc.setName("李静");
        rrc.setUrl("http://localhost:8080/avatar/lijing.png");

        return rrc;
    }

    public static RoleResponseContent buildWangpeng(String rsp) {
        RoleResponseContent rrc = getRoleResponseContent(rsp);
        rrc.setName("王鹏");
        rrc.setUrl("http://localhost:8080/avatar/wangpeng.png");

        return rrc;
    }

    public static RoleResponseContent buildZhangwei(String rsp) {
        RoleResponseContent rrc = getRoleResponseContent(rsp);
        rrc.setName("张伟");
        rrc.setUrl("http://localhost:8080/avatar/zhangwei.png");

        return rrc;
    }

    private static RoleResponseContent getRoleResponseContent(String response) {
        RoleResponseContent rrc = new RoleResponseContent();
        rrc.setResponse(ChatResponse.buildTextResponse(response));
        return rrc;
    }
}