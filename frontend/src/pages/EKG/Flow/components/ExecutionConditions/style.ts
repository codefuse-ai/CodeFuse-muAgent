import { styled } from '@umijs/max';

/**
 * 条件执行
 */
export const ExecutionConditionsWrapper = styled.div`
  .ant-collapse {
    background: #ffffff;
    .ant-collapse-item {
      background: #000a1a0a;
      border-radius: 8px;
      border: none;
      margin-top: 12px;
    }
    .ant-collapse-content {
      border-top: 1px solid #000a1a1a;
      padding-top: 8px;
      margin: 0 12px;
    }
    .ant-collapse-content-box {
      padding: 12px 0;
    }
    .ant-form-item {
      margin-bottom: 0;
    }
    .ant-radio-group {
      width: 100%;
    }
    .conditions-radio {
      .conditions-radio-item {
        height: 40px;
        background: #ffffff;
        border-radius: 8px;
        padding: 10px 12px;
      }
    }
  }
`;
