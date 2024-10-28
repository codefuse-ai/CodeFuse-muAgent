/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.util;

import java.util.Map;
import java.util.function.Supplier;

/**
 * @author jikong
 * @version MapUtil.java, v 0.1 2024年10月11日 19:46 jikong
 */
public class MapUtil {
    public interface Container<K, V, T extends Map<K, V>> {
        /**
         * 向Map中添加元素
         *
         * @param k key
         * @param v value
         * @return 添加元素后的Map
         */
        Container<K, V, T> put(K k, V v);

        /**
         * 当condition为true时向Map中添加元素
         *
         * @param k key
         * @param v value
         * @param condition condition
         * @return 添加元素后的Map
         */
        Container<K, V, T> putIf(K k, V v, boolean condition);

        /**
         * 当condition为true时向Map中添加元素
         *
         * @param k key
         * @param vSupplier vSupplier
         * @param condition condition
         * @return 添加元素后的Map
         */
        Container<K, V, T> putIf(K k, Supplier<V> vSupplier, boolean condition);

        /**
         * 获取存储的数据
         *
         * @return 存储的数据
         */
        T value();
    }

    /**
     * 内部容器
     *
     * @param <K>
     * @param <V>
     * @param <T>
     */
    protected static class ContainerImpl<K, V, T extends Map<K, V>> implements Container<K, V, T> {
        /**
         * 用于实际存储数据
         */
        private final T m;

        /**
         * 构造函数
         */
        protected ContainerImpl(T m) {this.m = m;}

        /**
         * 向Map中添加元素
         *
         * @param k key
         * @param v value
         * @return 添加元素后的Map
         */
        public Container<K, V, T> put(K k, V v) {
            this.m.put(k, v);
            return this;
        }

        /**
         * 当condition为true时向Map中添加元素
         *
         * @param k key
         * @param v value
         * @param condition condition
         * @return 添加元素后的Map
         */
        public Container<K, V, T> putIf(K k, V v, boolean condition) {
            if (condition) {
                this.m.put(k, v);
            }
            return this;
        }

        /**
         * 当condition为true时向Map中添加元素
         *
         * @param k key
         * @param vSupplier vSupplier
         * @param condition condition
         * @return 添加元素后的Map
         */
        @Override
        public Container<K, V, T> putIf(K k, Supplier<V> vSupplier, boolean condition) {
            if (condition) {
                this.m.put(k, vSupplier.get());
            }
            return this;
        }

        /**
         * 获取存储的数据
         *
         * @return 存储的数据
         */
        public T value() {return this.m;}
    }

    /**
     * 根据初始数据构造装饰器
     *
     * @param sourceSupplier 初始数据
     * @param <K>            Map key对应的数据类型
     * @param <V>            Map value对应的数据类型
     * @param <T>            用户实际数据类型
     * @return 构造后的容器
     */
    public static <K, V, T extends Map<K, V>> Container<K, V, T> from(Supplier<T> sourceSupplier) {return new ContainerImpl<>(sourceSupplier.get());}
}