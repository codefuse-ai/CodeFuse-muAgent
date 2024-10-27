import { getMySpaceId } from './userStore';
import { message } from 'antd';

export function trim(str: string) {
  return str.trim();
}
export function querySpaceId() {
  const str = location.pathname;
  const secondSlashIndex = str.indexOf('/', str.indexOf('/') + 1);
  const thirdSlashIndex = str.indexOf('/', secondSlashIndex + 1);
  const extractedNumber = str.slice(secondSlashIndex + 1, thirdSlashIndex);
  return extractedNumber;
}

export function isPersonalSpace() {
  return querySpaceId() === getMySpaceId();
}

/**
 * 复制
 * @param str
 */
export const copyCodeFromData = (str: string) => {
  const textarea = document.createElement('textarea');
  textarea.value = str;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  message.success('复制成功');
};

/**
 * 图片链接转换为base64
 * @param url
 * @returns
 */
export const imgUrlToBase64 = (url?: string) => {
  return new Promise((resolve, reject) => {
    if (!url) {
      reject('图片链接为空');
      return;
    }
    const image = new Image();
    // 允许跨域获取图片资源
    image.crossOrigin = 'Anonymous';
    image.onload = function () {
      // 创建canvas
      const canvas = document.createElement('canvas');
      // 获取canvas的2D上下文
      const ctx = canvas.getContext('2d');
      // 设定canvas的宽高为图片的宽高
      canvas.height = image.height;
      canvas.width = image.width;
      // 将图片画到canvas上
      ctx?.drawImage(image, 0, 0);
      // 转换为Base64格式
      const dataUrl = canvas.toDataURL('image/png');
      resolve(dataUrl);
      // 清理canvas资源
      canvas.remove();
    };
    // 如果图片加载失败
    image.onerror = (error) => reject(error);
    // 设置image对象的源为提供的URL
    image.src = url;
  });
};

/**
 * 图片文件类型转换为base64格式
 * @param file
 */
export const fileTransformBase64 = (file: File) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

/**
 * 保存知识库文档前的参数处理
 * @param params
 */
export const handleSaveFormatParams = (props: {
  knowledgeDocs?: Array<API.YuQueBookInfo>;
  treeCheckedDocKeys: string[];
  knowledgeId?: string;
  groupLogin?: string;
  syncType?: string;
  groupName?: string;
}) => {
  const {
    knowledgeDocs,
    treeCheckedDocKeys,
    knowledgeId,
    groupLogin,
    groupName,
    syncType,
  } = props;
  // 将选中的文档进行对应知识库进行分组
  const temp: any = {};
  knowledgeDocs?.forEach((item) => {
    // 知识库id作为key，其中文档选中keys作为value
    temp[item?.bookSlug as string] = [];
    item.docs?.forEach((el) => {
      // 有选中的就加入进去
      if (treeCheckedDocKeys.includes(el?.docSlug as string)) {
        temp[item?.bookSlug as string] = temp[item?.bookSlug as string].concat(
          el?.docSlug as string,
        );
      }
    });
  });
  // 组装参数books
  const books: any[] = [];
  Object.keys(temp)?.forEach((item) => {
    if (temp[item]?.length > 0) {
      books.push({ bookSlug: item, docs: temp[item] });
    }
  });
  // 参数
  const params: API.YuQueSpaceRequest = {
    knowledgeBaseId: knowledgeId,
    groups: [
      {
        groupLogin,
        books,
        groupName: syncType === 'RAG' ? groupName : undefined,
      },
    ],
  };
  return params;
};

/**
 * 节点输入参数转换，引用id拼接
 */
export const handleNodeInputFormat = (values?: any[]) => {
  // 转换为后端使用的数据
  const input_params: any = {};
  values?.forEach(
    (item: { key: string; value: string | string[]; valueType: string }) => {
      // 引用类型，value是数组，需要进行拼接
      if (item?.valueType === 'quote' && item?.value?.length > 0) {
        const curArr = item?.value?.slice(-2);
        input_params[item.key] = `$context.${(curArr as string[])?.join('--')}`;
      } else {
        input_params[item.key] = item.value;
      }
    },
  );
  return input_params;
};

/**
 * 数据输出为json字符串,可作为条件判断使用
 * @param data - 要转换为 JSON 字符串的数据，可以是对象或数组。
 * @param type - 指定数据的类型，'obj' 表示对象，'arr' 表示数组。根据此参数，函数可能返回不同的默认值。
 * @returns 返回一个对象，包含以下属性：
 *   - data: 转换后的 JSON 字符串。如果转换失败，返回一个空数组或空对象，具体取决于 type 参数。
 *   - flag: 布尔值，指示转换是否成功。如果转换成功，则为 true；否则为 false。
 */
export const dataToJson = (data: any, type: 'obj' | 'arr' = 'obj') => {
  if (!data) return { data: type === 'arr' ? [] : {}, flag: false };
  try {
    const result = JSON.stringify(data);
    return {
      data: result,
      flag: result === '{}' || result === '[]' ? false : true,
    };
  } catch (e) {
    console.warn(`json解析出错${e}`);
    return {
      data: type === 'arr' ? [] : {},
      flag: false,
    };
  }
};

/**
 * 字符串解析为数据,可作为条件判断使用
 * @param str - 字符串
 * @returns 返回一个对象，包含以下属性：
 *   - data: 转化后的数据。如果转换失败，返回原字符串或者空字符，兼容undefined等情况。
 *   - flag: 布尔值，指示转换是否成功。如果转换成功，则为 true；否则为 false。
 */
export const jsonToData = (str: string) => {
  if (!str) return { data: str || '', flag: false };
  try {
    const result = JSON.parse(str);
    return {
      data: result,
      flag:
        JSON.stringify(result) === '{}' || JSON.stringify(result) === '[]'
          ? false
          : true,
    };
  } catch (e) {
    console.warn(`json解析出错${e}`);
    return {
      data: str || '',
      flag: false,
    };
  }
};

/**
 * 复制文本
 * @param text - 字符串
 * @returns
 */
export const copyText = (text: string) => {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  message.info('复制成功');
};
