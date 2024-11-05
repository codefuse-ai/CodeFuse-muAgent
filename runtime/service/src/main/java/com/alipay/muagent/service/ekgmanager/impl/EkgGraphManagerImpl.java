/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.ekgmanager.impl;

import com.alipay.muagent.model.ekg.EkgNodeType;
import com.alipay.muagent.model.ekg.storage.GraphGraph;
import com.alipay.muagent.model.ekg.storage.GraphNode;
import com.alipay.muagent.model.ekg.storage.GraphUpdateRequest;
import com.alipay.muagent.service.ekgmanager.EkgGraphManager;
import com.alipay.muagent.service.ekgmanager.EkgGraphStorageClient;
import com.alipay.muagent.util.MapUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

/**
 * @author jikong
 * @version EkgGraphManagerImpl.java, v 0.1 2024年10月11日 19:39 jikong
 */
@Service
public class EkgGraphManagerImpl implements EkgGraphManager {
    @Autowired
    private EkgGraphStorageClient ekgGraphStorageClient;
    /**
     * 将teamId转换为团队根节点ID
     *
     * @param teamId
     * @return
     */
    @Override
    public String formatTeamRootNodeId(String teamId) {return "ekg_team_" + teamId;}

    /**
     * 根据团队ID查询图谱(外层图谱)
     *
     * @param teamId
     * @return
     */
    @Override
    public GraphGraph getGraphByTeam(String teamId) {
        String teamRootId = formatTeamRootNodeId(teamId);
        GraphGraph graph = ekgGraphStorageClient.getGraphByTeam(teamRootId);

        // 强制保证有团队根节点
        if (graph.getNodes() == null || graph.getNodes().isEmpty()) {
            GraphUpdateRequest request = new GraphUpdateRequest();
            request.setTeamId(teamId);
            request.setRootNodeId(teamRootId);
            request.setOldGraph(graph);

            LinkedList<GraphNode> nodes = new LinkedList<>();
            GraphNode node = new GraphNode();
            node.setId(teamRootId);
            node.setType(EkgNodeType.Intent.getCode());
            node.setAttributes(MapUtil.from(HashMap<String, Object>::new)
                    .put("name", "开始")
                    .put("description", "团队起始节点")
                    .put("teamids", teamId)
                    .put("isTeamRoot", true) // 告诉前端 这是团队根节点
                    .value());
            nodes.add(node);
            GraphGraph graph1 = new GraphGraph();
            graph1.setNodes(nodes);
            graph1.setEdges(graph.getEdges() == null ? new LinkedList<>() : graph.getEdges());
            request.setNewGraph(graph1);
            // 插入团队根节点
            updateGraph(request);

            return graph1;
        }

        return graph;
    }

    /**
     * 删除团队下的图谱数据
     *
     * @param teamId
     * @return
     */
    @Override
    public Boolean deleteByTeam(String teamId) {
        GraphUpdateRequest request = new GraphUpdateRequest();
        request.setTeamId(teamId);
        String rootNodeId = formatTeamRootNodeId(teamId);
        request.setRootNodeId(rootNodeId);
        GraphNode node = new GraphNode();
        node.setId(rootNodeId);
        node.setType(EkgNodeType.Intent.getCode());
        GraphGraph graph = new GraphGraph();
        graph.setNodes(Collections.singletonList(node));
        request.setOldGraph(graph);
        return ekgGraphStorageClient.updateGraph(request) != null;
    }

    /**
     * 根据节点ID查询图谱(内层图谱)
     *
     * @param nodeId 节点ID
     * @return 图谱(内层图谱)
     */
    @Override
    public GraphGraph getGraphByNode(String nodeId, String nodeType) {return ekgGraphStorageClient.getGraphByNode(nodeId, nodeType);}

    /**
     * 获取节点详情
     *
     * @param nodeId 节点ID
     * @return 节点详情
     */
    public GraphNode getNode(String nodeId, String nodeType) {return ekgGraphStorageClient.getNode(nodeId, nodeType);}

    /**
     * 更新图谱数据
     *
     * @param request 请求参数
     * @return 是否更新成功
     */
    public GraphGraph updateGraph(GraphUpdateRequest request) {return ekgGraphStorageClient.updateGraph(request);}

    /**
     * 节点搜索
     *
     * @param teamId 团队ID
     * @param text   搜索文本
     * @return 搜索结果
     */
    public List<GraphNode> searchNode(String teamId, String text) {return ekgGraphStorageClient.searchNode(teamId, text);}

    /**
     * 根据节点ID查询祖先链路
     *
     * @param teamId 团队ID
     * @param nodeId 节点ID
     * @return 祖先链路
     */
    public GraphGraph getNodeAncestor(String teamId, String nodeId, String nodeType) {
        return ekgGraphStorageClient.getNodeAncestor(formatTeamRootNodeId(teamId), nodeId, nodeType);
    }

}