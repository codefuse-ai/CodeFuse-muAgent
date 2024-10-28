import { styled, keyframes } from '@umijs/max';

const ripple = keyframes`
  0% {
    box-shadow: 0 0 0 0px rgba(82, 114, 224, 0.3),
      0 0 0 8px rgba(82, 114, 224, 0.15);
  }
  100% {
    box-shadow: 0 0 0 8px rgba(82, 114, 224, 0.3),
      0 0 0 16px rgba(82, 114, 224, 0.15);
  }
`;

export const SceneNodeWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;

  .nodeCircle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    position: relative;
    cursor: pointer;

    .handleWrapper {
      position: absolute;
      &:nth-child(1) {
        right: 0;
        top: 50%;
        transform: translate(50%, -50%);
        .handleDot:hover {
          right: -8px;
        }
      }
      &:nth-child(2) {
        left: 50%;
        bottom: 0;
        transform: translate(-50%, 50%);
        .handleDot:hover {
          bottom: -8px;
        }
      }
      &:nth-child(3) {
        left: 0;
        top: 50%;
        transform: translate(-50%, -50%);
        .handleDot:hover {
          left: -8px;
        }
      }
      &:nth-child(4) {
        left: 50%;
        top: 0;
        transform: translate(-50%, -50%);
        .handleDot:hover {
          top: -8px;
        }
      }
    }
    &:hover .handleDot {
      opacity: 1;
    }
    .handleDot {
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: #fff;
      border: 1px solid #1b62ff;
      cursor: pointer;
      opacity: 0;
      &:hover {
        width: 16px;
        height: 16px;
        background-image: url('https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*HjOMRJveUSAAAAAAAAAAAAAADprcAQ/original');
        background-position: center;
      }
    }
  }
  .showDot {
    opacity: 1 !important;
  }
  .nodeTitle {
    font-size: 12px;
    color: #000a1ae3;
  }
  .menuWrapper {
    position: absolute;
    top: -18px;
    left: -10px;
    transform: scale(0.6);
    ul {
      border-radius: 12px;
    }
    .deleteText {
      background: #000a1a12;
      color: #000a1a78;
      padding: 0 8px;
      border-radius: 8px;
      height: 24px;
      line-height: 24px;
    }
  }

  // 正常节点
  .normalNodeClass {
    background: #5272e0;
    border-radius: 50%;
    .handleDot {
      border-color: blue;
    }
  }
  // 暗淡节点
  .noActionNodeClass {
    background: #afbdee;
    border-radius: 50%;
    .handleDot {
      border-color: #dadce2;
    }
  }
  // 搜索节点
  .searchNodeClass {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    animation: ${ripple} 1s infinite;
    position: relative;
    margin: 8px;
    background: #5272e0;
    .handleDot {
      border-color: blue;
    }
  }
  // 选中节点
  .selectNodeClass {
    background: #5272e0;
    border-radius: 50%;
    .handleDot {
      border-color: blue;
    }
  }
  // 选中的节点背景
  .selectNodeBg {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: #d6ddf3;
    position: absolute;
    z-index: -1;
    transform: translate(-6.5px, -6.5px);
  }
  // loading节点
  .ant-spin-dot-item {
    background: #fff;
  }
`;
