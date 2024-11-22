package com.alipay.muagent.util;

import java.net.InetAddress;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * @author Joshua
 * @version TraceUtil.java v1.0 2024-11-20 20:34
 **/
public class TraceUtil {

    private static final String EMPTY_STRING = "";

    private static final AtomicInteger COUNT = new AtomicInteger(1000);

    private static String processId = null;

    private static String hexIpAddress = "ffffffff";

    static {
        try {
            String ipAddressStr = getInetAddress();
            if (null != ipAddressStr) {
                hexIpAddress = getHexAddress(ipAddressStr);
            }
        } catch (Exception e) {
            /*
             * empty catch
             */
        }
    }

    public static String generateTraceId() {
        return getTraceId(hexIpAddress, System.currentTimeMillis(), getNextId());
    }

    private static String getTraceId(String ip, long timeStamp, int nextId) {
        return ip + timeStamp + nextId + getProcessId();
    }

    private static String getProcessId() {
        if (StringUtils.isNotBlank(processId)) {
            return processId;
        }

        String processName = java.lang.management.ManagementFactory.getRuntimeMXBean().getName();

        if (StringUtils.isBlank(processName)) {
            return EMPTY_STRING;
        }

        String[] processSplitName = processName.split("@");

        if (processSplitName.length == 0) {
            return EMPTY_STRING;
        }

        String pid = processSplitName[0];

        if (StringUtils.isBlank(pid)) {
            return EMPTY_STRING;
        }

        processId = pid;
        return pid;
    }

    private static String getHexAddress(String ipAddressStr) {
        final String[] ips = ipAddressStr.split("\\.");
        StringBuilder stringBuilder = new StringBuilder();
        for (String partOfAddress : ips) {
            String hex = Integer.toHexString(Integer.parseInt(partOfAddress));
            if (hex.length() == 1) {
                stringBuilder.append('0').append(hex);
            } else {
                stringBuilder.append(hex);
            }
        }
        return stringBuilder.toString();
    }

    private static String getInetAddress() {
        try {
            return InetAddress.getLocalHost().getHostAddress();
        } catch (Exception e) {
            return null;
        }
    }

    private static int getNextId() {
        while (true) {
            int current = COUNT.get();
            int next = (current > 9000) ? 1000 : current + 1;
            if (COUNT.compareAndSet(current, next)) {
                return next;
            }
        }
    }


}
