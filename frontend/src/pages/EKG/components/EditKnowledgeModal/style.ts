import { styled } from '@umijs/max';
import { Modal } from 'antd';

// 创建知识弹窗
export const EditKnowledgeModalWrapper = styled(Modal)`
  textarea {
    height: 113px;
    resize: none;
  }
  .ant-modal-content,
  .ant-modal-title {
    background: #eceff6;
  }
  .mode-item {
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 16px;
    cursor: pointer;
    .ant-card-body {
      padding: 0;
    }
    .mode-item-title {
      font-size: 14px;
      color: #1c2533;
      font-weight: 600;
    }
    .mode-item-description {
      margin-top: 8px;
      font-size: 14px;
      color: #878c93;
      line-height: 24px;
    }
  }
  .mode-item-active {
    border: 1.6px solid #1b62ff;
  }
`;
