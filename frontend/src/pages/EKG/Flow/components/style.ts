import { styled } from '@umijs/max';
export const SidebarContainer = styled.div`
  padding: 0 16px 13px;

  .title {
    display: flex;
    align-items: center;
    .titleText {
      padding-top: 13px;
      font-size: 16px;
      color: #1c2533;
      font-weight: 600;
      user-select: none;
    }
    .titleIcon {
      font-size: 14px;
      padding-top: 13px;
      cursor: pointer;
      padding-left: 40px;
    }
  }
  .nodeItem {
    cursor: pointer;
    margin-top: 12px;
    background: #ffffff;
    border-radius: 10px;
    width: 120px;
    height: 48px;
    display: flex;
    align-items: center;
    .nodeItem_icon {
      padding: 8px;
    }
    .nodeItem_name {
      font-size: 14px;
    }
  }
`;
export const Container = styled.div`
  .content {
    max-height: 800px;
    overflow: auto;
    position: absolute;
    padding: 16px 16px 36px;
    width: 420px;
    background: #eceff6;
    border: 1px solid #000a1a29;
    border-radius: 12px;
    box-shadow: 0px 9px 28px 8px #0000000d, 0px 6px 16px 0px #00000014,
      0px 3px 6px -4px #0000001f;
    .content_header {
      display: flex;
      align-items: center;
      margin-bottom: 16px;
      font-size: 16px;
      color: #1c2533;
      font-weight: 600;
      .content_header_close {
        margin-left: auto;
        color: #525964;
      }
    }
    .closeInfo {
      z-index: 10000;
      background: #eceff6;
      height: 36px;
      width: 400px;
      top: 763px;
      position: fixed;
      display: flex;
      right: -422px;
      justify-content: center;
      align-items: center;
      color: #1b62ff;
    }
    .content_item {
      background: #ffffff;
      border-radius: 12px;
      .content_title {
        border-bottom: 1px solid #e3e4e6;
        display: flex;
        height: 42px;
        padding: 0 8px;
        align-items: center;
      }
      .content_title_text {
        font-size: 14px;
        color: #1c2533;
        font-weight: 600;
      }
      .content_title_icon {
        margin-left: auto;
      }
    }

    .dec {
      color: #b2b2b2;
      margin: 8px 0 16px;
    }
    .markdown {
      // max-height: 320px;
      margin: 8px 13px;
      font-size: 14px;
      color: #1c2533;
      line-height: 24px;
      min-height: 48px;
      overflow: auto;
    }
  }

  .status {
    width: calc(100% + 40px);
    margin: -12px 0px 12px -12px;
    border-radius: 8px 8px 0 0;
    padding: 0 16px;
    align-items: center;
    display: flex;
    height: 40px;
    background: #f4f4f4;
    color: #ccc;
    .expand {
      margin-left: auto;
      color: #1b62ff;
      font-weight: 600;
    }
  }
  .exe {
    background: #1b62ff19;
    color: #000a1ae3;
  }
  .success {
    background: #edf9ee;
    color: #15b533;
  }
  .error {
    background: #ff4d4f1a;
    color: #ff4d4f;
  }
  .executing {
    background: #e6f7ff;
    color: #51b9ff;
  }
  .title {
    display: flex;
    height: 32px;
    align-items: center;
    margin-bottom: 12px;
    img {
      margin-right: 12px;
    }
  }
  .tool-debug-drawer {
    line-height: 1.6;
    .tool-debug-drawer-item {
      border: 1px solid #e3e4e6;
      background: #fff;
      border-radius: 8px;
      .tool-debug-drawer-item-title {
        padding: 0 8px;
        height: 32px;
        line-height: 30px;
        border-radius: 8px 8px 0 0;
        border-bottom: 1px solid #e3e4e6;
      }
      .tool-debug-drawer-item-content {
        padding: 8px;
      }
    }
    .tool-debug-drawer-item-line {
      height: 24px;
      width: 1px;
      background-color: #d6d8da;
      margin-left: 24px;
    }
  }
`;
