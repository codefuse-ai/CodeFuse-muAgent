/**
 * Alipay.com Inc.
 * Copyright (c) 2004-2024 All Rights Reserved.
 */
package com.alipay.muagent.util;

import org.slf4j.helpers.MessageFormatter;

/**
 * @author renmao.rm
 * @version : StringUtils.java, v 0.1 2024年10月10日 上午11:25 renmao.rm Exp $
 */
public final class StringUtils {
    public static boolean isBlank(String string) {
        if (isEmpty(string)) {
            return true;
        } else {
            for(int i = 0; i < string.length(); ++i) {
                if (!Character.isWhitespace(string.charAt(i))) {
                    return false;
                }
            }

            return true;
        }
    }

    public static boolean isNotBlank( String string) {
        return !isBlank(string);
    }

    public static boolean isEmpty(String string) {
        return string == null || string.isEmpty();
    }

    public static boolean isNotEmpty(String string) {
        return !isEmpty(string);
    }

    public static String truncate(String string, int maxLength) {
        return string.length() > maxLength ? string.substring(0, maxLength) : string;
    }

    public static String truncate(String string, int maxLength, String truncationIndicator) {
        if (truncationIndicator.length() >= maxLength) {
            throw new IllegalArgumentException("maxLength must be greater than length of truncationIndicator");
        } else if (string.length() > maxLength) {
            int remainingLength = maxLength - truncationIndicator.length();
            return string.substring(0, remainingLength) + truncationIndicator;
        } else {
            return string;
        }
    }

    private StringUtils() {
    }

    public static String stringFormat(String format, Object... args) {
        return MessageFormatter.arrayFormat(format, args).getMessage();
    }
}