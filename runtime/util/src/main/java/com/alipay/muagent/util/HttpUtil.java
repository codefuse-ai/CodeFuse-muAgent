/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.util;

import com.squareup.okhttp.Callback;
import com.squareup.okhttp.HttpUrl;
import com.squareup.okhttp.MediaType;
import com.squareup.okhttp.OkHttpClient;
import com.squareup.okhttp.Request;
import com.squareup.okhttp.RequestBody;
import com.squareup.okhttp.Response;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * @author renmao.rm
 * @version : HttpUtil.java, v 0.1 2024年10月10日 下午2:58 renmao.rm Exp $
 */
public class HttpUtil {
    private static final MediaType JSONTYPE = MediaType.parse("application/json; charset=utf-8");
    private static final MediaType    FORMTYPE = MediaType.parse("application/x-www-form-urlencoded; charset=utf-8");
    private static final OkHttpClient OK_HTTP_CLIENT;

    static {
        OK_HTTP_CLIENT = new OkHttpClient();
        OK_HTTP_CLIENT.setConnectTimeout(3, TimeUnit.SECONDS);
        OK_HTTP_CLIENT.setReadTimeout(3, TimeUnit.MINUTES);
    }

    /**
     * get请求（带header），返回string
     *
     * @param url     the url
     * @param headers the headers
     * @return with headers
     * @throws IOException the io exception
     */
    public static String getWithHeaders(String url, Map<String, String> headers) throws IOException {
        Request.Builder builder = new Request.Builder().url(url);
        if (headers != null) {
            for (String key : headers.keySet()) {
                builder.addHeader(key, headers.get(key));
            }
        }
        Request request = builder.build();
        Response response = OK_HTTP_CLIENT.newCall(request).execute();
        if (response.isSuccessful()) {
            return response.body().string();
        } else {
            throw new IOException("Unexpected code " + response + "[" + response.body().string() + "]");
        }
    }

    /**
     * get请求（带header），返回string
     *
     * @param url      请求URL
     * @param headers  请求头
     * @param paramMap 查询参数
     * @return String格式的body
     * @throws IOException the io exception
     */
    public static String getWithHeadersAndParam(String url, Map<String, String> headers, Map<String, String> paramMap) throws IOException {
        HttpUrl.Builder httpUrlBuilder = HttpUrl.parse(url).newBuilder();
        if (null != paramMap && !paramMap.isEmpty()) {
            for (Map.Entry<String, String> entry : paramMap.entrySet()) {
                httpUrlBuilder.addQueryParameter(entry.getKey(), entry.getValue());
            }
        }
        HttpUrl httpUrl = httpUrlBuilder.build();

        Request.Builder builder = new Request.Builder().url(httpUrl.toString());
        if (headers != null) {
            for (String key : headers.keySet()) {
                builder.addHeader(key, headers.get(key));
            }
        }
        Request request = builder.build();
        Response response = OK_HTTP_CLIENT.newCall(request).execute();
        if (response.isSuccessful()) {
            return response.body().string();
        } else {
            throw new IOException("Unexpected code " + response + "[" + response.body().string() + "]");
        }
    }

    /**
     * post请求（带header）
     *
     * @param url         the url
     * @param requestBody the request body
     * @param headers     the headers
     * @return json object
     * @throws IOException the io exception
     */
    public static String postIterationJsonWithHeaders(String url, String requestBody,
                                                      Map<String, String> headers) throws IOException {
        RequestBody body = RequestBody.create(JSONTYPE, requestBody);
        Request.Builder builder = new Request.Builder().url(url).post(body);
        if (headers != null) {
            for (String key : headers.keySet()) {
                builder.addHeader(key, headers.get(key));
            }
        }
        Request request = builder.build();
        Response response = OK_HTTP_CLIENT.newCall(request).execute();
        if (response.isSuccessful()) {
            return response.body().string();
        } else {
            throw new IOException("Unexpected code " + response + "[" + response.body().string() + "]");
        }
    }

    /**
     * post请求（带header）
     *
     * @param url         the url
     * @param requestBody the request body
     * @param headers     the headers
     * @return json object
     * @throws IOException the io exception
     */
    public static String callWithHeadersAndQuery(String url,
                                                 String requestBody,
                                                 Map<String, String> headers,
                                                 Map<String, String> paramMap,
                                                 String method) throws IOException {
        HttpUrl.Builder httpUrlBuilder = HttpUrl.parse(url).newBuilder();
        if (null != paramMap && !paramMap.isEmpty()) {
            for (Map.Entry<String, String> entry : paramMap.entrySet()) {
                httpUrlBuilder.addQueryParameter(entry.getKey(), entry.getValue());
            }
        }
        HttpUrl httpUrl = httpUrlBuilder.build();

        String contentType = "application/json; charset=utf-8";
        if (headers != null && headers.containsKey("Content-Type")) {
            contentType = headers.get("Content-Type");
        }
        MediaType mediaType = MediaType.parse(contentType);
        RequestBody body = RequestBody.create(mediaType, requestBody);
        Request.Builder builder = new Request.Builder().url(httpUrl.toString()).method(method, body);
        if (headers != null) {
            for (String key : headers.keySet()) {
                builder.addHeader(key, headers.get(key));
            }
        }
        Request request = builder.build();
        Response response = OK_HTTP_CLIENT.newCall(request).execute();
        if (response.isSuccessful()) {
            return response.body().string();
        } else {
            throw new IOException("Unexpected code " + response + "[" + response.body().string() + "]");
        }
    }


    /**
     * 异步post请求（带header和query）
     *
     * @param url         the url
     * @param requestBody the request body
     * @param headers     the headers
     * @return json object
     * @throws IOException the io exception
     */
    public static void callAsyncWithHeadersAndQuery(String url,
                                                    String requestBody,
                                                    Map<String, String> headers,
                                                    Map<String, String> paramMap,
                                                    String method,
                                                    Callback callback) throws IOException {
        HttpUrl.Builder httpUrlBuilder = HttpUrl.parse(url).newBuilder();
        if (null != paramMap && !paramMap.isEmpty()) {
            for (Map.Entry<String, String> entry : paramMap.entrySet()) {
                httpUrlBuilder.addQueryParameter(entry.getKey(), entry.getValue());
            }
        }
        HttpUrl httpUrl = httpUrlBuilder.build();

        String contentType = "application/json; charset=utf-8";
        if (headers.containsKey("Content-Type")) {
            contentType = headers.get("Content-Type");
        }
        MediaType mediaType = MediaType.parse(contentType);
        RequestBody body = RequestBody.create(mediaType, requestBody);
        Request.Builder builder = new Request.Builder().url(httpUrl.toString()).method(method, body);
        if (headers != null) {
            for (String key : headers.keySet()) {
                builder.addHeader(key, headers.get(key));
            }
        }
        Request request = builder.build();
        OK_HTTP_CLIENT.newCall(request).enqueue(callback);
    }
}
