import React from 'react';
import ChatContent from './ChatContent';
import ChatFooter from './ChatFooter';
import { ChatContentWrapper } from './style';

const Chat = () => {
  return (
    <ChatContentWrapper>
      <ChatContent />
      <ChatFooter />
    </ChatContentWrapper>
  );
};

export default Chat;
