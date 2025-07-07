import CryptoJS from "crypto-js";
import * as base64 from "base-64";

// Websocket配置
interface WSConfig {
  APPID: string;
  APISecret: string;
  APIKey: string;
  VERSION: string;
}

// 根据版本指定访问的领域
const vDomain: { [key: string]: string } = {
  "v1.1": "general",
  "v2.1": "generalv2",
  "v3.0": "generalv3",
  "v3.5": "generalv3.5",
  "v4.0": "4.0Ultra",
};

// 会话项
export interface ChatItem {
  /** 会话角色：user表示是用户的问题，assistant表示AI的回复 */
  role: "user" | "assistant";
  /** 用户和AI的对话内容,所有content的累计tokens需控制8192以内 */
  content: string;
  index?: number;
  [key: string]: any; // 允许包含额外的属性
}

export interface WSReqParams {
  /** header部分 */
  header: {
    /** 应用appid，从开放平台控制台创建的应用中获取（必传） */
    app_id: string;
    /** 每个用户的id，用于区分不同用户（非必传） */
    uid?: string;
  };
  /**parameter部分 */
  parameter: {
    chat: {
      /**指定访问的领域 */
      domain: string;
      /**模型回答的tokens的最大长度:V1.5取值为[1,4096],V2.0取值为[1,8192]，默认为2048。V3.0取值为[1,8192]，默认为2048。 */
      max_tokens?: number;
    };
  };
  /**payload部分：请求加载数据块 */
  payload: {
    message: {
      text: ChatItem[];
    };
  };
}

export interface WSResParams {
  /** 协议头部，用于描述平台特性的参数 */
  header: {
    code: number;
    message: string;
    /** 本次会话的id */
    sid: string;
    /** 数据状态 0:start，1:continue，2:end */
    status: number;
  };
  /** 响应数据块:数据段，携带响应的数据 */
  payload: {
    choices: {
      /** 数据状态 0:start，1:continue，2:end */
      status: number;
      /** 数据序号，标明数据为第几块。最小值:0, 最大值:9999999 */
      seq: number;
      /** 文本数据 */
      text: ChatItem[];
    };
    usage: {
      text: {
        /**	问题的Tokens大小 */
        question_tokens: number;
        /**	包含历史问题的总Tokens大小 */
        prompt_tokens: number;
        /** 回答的Token大小 */
        completion_tokens: number;
        /**	promptTokens和completionTokens的和，也是本次交互计费的Tokens大小 */
        total_tokens: number;
      };
    };
  };
}

/**
 * 鉴权URL生成
 * @param  config  配置信息
 * @returns url 鉴权URL
 */
export const getWebsocketUrl = (config: WSConfig): string => {
  //
  let url = `wss://spark-api.xf-yun.com/v1/x1`;
  let host = window.location.origin;
  let apiKeyName = "api_key";

  let date = new Date().toUTCString();
  //加密算法，hmac是基于哈希算法的消息认证码算法，用于验证一个消息是否被篡改--如网站上传递email，
  //接收时可以通过hmac(email) 或者email 是否是用户伪造的
  let algorithm = "hmac-sha256";
  //参与签名的参数，固定的参数名为host date request-line，而非这些参数的值
  let headers = "host date request-line";

  // signature
  let signatureOrigin = `host: ${host}\ndate: ${date}\nGET /${config.VERSION}/x1 HTTP/1.1`; //原始签名
  //hmac是基于哈希算法的消息认证码算法，CryptoJS 是为js提供了各种各样的加密算法
  //1.直接使用，引入js文件，2. 安装依赖：npm install crypto-js,导入：import CryptoJS from "crypto-js"
  let signatureSha = CryptoJS.HmacSHA256(signatureOrigin, config.APISecret);
  let signature = CryptoJS.enc.Base64.stringify(signatureSha);

  // 授权参数组成
  let authorizationOrigin = `${apiKeyName}="${config.APIKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`;

  // authorization参数(base64编码的签名信息)生成
  // 安装：npm install base-64 导入：import * as base64 from "base-64"
  let authorization = base64.encode(authorizationOrigin);
  //encodeURI(date): 把日期字符串作为URI（统一资源标识符） 进行编码
  url = `${url}?authorization=${authorization}&date=${encodeURI(
    date
  )}&host=${host}`;

  console.log("url:" + url);
  console.log("domain:" + vDomain[config.VERSION]);
  return url;
};

/**
 * 发送数据格式化
 * @param sendData
 * @param sendData
 * @returns (数据结构注解可参考本文件中interface WSReqParams)
 */
export const wsSendMsgFormat = (config: WSConfig, sendData: ChatItem[]) => {
  const formatData = {
    header: {
      app_id: config.APPID,
    },
    parameter: {
      chat: {
        domain: "x1",
        max_tokens: 1024,
      },
    },
    payload: {
      message: {
        text: sendData,
      },
    },
  };

  return formatData;
};
