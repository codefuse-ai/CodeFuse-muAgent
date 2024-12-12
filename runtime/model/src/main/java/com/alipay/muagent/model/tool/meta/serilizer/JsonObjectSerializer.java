/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta.serilizer;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.ser.std.StdSerializer;

import com.google.gson.JsonObject;

import java.io.IOException;
/**
 * @author renmao.rm
 * @version : JsonObjectSerializer.java, v 0.1 2024年12月12日 15:58 renmao.rm Exp $
 */
public class JsonObjectSerializer extends StdSerializer<JsonObject> {

    public JsonObjectSerializer(Class<JsonObject> t) {
        super(t);
    }

    @Override
    public void serialize(JsonObject value, JsonGenerator gen, SerializerProvider provider) throws IOException {
        gen.writeRawValue(value.toString());
    }
}