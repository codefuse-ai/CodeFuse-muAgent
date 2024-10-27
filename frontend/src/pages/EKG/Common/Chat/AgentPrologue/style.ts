import { styled } from '@umijs/max';

export const AgentPrologueWrapper = styled.div`
  width: 100%;
  height: 100%;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  .agent_dec {
    width: 100%;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    -webkit-line-clamp: 2;
    font-size: 14px;
    padding: 0 12px;
  }
  .agent_questionSample {
    width: 100%;
    height: auto;
    padding: 14px 24px;
    margin: 14px 0;
    background: #fff;
    border-radius: 16px;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    -webkit-line-clamp: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
`;
