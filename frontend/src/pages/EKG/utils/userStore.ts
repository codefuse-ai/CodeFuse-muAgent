import { getUserInfo } from '@/services/user';
let userState: Record<string, any> = {};

export function setGlobalState(state: Record<string, any>) {
  userState = {
    ...userState,
    ...state,
  };
}
export function getGlobalState() {
  return userState;
}

export function getGlobalValueFromKey(key: string) {
  return userState[key];
}

export function getMySpaceId() {
  return getGlobalValueFromKey('spaceId');
}

export function getMyLoginName() {
  return getGlobalValueFromKey('loginName');
}
export function getIsSuperAdmin() {
  return getGlobalValueFromKey('superAdmin');
}

export function getMyEmpId() {
  return getGlobalValueFromKey('empId');
}

export function getMyDeptName() {
  return getGlobalValueFromKey('deptName');
}

// 请求用户数据，如在官网页面，在资源闲置时，提前请求用户数据
// 请求完成后，存放在globalStore中
/**
 * 获取初始的用户信息
 * 并且包含这个用户名下创建的agent空间
 */
export function requestUserInfo(
  successCallback?: (userInfo: Record<string, any>) => void,
  errorCallback?: (errorObj: any) => void,
) {
  const loginName = getMyLoginName();
  // 如果userState中存在用户名，则此时不再请求了，直接返回userState
  if (loginName) {
    successCallback?.(userState);
    return;
  }
  getUserInfo()
    .then((resData) => {
      if (resData.success && resData.data) {
        console.log('请求用户数据成功了', resData.data);
        setGlobalState(resData.data);
        successCallback?.(resData.data);
      } else if (
        resData?.buserviceErrorCode === 'USER_NOT_LOGIN' &&
        resData?.buserviceErrorMsg
      ) {
        let url = new URL(resData.buserviceErrorMsg);
        url.searchParams.set('sourceUrl', window.location.href);
        errorCallback?.({
          type: 'USER_NOT_LOGIN',
          message: `${url.toString()}`,
        });
      } else {
        // 接口状态200，但是数据返回异常
        errorCallback?.({
          type: 'REQUEST_OK',
          message: resData.errorMessage,
        });
      }
    })
    .catch((e) => {
      // 接口状态异常
      errorCallback?.({
        type: 'REQUEST_BAD',
        message: e.message,
      });
    });
}
