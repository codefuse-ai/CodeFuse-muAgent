import { styled } from '@umijs/max';

export const ChatContentWrapper = styled.div`
  width: 100%;
  height: calc(100% - 65px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 12px;
`;

export const FooterWrapper = styled.div`
  width: 100%;
  height: 74px;
  .InputMainWrapper {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-direction: column;
    .InputWrapper {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: space-between;
      align-items: end;
      background: #fff;
      .sendInputWrapper {
        flex: 1;
        height: 100%;
        .ant-input {
          height: 100%;
          resize: none;
          border: none;
          &:focus {
            box-shadow: none;
          }
        }
      }
      .sendBtnWrapper {
        width: 36px;
        height: 100%;
        display: flex;
        flex-direction: column-reverse;
        align-items: center;
      }
    }
  }
`;

export const ContentWrapper = styled.div`
  width: 100%;
  flex: 1;
  overflow: auto;
  &::-webkit-scrollbar {
    width: 0px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: #ccc;
    border-radius: 5px;
  }
  &::-webkit-scrollbar-track {
    border-radius: 6px;
  }
  .msg_wrap {
    width: 100%;
    height: auto;
    margin: 18px 0;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
  }
  .user_wrap {
    max-width: calc(100% - 76px);
    word-wrap: break-word;
    background-image: linear-gradient(104deg, #3595ff 13%, #185cff 99%);
    border-radius: 16px 0 16px 16px;
    padding: 12px;
    margin: 0 12px;
    font-size: 14px;
    line-height: 1.5;
  }
  .assistant_wrap {
    max-width: calc(100% - 76px);
    word-wrap: break-word;
    background: #ffffff;
    border-radius: 0px 16px 16px 16px;
    padding: 12px;
    margin: 0 12px;
    font-size: 14px;
    line-height: 1.5;
    overflow-x: auto;
  }
`;
