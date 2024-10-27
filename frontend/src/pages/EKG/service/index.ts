import { request } from '@umijs/max';
export async function getSreAgentFlow(sessionId: string) {
  return request('/sreAgent/v1/opsconvobus/ekgGraph/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: {
      sessionId,
    },
  });
}
