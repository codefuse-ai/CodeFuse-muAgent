/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.shell.impl;

import com.alipay.muagent.model.shell.ShellRequest;
import com.alipay.muagent.model.shell.ShellResponse;
import com.alipay.muagent.service.shell.ShellService;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.LoggerUtil;
import com.alipay.muagent.util.StringUtils;
import groovy.lang.Binding;
import groovy.lang.GroovyClassLoader;
import groovy.lang.GroovyShell;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.PrintStream;
import java.util.Map;
import java.util.Set;

/**
 * @author renmao.rm
 * @version : ShellServiceImpl.java, v 0.1 2024年10月11日 上午11:06 renmao.rm Exp $
 */
@Service
public class ShellServiceImpl implements ShellService {

    private static final Logger LOGGER = LoggerFactory.getLogger(ShellServiceImpl.class);

    @Override
    public ShellResponse execute(ShellRequest request) {

        LoggerUtil.info(LOGGER, "receiveShellRequest:{}", GsonUtils.toString(request));
        Binding binding = new Binding();

        Map<String, Object> args = request.getArgs();
        if (!CollectionUtils.isEmpty(args)) {
            Set<String> keySet = args.keySet();
            for (String key : keySet) {
                binding.setVariable(key, args.get(key));
            }
        }

        GroovyClassLoader groovyClassLoader = loadGroovyClassLoader();

        // 创建ByteArrayOutputStream对象
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        // 创建PrintStream对象，并将ByteArrayOutputStream对象作为参数传入
        PrintStream printStream = new PrintStream(outputStream);
        binding.setProperty("out", printStream);

        GroovyShell shell = new GroovyShell(groovyClassLoader, binding);
        //执行脚本并返回结果
        Object result = null;
        try {
            result = shell.evaluate(request.getScript());
            LoggerUtil.info(LOGGER, "shellResult:{}", GsonUtils.toString(result));
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "ShellServiceImpl execute script error. Script:{}", request.getScript());
            throw new RuntimeException(e);
        }
        groovyClassLoader.clearCache();

        String log = outputStream.toString();

        try {
            outputStream.close();
            printStream.close();
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "ShellServiceImpl closed stream error.");
        }
        if (result instanceof String) {
           return ShellResponse.builder()
                   .result((String) result)
                   .log(log)
                   .build();
        }

        throw new RuntimeException(StringUtils.stringFormat("The shell result is not String.class, actual type is:{}, the result is:{}",  result.getClass().getSimpleName(),
                GsonUtils.toString(result)));
    }

    private static GroovyClassLoader loadGroovyClassLoader() {
        String classpath = System.getProperty("java.class.path");

        String[] paths = classpath.split(File.pathSeparator);
        String fullClassPath = classpath;
        for (String path : paths) {
            if (path.endsWith("executable")) {
                fullClassPath = path + "/BOOT-INF/lib/gson-2.9.0.jar";
            }
        }
        ClassLoader parentClassLoader = Thread.currentThread().getContextClassLoader();
        GroovyClassLoader groovyClassLoader = new GroovyClassLoader(parentClassLoader);
        groovyClassLoader.addClasspath(fullClassPath);
        return groovyClassLoader;
    }
}