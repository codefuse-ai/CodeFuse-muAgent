import { styled } from '@umijs/max';
/**
 * 编排头部
 */
export const EKGHeaderWrapper = styled.div`
  height: 56px;
  padding: 0 16px;
  background: #f5f7fa;
  border: 1px solid #ffffffcd;
  border-radius: 12px;
  user-select: none;
  .header-title {
    font-size: 16px;
    color: #1c2533;
    font-weight: 600;
  }
  .header-save-tip {
    font-size: 12px;
    color: #000a1a78;
  }
  .header-tab {
    font-size: 20px;
    color: #525964;
    cursor: pointer;
  }
  .header-active-tab {
    color: #1b62ff;
    font-weight: 600;
  }
  .header-children-wrapper {
    width: 320px;
    background-color: #fff;
    padding: 4px 12px;
    border-radius: 10px;
    .header-children-name {
      font-size: 16px;
      color: #000a1ae3;
      font-weight: 600;
      margin: 0 8px;
    }
  }
`;
