import { styled } from '@umijs/max';

export const EKGFlowContainer = styled.div`
  height: 100vh;
  width: 100vw;
  .react-flow__attribution {
    display: none;
  }
  .custom-controls {
    position: absolute;
    right: 16px !important;
    bottom: 16px !important;
    height: 40px !important;
    pointer-events: auto;
    margin: 0;
    padding: 0;
    box-shadow: none;
  }

  .zoom-containers {
    background: #ffffff;
    border-radius: 12px;
    height: 40px;
    width: 173px;
    display: flex;
    align-items: center;
  }

  .dividing-line {
    width: 1px;
    height: 24px;
    background: #000a1a1a;
  }

  .no-border {
    border-width: 0px;
    .ant-btn-icon {
      width: 16px;
      height: 16px;
    }
  }
  .doc-analysis {
    width: 40px;
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;
    background: #1c2533;
    cursor: pointer;
  }
`;

/**
 * 解析文件内容
 */
export const DocAnalysisWrapper = styled.div`
  width: 344px;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: 186px;
  transition: max-height 0.3s;
  padding: 0 8px;
  margin: 0 4px;
`;
