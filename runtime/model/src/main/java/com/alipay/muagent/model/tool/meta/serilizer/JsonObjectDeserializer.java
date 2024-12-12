/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.tool.meta.serilizer;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.google.gson.JsonObject;

import java.io.IOException;

public class JsonObjectDeserializer extends JsonDeserializer<JsonObject> {

    @Override
    public JsonObject deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        return com.google.gson.JsonParser.parseString(p.getText()).getAsJsonObject();
    }
}