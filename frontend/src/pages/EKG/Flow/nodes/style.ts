import { styled } from '@umijs/max';
export const NodeContainer = styled.div`
  padding: 12px;
  width: 420px;
  min-height: 166px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 3px 6px -4px #0000001f;
  .ant-collapse-header {
    padding: 12px !important ;
    margin-bottom: 10px;
  }
  .ant-collapse-content {
    min-height: 120px;
  }
  .summarize-switch {
    display: flex;
    padding: 0 12px;
    margin: 12px 0;
    align-items: center;
    justify-content: space-between;
    background: #000a1a0a;
    border-radius: 8px;
    width: 100%;
    height: 40px;
    font-size: 14px;
    color: #1c2533;
    font-weight: 600;
  }
`;
