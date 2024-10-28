import { cloneDeep } from 'lodash';
import { DownOutlined, UpOutlined } from '@ant-design/icons';
import React, { useState } from 'react';
import type { XYPosition } from 'reactflow';
import { ChildNodeTemplate } from '../utils/ChildNodeTemplate';
import { SidebarContainer } from './style';
interface Props {
  onAddNode: (node: { template: any; position: XYPosition }) => void;
}
export default (props: Props) => {
  const { onAddNode } = props;
  const [status, setStatus] = useState<boolean>(true); // 节点展开收起

  return (
    <SidebarContainer>
      <div className="title">
        <div className="titleText">添加节点</div>
        <div onClick={() => setStatus(!status)} className="titleIcon">
          {status ? <UpOutlined /> : <DownOutlined />}
        </div>
      </div>
      <div style={{ display: status ? 'block' : 'none' }}>
        {ChildNodeTemplate.list.map((i) => (
          <div
            className="nodeItem"
            draggable
            key={i.type}
            onDragEnd={(e) => {
              try {
                if (e.clientX < 160) return;
                const template = cloneDeep(i);
                onAddNode({
                  template,
                  position: { x: e.clientX, y: e.clientY },
                });
              } catch (error) {
                console.error(error);
              }
            }}
          >
            <div className="nodeItem_icon">
              <img
                width={32}
                src={i.logo}
                style={{ WebkitUserDrag: 'none', UserDrag: 'none' }}
              />
            </div>
            <div className="nodeItem_name">{i.name}</div>
          </div>
        ))}
      </div>
    </SidebarContainer>
  );
};
