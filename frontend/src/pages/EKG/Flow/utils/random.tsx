import { customAlphabet } from 'nanoid';

export function createWorkflowRandom() {
  return customAlphabet(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    32,
  )(); //随机生成节点id
}
