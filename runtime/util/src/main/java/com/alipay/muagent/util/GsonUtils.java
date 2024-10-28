/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.util;

import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.ToNumberPolicy;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

/**
 * @author renmao.rm
 * @version : GsonUtils.java, v 0.1 2024年10月10日 上午11:19 renmao.rm Exp $
 */
public class GsonUtils {

    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().setDateFormat("yyyy-MM-dd HH:mm:ss")
            .setNumberToNumberStrategy(ToNumberPolicy.LONG_OR_DOUBLE)
            .setObjectToNumberStrategy(ToNumberPolicy.LONG_OR_DOUBLE)
            .create();

    private static final Gson PRETTY_GSON = new GsonBuilder()
            .disableHtmlEscaping()
            .setDateFormat("yyyy-MM-dd HH:mm:ss")
            .setPrettyPrinting()
            .create();

    private static final Gson SNAKE_CASE_GSON = new GsonBuilder()
            .disableHtmlEscaping()
            .setDateFormat("yyyy-MM-dd HH:mm:ss")
            .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
            .create();

    /**
     * 将对象转化为JsonElement
     *
     * @param object the object
     * @return json element
     */
    public static JsonElement toJsonTree(Object object){
        return GSON.toJsonTree(object);
    }

    /**
     * 获取Geson
     *
     * @return gson
     */
    public static Gson getGson() {
        return GSON;
    }

    /**
     * 序列化
     *
     * @param o the o
     * @return string
     */
    public static String toString(Object o) {
        return GSON.toJson(o);
    }

    /**
     * 美化Json字符串
     *
     * @param o the o
     * @return string
     */
    public static String toPrettyString(String o) {
        return PRETTY_GSON.toJson(parse(o));
    }

    /**
     * 序列化
     *
     * @param o the o
     * @return string
     */
    public static String toPrettyString(Object o) {
        return PRETTY_GSON.toJson(o);
    }

    /**
     * 反序列化
     *
     * @param <T> the type parameter
     * @param c   the c
     * @param s   the s
     * @return t
     */
    public static <T> T fromString(Class<T> c, String s) {
        if (StringUtils.isBlank(s)) {
            return null;
        }
        return GSON.fromJson(s, c);
    }

    /**
     * 反序列化，下划线转驼峰
     *
     * @param <T> the type parameter
     * @param c   the c
     * @param s   the s
     * @return t
     */
    public static <T> T fromSnakeToCamelString(Class<T> c, String s) {
        if (StringUtils.isBlank(s)) {
            return null;
        }
        return SNAKE_CASE_GSON.fromJson(s, c);
    }


    /**
     * 反序列化
     *
     * @param <T>  the type parameter
     * @param type the type
     * @param s    the s
     * @return t
     */
    public static <T> T fromString(Type type, String s) {
        if (StringUtils.isBlank(s)) {
            return null;
        }
        return GSON.fromJson(s, type);
    }

    /**
     * 解析Json，用于细粒度地处理Json
     *
     * @param s the s
     * @return json element
     */
    public static JsonElement parse(String s) {
        return JsonParser.parseString(s);
    }

    /**
     * Parse array list.
     *
     * @param <T>   the type parameter
     * @param s     the s
     * @param clazz the clazz
     * @return the list
     */
    public static <T> List<T> parseArray(String s, Class<T> clazz) {
        Type type = TypeToken.getParameterized(List.class, clazz).getType();
        return fromString(type, s);
    }

    /**
     * Parse map map.
     *
     * @param <K>        the type parameter
     * @param <V>        the type parameter
     * @param s          the s
     * @param keyClazz   the key clazz
     * @param valueClazz the value clazz
     * @return the map
     */
    public static <K, V> Map<K, V> parseMap(String s, Class<K> keyClazz, Class<V> valueClazz) {
        Type type = TypeToken.getParameterized(Map.class, keyClazz, valueClazz).getType();
        return fromString(type, s);
    }

    /**
     * 反序列化
     *
     * @param <T>     the type parameter
     * @param c       the c
     * @param element the element
     * @return t
     */
    public static <T> T fromJsonElement(Class<T> c, JsonElement element) {
        if (element == null) {
            return null;
        }
        return GSON.fromJson(element, c);
    }


    /**
     * 反序列化
     *
     * @param <T>     the type parameter
     * @param element the element
     * @return t
     */
    public static <T> T fromJsonElement(Type type, JsonElement element) {
        if (element == null) {
            return null;
        }
        return GSON.fromJson(element, type);
    }

    /**
     * Gets string.
     *
     * @param jsonObject the json object
     * @param key        the key
     * @return the string
     */
    public static String getString(JsonObject jsonObject, String key) {
        return getString(jsonObject, key, false);
    }

    /**
     * Gets string.
     *
     * @param jsonObject the json object
     * @param key        the key
     * @param checkExist the check exist
     * @return the string
     */
    public static String getString(JsonObject jsonObject, String key, boolean checkExist) {
        if (jsonObject.has(key)) {
            return jsonObject.get(key).getAsString();
        } else {
            if (checkExist) {
                throw new NoSuchElementException("This key(" + key + ") is not exist!");
            }
        }

        return null;
    }
}