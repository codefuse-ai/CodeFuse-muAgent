import { dataToJson, jsonToData } from '../../utils/format';
import { cloneDeep } from 'lodash';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { message } from 'antd';

const commonError = {
  type: 'json',
  msgId: new Date().getTime(),
  content: {
    output: '会话出错，请重试',
    input: '用户提问',
    costMs: 0,
    role: 'assistant',
    messageType: 'json',
    conversationId: new Date().getTime(),
    status: 'FAILED',
  },
  traceId: new Date().getTime(),
  chatResultTypeCode: 'cover',
  streamingDisplay: false,
};

export const ssePost = async (
  url: string,
  paramValues: any,
  propsObj: {
    setLoading: (values: any) => void;
    setMsgList: (values: any) => void;
    props_sessionId: string;
  },
) => {
  const ctrl = new AbortController();
  let headers: Record<string, any> = {
    'Content-Type': 'application/json',
  };
  let currentMsg = [];

  fetchEventSource(`${url}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(paramValues),
    openWhenHidden: true,
    signal: ctrl.signal,
    credentials: 'include',
    onopen: async (response) => {
      if (
        response.ok &&
        response.headers.get('content-type') === 'text/event-stream'
      ) {
        return;
      } else {
        // 错误处理
        if (response.status !== 200) {
          switch (response.status) {
            case 500:
              message.error('Internal Server Error');
              propsObj?.setLoading(false);
              propsObj?.setMsgList((pre: any) => {
                const newPre = cloneDeep(pre);
                newPre.pop();
                newPre.push(commonError);
                return newPre;
              });
              return;
            default:
              message.error('状态码非 200');
              propsObj?.setLoading(false);
              propsObj?.setMsgList((pre: any) => {
                const newPre = cloneDeep(pre);
                newPre.pop();
                newPre.push(commonError);
                return newPre;
              });
              return;
          }
        }
        const reader = response?.body?.getReader();
        reader
          ?.read()
          .then(function process({ done, value }) {
            if (done) {
              reader?.cancel();
              ctrl.abort();
              return;
            }
            let valueObject;
            try {
              valueObject = JSON.parse(new TextDecoder().decode(value));
            } catch (err) {
              console.error(err);
              throw new Error('json 解析错误');
            }
            if (valueObject.success) {
              throw new Error('reaponse 非 text/event-stream');
            } else {
              throw new Error(valueObject?.topErrorReason?.content);
            }
          })
          .catch((err) => {
            reader?.cancel();
            ctrl.abort();
            message.error(err.message);
          });
      }
    },
    onmessage: async (msg) => {

      if (msg.data !== 'start' && msg.data !== 'end') {
        if (msg.data && jsonToData(msg.data).data[0].type === "role_response") {
          currentMsg.push(jsonToData(msg.data).data[0]);
        } else {
          currentMsg.push(jsonToData(msg.data).data[0]);
        }
      }
      if (msg.data === 'end') {
        propsObj?.setMsgList((pre: any) => {
          const newPre = cloneDeep(pre);
          const newData = cloneDeep(currentMsg);
          newPre.pop();
          newPre.push(...newData);
          return newPre;
        });
      }

      else if (msg.event === 'end') {
        ctrl.abort();
      } else if (msg.event === 'error') {
        ctrl.abort();
        message.error('会话出错');
      }
    },
    onclose: () => {
      propsObj?.setLoading(false);
      console.log('close');
      ctrl.abort();
    },
    onerror: (err) => {
      console.error('err', err);
      propsObj?.setLoading(false);
      propsObj?.setMsgList((pre: any) => {
        const newPre = cloneDeep(pre);
        newPre.pop();
        newPre.push(commonError);
        return newPre;
      });
      ctrl.abort();
      throw err;
    },
  }).then((response) => {
    console.log('response', response)
  })
  return ctrl;
};


// export const ssePost = (
//   url: string,
//   paramValues: any
// ) => {
//   fetch(url, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify(paramValues),
//   })
// }

// export async function ssePost(url, data) {
//   try {
//     // 创建POST请求
//     const response = await fetch(url, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json', // 根据实际情况调整Content-Type
//       },
//       body: JSON.stringify(data),
//     });

//     if (!response.ok) {
//       throw new Error(`Network response was not ok: ${response.statusText}`);
//     }

//     // 获取响应体的可读流
//     const reader = response.body.getReader();
//     const decoder = new TextDecoder('utf-8');

//     // 处理流式响应
//     const processChunk = async () => {
//       const { done, value } = await reader.read();
//       if (done) {
//         console.log('Stream complete',value);
//         return;
//       }
//       const chunk = decoder.decode(value, { stream: true });
//       console.log('Received chunk:', {chunk});
//       processChunk();
//     };

//     await processChunk();
//   } catch (error) {
//     console.error('Error:', error);
//   }
// }