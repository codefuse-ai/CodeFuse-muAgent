/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.model.ekg;

import lombok.Data;

/**
 * @author renmao.rm
 * @version : EkgRequest.java, v 0.1 2024年10月16日 上午10:58 renmao.rm Exp $
 */
@Data
public class EkgRequest {

    public EkgRequest(EkgQueryRequest query) {
        this.features.setQuery(query);
    }

    private EkgFeaturesRequest features = new EkgFeaturesRequest();
}