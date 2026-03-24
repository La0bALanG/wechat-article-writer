import json
import os
import base64
import datetime
import hashlib
import hmac
import requests
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class JimengTextToImageGenerator:
    def __init__(self, access_key: str = None, secret_key: str = None):
        """
        初始化即梦文生图生成器
        :param access_key: 您的 AK（若不传则从环境变量 VOLC_ACCESS_KEY 中读取）
        :param secret_key: 您的 SK（若不传则从环境变量 VOLC_SECRET_KEY 中读取）
        """
        self.access_key = access_key or os.environ.get("VOLC_ACCESS_KEY")
        self.secret_key = secret_key or os.environ.get("VOLC_SECRET_KEY")
        
        if not self.access_key or not self.secret_key:
            raise ValueError('请在参数中指定 AK/SK 或在 .env 文件中配置 VOLC_ACCESS_KEY 和 VOLC_SECRET_KEY')

        self.method = 'POST'
        self.host = 'visual.volcengineapi.com'
        self.region = 'cn-north-1'
        self.endpoint = 'https://visual.volcengineapi.com'
        self.service = 'cv'

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self._sign(key.encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, 'request')
        return k_signing

    def _format_query(self, parameters):
        request_parameters_init = ''
        for key in sorted(parameters):
            request_parameters_init += key + '=' + str(parameters[key]) + '&'
        return request_parameters_init[:-1]

    def _sign_v4_request(self, req_query, req_body):
        t = datetime.datetime.utcnow()
        current_date = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d') 
        canonical_uri = '/'
        canonical_querystring = req_query
        signed_headers = 'content-type;host;x-content-sha256;x-date'
        payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
        content_type = 'application/json'
        
        canonical_headers = (
            'content-type:' + content_type + '\n' + 
            'host:' + self.host + '\n' + 
            'x-content-sha256:' + payload_hash + '\n' + 
            'x-date:' + current_date + '\n'
        )
        
        canonical_request = (
            self.method + '\n' + 
            canonical_uri + '\n' + 
            canonical_querystring + '\n' + 
            canonical_headers + '\n' + 
            signed_headers + '\n' + 
            payload_hash
        )
        
        algorithm = 'HMAC-SHA256'
        credential_scope = datestamp + '/' + self.region + '/' + self.service + '/request'
        string_to_sign = (
            algorithm + '\n' + 
            current_date + '\n' + 
            credential_scope + '\n' + 
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        )
        
        signing_key = self._get_signature_key(self.secret_key, datestamp, self.region, self.service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        authorization_header = (
            algorithm + ' Credential=' + self.access_key + '/' + credential_scope + 
            ', SignedHeaders=' + signed_headers + 
            ', Signature=' + signature
        )
        
        headers = {
            'X-Date': current_date,
            'Authorization': authorization_header,
            'X-Content-Sha256': payload_hash,
            'Content-Type': content_type
        }

        request_url = self.endpoint + '?' + canonical_querystring

        print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 开始请求生图任务...")
        r = requests.post(request_url, headers=headers, data=req_body)
        r.raise_for_status()
        
        try:
            return r.json()
        except Exception:
            return None

    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> list:
        """
        调用接口生成图片，返回图片链接地址列表
        :param prompt: 提示词
        :param width: 图片宽度
        :param height: 图片高度
        :return: 包含生成的图片 URL 字符串列表
        """
        query_params = {
            'Action': 'CVProcess',
            'Version': '2022-08-31',
        }
        formatted_query = self._format_query(query_params)

        body_params = {
            "req_key": "jimeng_t2i_v31",
            "prompt": prompt,
            "seed": -1,  # -1 为随机种子
            "width": width,
            "height": height,
            "return_url": True,
            "logo_info": {
                "add_logo": False
            }
        }
        formatted_body = json.dumps(body_params)

        response_data = self._sign_v4_request(formatted_query, formatted_body)

        image_urls_result = []
        if response_data and response_data.get("code") == 10000:
            data = response_data.get("data", {})
            # 直接提取返回的 urls
            image_urls = data.get("image_urls", [])
            for url in image_urls:
                image_urls_result.append(url.replace('\\u0026', '&'))
        else:
            print(f"❌ 生成失败！返回值: {response_data}")

        return image_urls_result


if __name__ == "__main__":
    import argparse
    
    # 增加命令行参数解析
    parser = argparse.ArgumentParser(description="调用即梦文生图API生成图片并保存到本地")
    parser.add_argument("--prompt", type=str, required=True, help="用于生成图像的提示词，例如 'A stunning cover...'")
    parser.add_argument("--output", type=str, required=True, help="图片保存的本地相对/绝对路径，包含文件名（例如 cover.png）")
    # 可以额外多保留个 --api 以防之前部分代码逻辑习惯性传入此参数
    parser.add_argument("--api", type=str, default="gemini", help="指定调用的API（即梦环境默认忽略该项）")

    args = parser.parse_args()

    # 实例化调用类，如果不在参数中传入，会自动从 .env 中读取 VOLC_ACCESS_KEY 和 VOLC_SECRET_KEY
    generator = JimengTextToImageGenerator()

    # 打印一些执行信息
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎬 开始执行文生图，准备按 16:9 (1664x936) 渲染图片...")
    print(f"- 提示词 (Prompt): {args.prompt}")
    print(f"- 目标路径 (Output): {args.output}")

    # 调用生图接口 (对于头图，这里默认指定了 1664 x 936 的 16:9 画幅)
    result_urls = generator.generate_image(prompt=args.prompt, width=1664, height=936)
    
    # 获取数据并下载
    if result_urls:
        image_url = result_urls[0]
        print(f"\n✅ 生成成功！图片下载链接为：\n{image_url}")
        
        # 将图片保存到指定目录
        try:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ 正在打包下载保存到本地...")
            img_response = requests.get(image_url, stream=True)
            img_response.raise_for_status()
            
            # 若给出的路径涉及多层文件夹（例如 scripts/images/cover.png），则自动创建父文件夹
            output_dir = os.path.dirname(os.path.abspath(args.output))
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(args.output, "wb") as f:
                for chunk in img_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            print(f"✨ 完美！图片已成功保存至: {os.path.abspath(args.output)}")
        except Exception as e:
            print(f"❌ 下载或保存图片时出错: {e}")
            
    else:
        print("\n❌ 未返回图片链接，或者接口需要异步拉取 task_id。")