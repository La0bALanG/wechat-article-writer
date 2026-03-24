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

class JimengImageToImageGenerator:
    def __init__(self, access_key: str = None, secret_key: str = None):
        """
        初始化即梦图生图3.0生成器
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

        print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 开始请求图生图智能参考生图任务...")
        r = requests.post(request_url, headers=headers, data=req_body)
        
        if r.status_code != 200:
            print(f"❌ HTTP 请求失败，状态码: {r.status_code}")
            print(f"返回详情: {r.text}")
            
        try:
            return r.json()
        except Exception:
            return None

    def generate_image(self, image_urls: list, prompt: str, scale: float = 0.5, width: int = 1024, height: int = 1024) -> list:
        """
        调用图生图接口生成图片，返回图片链接地址列表
        :param image_urls: 参考图 URL 列表（通常只需输入1张图片）
        :param prompt: 编辑图像的提示词
        :param scale: 文本描述影响的程度，默认 0.5。范围[0, 1]
        :param width: 图片宽度
        :param height: 图片高度
        :return: 包含生成的图片 URL 字符串列表
        """
        import time
        # 1. 提交任务
        submit_query_params = {
            'Action': 'CVSync2AsyncSubmitTask',
            'Version': '2022-08-31',
        }
        submit_query = self._format_query(submit_query_params)

        submit_body_params = {
            "req_key": "jimeng_i2i_v30",
            "image_urls": image_urls,
            "prompt": prompt,
            "seed": -1,  # -1 为随机种子
            "scale": scale,
            "width": width,
            "height": height
        }
        submit_body = json.dumps(submit_body_params)
        
        submit_resp = self._sign_v4_request(submit_query, submit_body)

        if not submit_resp or submit_resp.get("code") != 10000:
            print(f"❌ 任务提交失败！返回值: {submit_resp}")
            return []
            
        task_id = submit_resp['data']['task_id']
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 任务提交成功，任务ID: {task_id}")

        # 2. 轮询结果
        query_params = {
            'Action': 'CVSync2AsyncGetResult',
            'Version': '2022-08-31',
        }
        formatted_query = self._format_query(query_params)

        req_json_str = json.dumps({
            "return_url": True,
            "logo_info": {
                "add_logo": False
            }
        })

        query_body_params = {
            "req_key": "jimeng_i2i_v30",
            "task_id": task_id,
            "req_json": req_json_str
        }
        query_body = json.dumps(query_body_params)

        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ 开始轮询等待图片生成...")

        while True:
            query_resp = self._sign_v4_request(formatted_query, query_body)
            if not query_resp or query_resp.get("code") != 10000:
                print(f"❌ 查询任务失败！返回值: {query_resp}")
                return []
                
            status = query_resp['data']['status']
            
            if status == "done":
                # 任务处理完成
                response_image_urls = query_resp['data'].get('image_urls', [])
                image_urls_result = []
                for url in response_image_urls:
                    image_urls_result.append(url.replace('\\u0026', '&'))
                return image_urls_result
                
            elif status in ["in_queue", "generating"]:
                # 任务还在处理中，休息 3 秒再查
                print(".", end="", flush=True)
                time.sleep(3)
                
            elif status in ["not_found", "expired"]:
                print(f"\n❌ 任务未找到或已过期: {status}")
                return []
                
            else:
                print(f"\n❓ 未知状态: {status}")
                return []


if __name__ == "__main__":
    import argparse

    # 命令行参数解析
    parser = argparse.ArgumentParser(description="调用即梦图生图API，基于参考图+提示词生成新图片并保存到本地")
    parser.add_argument("--image_url", type=str, required=True, help="参考图的URL地址（必须是可公开访问的图片链接）")
    parser.add_argument("--prompt", type=str, required=True, help="编辑图像的提示词，例如 '背景换成演唱会现场，平面设计风格'")
    parser.add_argument("--output", type=str, required=True, help="图片保存的本地相对/绝对路径，包含文件名（例如 output.png）")
    parser.add_argument("--scale", type=float, default=0.5, help="文本描述影响程度，范围 [0, 1]，默认 0.5")
    parser.add_argument("--width", type=int, default=1024, help="生成图片宽度，默认 1024")
    parser.add_argument("--height", type=int, default=1024, help="生成图片高度，默认 1024")

    args = parser.parse_args()

    # 实例化调用类，自动从 .env 中读取 VOLC_ACCESS_KEY 和 VOLC_SECRET_KEY
    generator = JimengImageToImageGenerator()

    # 打印执行信息
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎬 开始执行图生图...")
    print(f"- 参考图 (Image URL): {args.image_url}")
    print(f"- 提示词 (Prompt): {args.prompt}")
    print(f"- 文本影响度 (Scale): {args.scale}")
    print(f"- 输出尺寸: {args.width}x{args.height}")
    print(f"- 目标路径 (Output): {args.output}")

    # 调用图生图接口
    result_urls = generator.generate_image(
        image_urls=[args.image_url],
        prompt=args.prompt,
        scale=args.scale,
        width=args.width,
        height=args.height
    )

    # 获取数据并下载
    if result_urls:
        image_url = result_urls[0]
        print(f"\n✅ 生成成功！图片下载链接为：\n{image_url}")

        # 将图片保存到指定目录
        try:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ 正在打包下载保存到本地...")
            img_response = requests.get(image_url, stream=True)
            img_response.raise_for_status()

            # 若给出的路径涉及多层文件夹，则自动创建父文件夹
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
        print("\n❌ 未返回图片链接。")

