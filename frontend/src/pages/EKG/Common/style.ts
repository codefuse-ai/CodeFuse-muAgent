import { styled } from '@umijs/max';

export const ChatWrapper = styled.div`
  position: fixed;
  background: #eceff6;
  border: 1px solid #000a1a29;
  border-radius: 12px;
  box-shadow: 0px 9px 28px 8px #0000000d, 0px 6px 16px 0px #00000014,
    0px 3px 6px -4px #0000001f;
  width: 380px;
  right: 16px;
  top: 100px;
  bottom: 72px;
  z-index: 999;
`;

export const HeaderWrapper = styled.div`
  width: 100%;
  height: 65px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  border-bottom: 1px solid #000a1a1c;
  .headerBtn {
    width: 24px;
    height: 24px;
    background: #ffffff;
    border: 1px solid #000a1a29;
    border-radius: 50%;
    padding: 0;
  }
  .ant-segmented-item {
    background: #000a1a0a;
  }
  .ant-segmented-item-selected {
    background: #ffffff;
  }
  .ant-segmented-item-label {
    height: 32px;
    line-height: 32px;
  }
  .headerIcon {
    width: 24px;
    height: 24px;
    cursor: pointer;
  }
  .ant-space-item {
    padding: 3px 4px;
    border-radius: 8px;
    &:hover {
      background: #eaeaea;
      box-shadow: 0px 9px 28px 8px #0000000d, 0px 6px 16px 0px #00000014,
        0px 3px 6px -4px #0000001f;
    }
  }
`;

export const SelectAgentWrapper = styled.div`
  width: 100%;
  height: calc(100% - 65px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 40px;
  .agentTitle {
    font-size: 16px;
    color: #000000e0;
    line-height: 28px;
    text-align: center;
    font-weight: 600;
  }
  .agentDes {
    font-size: 12px;
    color: #000a1aad;
    line-height: 20px;
    text-align: center;
  }
  .ant-spin-nested-loading {
    width: 100%;
    margin-top: 24px;
  }
  .noSelected {
    margin-top: 24px;
    height: 40px;
    background-image: linear-gradient(97deg, #3595ff 13%, #185cff 100%);
    border-radius: 10px;
    opacity: 0.6;
  }
  .hasSelected {
    margin-top: 24px;
    height: 40px;
    background-image: linear-gradient(97deg, #3595ff 13%, #185cff 100%);
    border-radius: 10px;
  }
`;

export const ChatMainWrapper = styled.div`
  width: 100%;
  height: calc(100% - 65px);
`;
