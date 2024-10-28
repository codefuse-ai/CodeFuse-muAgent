import React from 'react';
import { Handle, Position } from 'reactflow';
import NodeHeader from '../components/NodeHeader';
import { NodeContainer } from './style';
export default (props: any) => {
  console.log(props, 'props');
  return (
    <NodeContainer style={{ minHeight: 56 }}>
      <NodeHeader moduleData={props} />
      <Handle
        type="source"
        style={{
          width: '12px',
          height: '12px',
          background: '#bdc0c4',
        }}
        id={props?.id || '111'}
        position={Position.Right}
      />
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          height: 56,
          padding: '0 8px',
        }}
      >
        <div>
          <img
            width={32}
            src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*onSLQLtYSzkAAAAAAAAAAAAADprcAQ/original"
          />
        </div>
        <div>{props.data.attributes.name}</div>
      </div>
    </NodeContainer>
  );
};
