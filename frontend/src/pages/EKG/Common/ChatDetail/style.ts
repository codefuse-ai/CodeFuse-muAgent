import { styled } from '@umijs/max';

export const ChatDetailWrapper = styled.div`
  width: 100%;
  height: calc(100% - 65px);
  .detailListWrapper {
    height: 100%;
    overflow: auto;
  }
  .detailCol {
    width: 100%;
    padding: 4px 12px;
    cursor: pointer;
    .dec {
      flex: 1;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }
  .detailResultWrapper {
    padding: 12px;
    .startNodeIcon {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background-image: linear-gradient(180deg, #ffbf1a 0%, #ff8216 100%);
    }
    .opsgptkgIntentIcon {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #5272e0;
    }
    .opsgptkgScheduleIcon {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #5dbb30;
    }
  }
`;
