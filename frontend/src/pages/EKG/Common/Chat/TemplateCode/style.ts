import { styled } from '@umijs/max';

export const CodeWrapper = styled.div`
  .code_less p:last-child {
    margin-bottom: 0;
  }
  .hljs {
    margin-bottom: 0;
  }
  .code_less {
    padding: 6px;
    display: block !important;
  }
  .hljs {
    border-radius: 6px;
  }
  .code_less {
    thead {
      background-color: rgb(244, 245, 245);
    }
    td,
    th {
      border: 1px solid rgb(231, 233, 232);
      padding: 8px;
    }
    p:first-child {
      margin-top: 0;
    }
    p:last-child {
      margin-bottom: 0;
    }
  }

  .templateCodeCustom {
    .ant-collapse {
      border-radius: 6px;
    }
    .ant-collapse-header {
      padding: 6px 8px !important;
    }
    .ant-collapse-content-box {
      padding: 0 !important;
    }
  }
`;
