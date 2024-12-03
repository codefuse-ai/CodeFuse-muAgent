/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.enums.tool;

/**
 * @author chenjue.wwp
 * @version : ToolDataTypeEnum.java, v 0.1 2024年12月03日 下午17:01 renmao.rm Exp $
 */
public enum ToolDataTypeEnum {
                              LOCAL("local", "本地数据"), MYSQL("mysql", "MYSQL数据");

    private String name;
    private String desc;

    ToolDataTypeEnum(String name, String desc) {
        this.name = name;
        this.desc = desc;
    }

    /**
     * Gets get by name.
     *
     * @param name the name
     * @return the get by name
     */
    public static ToolDataTypeEnum getByName(String name) {
        for (ToolDataTypeEnum toolDataTypeEnum : ToolDataTypeEnum.values()) {
            if (toolDataTypeEnum.name.equals(name)) {
                return toolDataTypeEnum;
            }
        }
        throw new RuntimeException("ToolDataTypeEnum not found");
    }

    /**
     * Getter method for property <tt>name</tt>.
     *
     * @return property value of name
     */
    public String getName() {
        return name;
    }

    /**
     * Setter method for property <tt>name</tt>.
     *
     * @param name value to be assigned to property name
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Getter method for property <tt>desc</tt>.
     *
     * @return property value of desc
     */
    public String getDesc() {
        return desc;
    }

    /**
     * Setter method for property <tt>desc</tt>.
     *
     * @param desc value to be assigned to property desc
     */
    public void setDesc(String desc) {
        this.desc = desc;
    }
}