/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.ekgmanager.impl;

import com.alipay.muagent.model.ekg.EkgNodeType;
import com.alipay.muagent.model.ekg.storage.GraphEdge;
import com.alipay.muagent.model.ekg.storage.GraphGraph;
import com.alipay.muagent.model.ekg.storage.GraphNode;
import com.alipay.muagent.model.ekg.storage.GraphUpdateRequest;
import com.alipay.muagent.service.ekgmanager.EkgGraphStorageClient;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.HttpUtil;
import com.alipay.muagent.util.LoggerUtil;
import com.alipay.muagent.util.MapUtil;
import com.google.gson.JsonElement;
import com.google.gson.reflect.TypeToken;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.Assert;
import org.springframework.util.StringUtils;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * @author jikong
 * @version EkgGraphStorageClientImpl.java, v 0.1 2024年10月11日 19:42 jikong
 */
@Service
public class EkgGraphStorageClientImpl implements EkgGraphStorageClient {
    private static final Logger LOGGER   = LoggerFactory.getLogger(EkgGraphStorageClientImpl.class);
    public static final  String AIS_HOST = "http://ekgservice:3737";

    enum AisService {
        EkgGraph(AIS_HOST + "/ekg/graph"),
        EkgNode(AIS_HOST + "/ekg/node"),
        EkgGraphUpdate(AIS_HOST + "/ekg/graph/update"),
        EkgNodeSearch(AIS_HOST + "/ekg/node/search"),
        EkgGraphAncestor(AIS_HOST + "/ekg/graph/ancestor");
        private final String url;

        AisService(String url) {
            this.url = url;
        }
    }

    private Map<String, Object> aisInvoke(AisService aisService, HashMap<String, Object> query) {
        try {
            HashMap<String, Object> request = new HashMap<>();
            HashMap<String, Object> features = new HashMap<>();
            features.put("query", query);
            request.put("features", features);
            String respStr = HttpUtil.postIterationJsonWithHeaders(aisService.url, GsonUtils.toString(request), new HashMap<>());
            LoggerUtil.info(LOGGER, "aisInvoke, " + aisService.name() + ", request: " + GsonUtils.toString(query) + ", response: " + respStr);
            JsonElement resp = GsonUtils.parse(respStr);
            String algorithmResult = resp.getAsJsonObject().get("resultMap").getAsJsonObject().get("algorithmResult").getAsString();
            return GsonUtils.parseMap(algorithmResult, String.class, Object.class);
        } catch (IOException e) {
            LoggerUtil.error(LOGGER, e, "算法接口请求异常");
            return null;
        }
    }

    private Map<String, Object> covertToAttributes(Object origin) {
        if (origin == null) {return null;}
        if (origin instanceof Map) {return (Map<String, Object>) origin;}
        throw new RuntimeException("不支持的Attribute类型转换");
    }

    private GraphNode convertToNode(Object origin) {
        if (origin == null) {return null;}
        if (origin instanceof GraphNode) {return (GraphNode) origin;}
        if (origin instanceof Map<?, ?> mo) {
            GraphNode node = new GraphNode();
            node.setId(mo.get("id").toString());
            node.setType(mo.get("type").toString());
            node.setAttributes(covertToAttributes(mo.get("attributes")));
            return node;
        }
        throw new RuntimeException("不支持的GNode类型转换");
    }

    private List<GraphNode> convertToNodes(List<?> origin) {return origin.stream().map(this::convertToNode).collect(Collectors.toList());}

    private GraphEdge convertToEdge(Object origin) {
        if (origin == null) {return null;}
        if (origin instanceof GraphEdge) {return (GraphEdge) origin;}
        if (origin instanceof Map<?, ?> mo) {
            GraphEdge edge = new GraphEdge();
            edge.setStartId(mo.get("start_id").toString());
            edge.setEndId(mo.get("end_id").toString());
            edge.setAttributes(covertToAttributes(mo.get("attributes")));
            return edge;
        }
        throw new RuntimeException("不支持的GNode类型转换");
    }

    private List<GraphEdge> convertToEdges(List<?> origin) {return origin.stream().map(this::convertToEdge).collect(Collectors.toList());}

    private GraphGraph convertToGraph(Object origin) {
        if (origin instanceof GraphGraph) {return (GraphGraph) origin;}
        if (origin instanceof Map<?, ?> mo) {
            GraphGraph graph = new GraphGraph();
            graph.setNodes(mo.containsKey("nodes") && (mo.get("nodes") instanceof List) ? convertToNodes((List<?>) mo.get("nodes")) : new LinkedList<>());
            graph.setEdges(mo.containsKey("edges") && (mo.get("edges") instanceof List) ? convertToEdges((List<?>) mo.get("edges")) : new LinkedList<>());
            return graph;
        }
        throw new RuntimeException("不支持的GNode类型转换");
    }

    /**
     * 根据团队ID查询图谱(外层图谱)
     *
     * @param teamRootId 团队根节点ID
     * @return
     */
    public GraphGraph getGraphByTeam(String teamRootId) {
        Map<String, Object> result = aisInvoke(AisService.EkgGraph, MapUtil.from(HashMap<String, Object>::new)
                .put("nodeid", teamRootId)
                .put("nodeType", EkgNodeType.Intent.getCode())
                .put("layer", "first")
                .value());

        LoggerUtil.info(LOGGER, "getGraphByTeam:{},{}", teamRootId, GsonUtils.toString(result));
        return convertToGraph(result);
    }

    /**
     * 根据节点ID查询图谱(内层图谱)
     *
     * @param nodeId 节点ID
     * @return 图谱(内层图谱)
     */
    public GraphGraph getGraphByNode(String nodeId, String nodeType) {
        Map<String, Object> result = aisInvoke(AisService.EkgGraph, MapUtil.from(HashMap<String, Object>::new)
                .put("nodeid", nodeId)
                .put("nodeType", nodeType)
                .put("layer", "second")
                .value());
        return convertToGraph(result);
    }

    /**
     * 获取节点详情
     *
     * @param nodeId 节点ID
     * @return 节点详情
     */
    public GraphNode getNode(String nodeId, String nodeType) {
        Map<String, Object> result = aisInvoke(AisService.EkgNode, MapUtil.from(HashMap<String, Object>::new)
                .put("nodeid", nodeId)
                .put("nodeType", nodeType)
                .value());
        return convertToNode(result.get("node"));
    }

    /**
     * 更新图谱数据
     *
     * @param request 请求参数
     * @return 是否更新成功
     */
    public GraphGraph updateGraph(GraphUpdateRequest request) {
        Map<String, Object> result = aisInvoke(AisService.EkgGraphUpdate, MapUtil.from(HashMap<String, Object>::new)
                .put("originNodes", request.getOldGraph().getNodes())
                .put("originEdges", request.getOldGraph().getEdges())
                .put("nodes", request.getNewGraph().getNodes())
                .put("edges", request.getNewGraph().getEdges())
                .put("teamid", request.getTeamId())
                .put("rootNodeId", request.getRootNodeId())
                .value());
        Object successCode = result.get("successCode");
        boolean succeed = false;
        if (successCode != null && StringUtils.hasLength(successCode.toString())) {
            if (successCode instanceof Number) {
                succeed = new BigDecimal(successCode.toString()).compareTo(new BigDecimal("1")) == 0;
            } else if (successCode instanceof Boolean) {
                succeed = (boolean) successCode;
            }
        }
        String errorMessage = (String) result.get("errorMessage");
        Assert.isTrue(succeed, errorMessage != null ? errorMessage : "图谱更新失败");
        return convertToGraph(result);
    }

    /**
     * 节点搜索
     *
     * @param teamId 团队ID
     * @param text   搜索文本
     * @return 搜索结果
     */
    public List<GraphNode> searchNode(String teamId, String text) {
        Map<String, Object> result = aisInvoke(AisService.EkgNodeSearch, MapUtil.from(HashMap<String, Object>::new)
                .put("text", text)
                .put("teamid", teamId)
                .value());
        return convertToNodes((List<?>) result.get("nodes"));
    }

    /**
     * 根据节点ID查询祖先链路
     *
     * @param teamRootId 团队根节点ID
     * @param nodeId     节点ID
     * @return 祖先链路
     */
    public GraphGraph getNodeAncestor(String teamRootId, String nodeId, String nodeType) {
        Map<String, Object> result = aisInvoke(AisService.EkgGraphAncestor, MapUtil.from(HashMap<String, Object>::new)
                .put("nodeid", nodeId)
                .put("nodeType", nodeType)
                .put("rootid", teamRootId)
                .value());
        return convertToGraph(result);
    }
}