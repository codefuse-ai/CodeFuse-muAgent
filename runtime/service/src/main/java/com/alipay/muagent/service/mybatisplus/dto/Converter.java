package com.alipay.muagent.service.mybatisplus.dto;

import java.util.function.Function;

/**
 * @author chenjue.wwp
 * @version : LocalToolLoader.java, v 0.1 2024年12月10日 下午7:23 chenjue.wwp Exp $
 */
public class Converter<T, U> {

    private final Function<T, U> fromDto;
    private final Function<U, T> fromEntity;

    /**
     * @param fromDto entity function
     * @param fromEntity domain function
     */
    public Converter(final Function<T, U> fromDto, final Function<U, T> fromEntity) {
        this.fromDto = fromDto;
        this.fromEntity = fromEntity;
    }

    /**
     * @param dto DTO entity
     * @return T -> U
     */
    public final U convertFromDto(final T dto) {
        if (dto == null) {
           throw new RuntimeException("dto is null");
        }
        return fromDto.apply(dto);
    }

    /**
     * @param entity domain entity
     * @return U -> T
     */
    public final T convertFromEntity(final U entity) {
        if (entity == null) {
            throw new RuntimeException("entity is null");
        }
        return fromEntity.apply(entity);
    }

}