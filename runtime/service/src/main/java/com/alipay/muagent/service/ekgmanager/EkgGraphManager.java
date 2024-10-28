/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.service.ekgmanager;

import com.alipay.muagent.model.ekg.storage.GraphGraph;
import com.alipay.muagent.model.ekg.storage.GraphNode;
import com.alipay.muagent.model.ekg.storage.GraphUpdateRequest;

import java.util.List;

/**
 * EKG底层存储操作管理
 *
 * @author jikong
 * @version EkgGraphManager.java, v 0.1 2024年10月11日 19:22 jikong
 */
public interface EkgGraphManager {
    /**
     * 将teamId转换为团队根节点ID
     *
     * @param teamId
     * @return
     */
    String formatTeamRootNodeId(String teamId);

    /**
     * 根据团队ID查询图谱(外层图谱)
     *
     * @param teamId
     * @return
     */
    GraphGraph getGraphByTeam(String teamId);

    /**
     * 删除团队下的图谱数据
     *
     * @param teamId
     * @return
     */
    Boolean deleteByTeam(String teamId);

    /**
     * 根据节点ID查询图谱(内层图谱)
     *
     * @param nodeId 节点ID
     * @return 图谱(内层图谱)
     */
    GraphGraph getGraphByNode(String nodeId, String nodeType);

    /**
     * 获取节点详情
     *
     * @param nodeId 节点ID
     * @return 节点详情
     */
    GraphNode getNode(String nodeId, String nodeType);

    /**
     * 更新图谱数据
     *
     * @param request 请求参数
     * @return 是否更新成功
     */
    GraphGraph updateGraph(GraphUpdateRequest request);

    /**
     * 节点搜索
     *
     * @param teamId 团队ID
     * @param text   搜索文本
     * @return 搜索结果
     */
    List<GraphNode> searchNode(String teamId, String text);

    /**
     * 根据节点ID查询祖先链路
     *
     * @param teamId 团队ID
     * @param nodeId 节点ID
     * @return 祖先链路
     */
    GraphGraph getNodeAncestor(String teamId, String nodeId, String nodeType);
}