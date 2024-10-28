/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.connector.impl;

import com.alipay.muagent.model.connector.http.HttpParameters;
import com.alipay.muagent.model.enums.tool.ToolProtocolEnum;
import com.alipay.muagent.model.shell.ShellRequest;
import com.alipay.muagent.model.shell.ShellResponse;
import com.alipay.muagent.model.tool.TaskExeContext;
import com.alipay.muagent.model.tool.ToolExeResponse;
import com.alipay.muagent.model.tool.meta.ApiIvkSchema;
import com.alipay.muagent.model.tool.meta.ManifestSchema;
import com.alipay.muagent.model.tool.meta.Tool;
import com.alipay.muagent.service.shell.ShellService;
import com.alipay.muagent.service.connector.Connector;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.HttpUtil;
import com.alipay.muagent.util.LoggerUtil;
import com.alipay.muagent.util.StringUtils;
import com.squareup.okhttp.internal.http.HttpMethod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.util.Map;

import static com.alipay.muagent.model.enums.tool.ToolProtocolEnum.HTTP;

/**
 * @author renmao.rm
 * @version : HttpConnector.java, v 0.1 2024年10月10日 下午10:26 renmao.rm Exp $
 */
@Service
public class HttpConnector implements Connector {

    private static final Logger LOGGER = LoggerFactory.getLogger(HttpConnector.class);

    @Autowired
    private ShellService shellService;

    @Override
    public ToolExeResponse executeTool(TaskExeContext context) {
        HttpParameters httpParameters = buildRequestParam(context);
        return invokeRequest(httpParameters, context);
    }

    private HttpParameters buildRequestParam(TaskExeContext context) {
        String input = context.getTaskRequest().getIntention();
        Tool tool = context.getTool();
        String requestGroovy = tool.getRequestGroovy();
        ApiIvkSchema apiSchema = tool.getApiSchema();
        ManifestSchema manifestSchema = tool.getManifestSchema();

        // 组装HTTP的请求地址
        String url = tool.getApiSchema().getServers().get(0).getUrl();

        ShellRequest shellRequest = GroovyConnector.buildShellRequest("request", input, requestGroovy);
        shellRequest.getArgs().put("stepMemory", context.getTaskRequest().getMemory());
        ShellResponse shellResponse = shellService.execute(shellRequest);

        // 对参数和requestBody进行处理
        // 获取requestBody
        HttpParameters httpParameters = GsonUtils.fromString(HttpParameters.class, shellResponse.getResult());
        Map<String, String> headers = httpParameters.getHeaderParameters();
        if (!CollectionUtils.isEmpty(manifestSchema.getHeaders()) && !CollectionUtils.isEmpty(headers)) {
            headers.putAll(manifestSchema.getHeaders());
        }

        //path参数的处理,将请求中的path参数替换成实际的值
        url = replacePathParameter(url, httpParameters.getPathParameters());
        httpParameters.setUrl(url);

        // 获取HTTP的请求类型
        String requestMethod = (StringUtils.isNotBlank(httpParameters.getRequestMethod()) ? httpParameters.getRequestMethod() : apiSchema.getPaths().getHttp().getMethod());
        httpParameters.setRequestMethod(requestMethod);

        return httpParameters;
    }

    private String replacePathParameter(String url, Map<String, String> pathParameters) {
        if (pathParameters == null) {
            return url;
        }
        for (Map.Entry<String, String> entry : pathParameters.entrySet()) {
            String key = entry.getKey();
            String value = entry.getValue();
            url = url.replace("{" + key + "}", value);
        }

        return url;
    }

    @Override
    public ToolProtocolEnum register() {
        return HTTP;
    }

    private ToolExeResponse invokeRequest(HttpParameters hparm, TaskExeContext context) {
        LoggerUtil.info(LOGGER, "receiveHttpRequest:{}", GsonUtils.toString(hparm));
        String responseBody = null;
        try {
            if (HttpMethod.permitsRequestBody(hparm.getRequestMethod())) {
                responseBody = HttpUtil.callWithHeadersAndQuery(hparm.getUrl(), hparm.getRequestBody(), hparm.getHeaderParameters(),
                        hparm.getQueryParameters(), hparm.getRequestMethod());
            } else {
                responseBody = HttpUtil.getWithHeadersAndParam(hparm.getUrl(), hparm.getHeaderParameters(), hparm.getQueryParameters());
            }
        } catch (Exception e) {
            throw new RuntimeException("http connector error", e);
        }

        LoggerUtil.info(LOGGER, "httpConnectorResponse:{}", responseBody);

        ShellRequest shellRequest = GroovyConnector.buildShellRequest("response", responseBody, context.getTool().getResponseGroovy());
        ShellResponse shellResponse = shellService.execute(shellRequest);

        ToolExeResponse ter = ToolExeResponse.builder()
                .result(shellResponse.getResult())
                .build();

        return ter;
    }
}