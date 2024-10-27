import React from 'react';
import { Avatar, Tooltip } from 'antd';
import { AgentPrologueWrapper } from './style';

const AgentPrologue = ({ agent }: any) => {
  return (
    <AgentPrologueWrapper>
      <div
        style={{
          width: '75%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Avatar
          style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
          }}
          src={agent?.avatar}
        />
        <h2 style={{ margin: '12px' }}>
          {agent.agentConfig?.name || agent?.agentName}
        </h2>
        <div className="agent_dec">
          <Tooltip title={agent?.agentDesc}>{agent?.agentDesc}</Tooltip>
        </div>
      </div>
    </AgentPrologueWrapper>
  );
};

export default AgentPrologue;
