/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

/**
 * @author renmao.rm
 * @version : ProtocolSchema.java, v 0.1 2024年10月11日 上午10:35 renmao.rm Exp $
 */
@Data
public class ProtocolSchema {

    /**
     * $ref，参数的引用 id，与 FieldNode.id 是同一个值，该值将二者关联起来
     * 即可以通过 FieldNode.id 找到对应的 schema 参数，进而确定这个参数实际的参数位置
     */
    @JsonProperty("$ref")
    private String $ref;
}