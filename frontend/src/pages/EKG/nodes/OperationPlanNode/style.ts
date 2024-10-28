import { styled } from '@umijs/max';

export const StartNodeWrapper = styled.div`
  width: 84px;
  height: 45px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;

  /* 定义扩散动画 */
  @keyframes ripple_1 {
    0% {
      box-shadow: 0 0 0 0px rgba(93, 187, 48, 0.3),
        0 0 0 6px rgba(93, 187, 48, 0.15);
    }
    100% {
      box-shadow: 0 0 0 6px rgba(93, 187, 48, 0.3),
        0 0 0 12px rgba(93, 187, 48, 0.15);
    }
  }
  @keyframes ripple_2 {
    0% {
      box-shadow: 0 0 0 0px rgba(125, 132, 142, 0.3),
        0 0 0 6px rgba(125, 132, 142, 0.15);
    }
    100% {
      box-shadow: 0 0 0 6px rgba(125, 132, 142, 0.3),
        0 0 0 12px rgba(125, 132, 142, 0.15);
    }
  }
  /* 应用动画到元素 */
  .container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
  }
  .greenContainer {
    animation: ripple_1 1s linear infinite;
  }
  .greyContainer {
    animation: ripple_2 1s linear infinite;
  }
  .node-circle {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    font-size: 16px;
    color: #ffffff;
    font-weight: 600;
    position: relative;
    .node-circle-handle-dot {
      width: 4px;
      height: 4px;
      background: #fff;
      border: 1px solid #1b62ff;
      left: 50%;
      top: 50%;
    }
  }
  .node-circle :hover {
    .node-circle-handle-dot {
      visibility: hidden;
    }
  }
  .node-title {
    max-width: 150px;
    position: absolute;
    top: 28px;
    font-size: 12px;
    color: #000a1ae3;
    text-align: center;
  }
  .ant-menu {
    width: 172px;
    font-size: 14px;
    border-radius: 12px;
    padding: 4px;
    font-weight: normal;
    .ant-menu-item {
      height: 36px;
      padding: 0 4px;
    }
  }
  .delete {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #ff4d4f;
    .tag {
      display: flex;
      justify-content: center;
      align-items: center;
      background: #000a1a12;
      height: 24px;
      font-size: 12px;
      border-radius: 6px;
      padding: 2px 6px;
      color: #000a1a78;
    }
  }
  .ant-menu li:last-child:hover {
    background: #f5222d1a !important;
  }
`;
