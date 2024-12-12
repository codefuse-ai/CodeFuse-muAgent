/*
 * Ant Group
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.web;

import com.alipay.muagent.model.ekg.storage.GraphGraph;
import com.alipay.muagent.model.ekg.storage.GraphNode;
import com.alipay.muagent.model.ekg.storage.GraphUpdateRequest;
import com.alipay.muagent.service.ekgmanager.EkgGraphManager;
import com.alipay.muagent.util.GsonUtils;
import com.alipay.muagent.util.LoggerUtil;
import com.alipay.muagent.web.model.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * @author jikong
 * @version EkgStorageController.java, v 0.1 2024年10月17日 22:10 jikong
 */
@RestController
@RequestMapping("/api/ekg/prod")
public class EkgStorageController {
    private static final Logger LOGGER = LoggerFactory.getLogger(EkgStorageController.class);

    @Autowired
    private EkgGraphManager ekgGraphManager;

    /**
     * 根据团队ID查询图谱(外层图谱)
     *
     * @param teamId 团队ID
     * @return 团队图谱(外层图谱)
     */
    @GetMapping("/graph/team")
    public Result<GraphGraph> getGraphByTeam(@RequestParam("teamId") String teamId) {
        try {
            GraphGraph graphByTeam = ekgGraphManager.getGraphByTeam(teamId);
            return Result.success(graphByTeam);
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "getGraphByTeam 接口异常");
            return Result.fail(e.getMessage());
        }

    }

    /**
     * 根据节点ID查询图谱(内层图谱)
     *
     * @param nodeId 节点ID
     * @return 图谱(内层图谱)
     */
    @GetMapping("/graph/node")
    public Result<GraphGraph> getGraphByNode(@RequestParam("nodeId") String nodeId, @RequestParam("nodeType") String nodeType) {
        try {
            GraphGraph graphByNode = ekgGraphManager.getGraphByNode(nodeId, nodeType);
            return Result.success(graphByNode);
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "getGraphByNode 接口异常");
            return Result.fail(e.getMessage());
        }

    }

    /**
     * 获取节点详情
     *
     * @param nodeId 节点ID
     * @return 节点详情
     */
    @GetMapping("/node")
    public Result<GraphNode> getNode(@RequestParam("nodeId") String nodeId, @RequestParam("nodeType") String nodeType) {
        try {
            return Result.success(ekgGraphManager.getNode(nodeId, nodeType));
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "getNode 接口异常");
            return Result.fail(e.getMessage());
        }
    }

    /**
     * 更新图谱数据
     *
     * @param request 请求参数
     * @return
     */
    @PostMapping("/graph/update")
    public Result<GraphGraph> updateGraph(@RequestBody GraphUpdateRequest request) {
        try {
            LoggerUtil.info(LOGGER, "/graph/update", GsonUtils.toString(request));
            return Result.success(ekgGraphManager.updateGraph(request));
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "updateGraph 接口异常");
            return Result.fail(e.getMessage());
        }
    }

    /**
     * 节点搜索
     *
     * @param teamId 团队ID
     * @param text   搜索文本
     * @return 搜索结果
     */
    @GetMapping("/node/search")
    public Result<List<GraphNode>> searchNode(@RequestParam("teamId") String teamId, @RequestParam("text") String text) {
        try {
            return Result.success(ekgGraphManager.searchNode(teamId, text));
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "searchNode 接口异常");
            return Result.fail(e.getMessage());
        }

    }

    /**
     * 根据节点ID查询祖先链路
     *
     * @param teamId 团队ID
     * @param nodeId 节点ID
     * @return 祖先链路
     */
    @GetMapping("/graph/ancestor")
    public Result<GraphGraph> getNodeAncestor(@RequestParam("teamId") String teamId, @RequestParam("nodeId") String nodeId, @RequestParam("nodeType") String nodeType) {
        try {
            return Result.success(ekgGraphManager.getNodeAncestor(teamId, nodeId, nodeType));
        } catch (Exception e) {
            LoggerUtil.error(LOGGER, e, "getNodeAncestor 接口异常");
            return Result.fail(e.getMessage());
        }
    }
}