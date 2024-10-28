import { request } from '@umijs/max';

// 获取用户个人信息
export async function getUserInfo() {
  return request('/user/getCurrentUser.json', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
}
