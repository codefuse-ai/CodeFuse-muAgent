import { styled } from '@umijs/max';

export const StartNodeWrapper = styled.div`
  .node-circle {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background-image: linear-gradient(180deg, #ffbf1a 0%, #ff8216 100%);
    font-size: 16px;
    color: #ffffff;
    position: relative;
    .node-circle-label {
      font-weight: 600;
    }
    .node-circle-handle-dot {
      width: 4px;
      height: 4px;
      background: #fff;
      border: 1px solid #1b62ff;
      left: 50%;
      top: 50%;
    }
    .node-circle-handle-dot:hover {
      width: 16px;
      height: 16px;
      background-image: url('https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*HjOMRJveUSAAAAAAAAAAAAAADprcAQ/original');
      background-position: center;
    }
  }
  .node-title {
    width: 120px;
    position: absolute;
    top: 68px;
    font-size: 12px;
    color: #000a1ae3;
    text-align: center;
  }
  .ant-menu {
    font-size: 14px;
    border-radius: 12px;
    padding: 4px;
    .ant-menu-item {
      height: 36px;
      text-align: center;
      padding: 0 4px;
      color: #000000e0;
      font-weight: 400;
    }
  }
`;
