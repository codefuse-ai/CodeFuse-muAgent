import { styled } from '@umijs/max';
export const Container = styled.div`
  width: 380px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 9px 28px 8px #0000000d, 0px 6px 16px 0px #00000014,
    0px 3px 6px -4px #0000001f;
  .header {
    display: flex;
    align-items: center;
    height: 64px;
    border-bottom: 1px solid #000a1a1c;
    .close {
      display: flex;
      align-items: center;
      cursor: pointer;
      border-right: 1px solid #000a1a1c;
      font-size: 16px;
      width: 61px;
      height: 25px;
      padding-left: 29px;
    }
    .icon {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      margin: 0 6px 0 12px;
    }
    .title {
      margin-left: 12px;
      font-size: 16px;
      color: #1c2533;
      font-weight: 600;
    }
    .save {
      margin: 0 16px 0 auto;
      .save-button {
        border: none;
        background-image: linear-gradient(120deg, #3595ff 12%, #185cff 98%);
        border-radius: 8px;
      }
    }
  }
  .content {
    padding: 24px 24px 2px;
  }
`;
export const FlowWrapperDrawer = styled.div`
  max-height: 200;
  overflow: hidden;
  .flowWrapper {
    position: relative;
    border-radius: 8px;
    height: 200px;
  }
  .flowWrapper:hover {
    .flowMask {
      display: flex;
    }
  }
  .flowMask {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 200px;
    text-align: center;
    display: none;
    background: #000a1a78;
    border-radius: 8px;
    cursor: pointer;
    color: #fff;
    justify-content: center;
    align-items: center;
  }
`;

export const SceneModalInfoWrapper = styled.div`
  .sceneModal {
    .ant-modal-header {
      background: #eceff6;
    }
    .ant-modal-content {
      background: #eceff6;
    }
    .tagItem {
      width: 100%;
      height: 40px;
      background: #ffffff;
      border-radius: 8px;
      margin: 6px 0;
      cursor: pointer;
      padding: 0 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      &:hover {
        background: #000a1a0a;
      }
      .tagIcon {
        border-radius: 8px;
        padding: 4px 8px;
        &:hover {
          background: #000a1a12;
        }
      }
    }
  }
`;
