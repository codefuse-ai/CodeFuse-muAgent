package com.alipay.muagent.bootstrap;

import com.alipay.muagent.util.LoggerUtil;
import org.mybatis.spring.annotation.MapperScan;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;


@SpringBootApplication
@ComponentScan(basePackages = {"com.alipay.muagent"})
@MapperScan("com.alipay.muagent.service.mybatisplus.mapper")
public class BootstrapApplication {

	private static final Logger LOGGER = LoggerFactory.getLogger(BootstrapApplication.class);

	public static void main(String[] args) {
		try {
			SpringApplication.run(BootstrapApplication.class, args);
			LoggerUtil.info(LOGGER, "Runtime Application has been started!!");
		} catch (Exception e) {
			LoggerUtil.error(LOGGER, e, "Runtime has been failed.");
		}
	}
}
