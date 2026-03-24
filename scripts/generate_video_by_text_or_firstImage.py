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

class JimengVideoGenerator:
    def __init__(self, access_key: str = None, secret_key: str = None):
        """
        初始化即梦视频3.0Pro生成器 (支持文生视频、图生视频)
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

        print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 发起 API 请求...")
        r = requests.post(request_url, headers=headers, data=req_body)
        
        if r.status_code != 200:
            print(f"❌ HTTP 请求失败，状态码: {r.status_code}")
            print(f"返回详情: {r.text}")
            
        try:
            return r.json()
        except Exception:
            return None

    def generate_video(self, prompt: str = None, image_urls: list = None, frames: int = 121, aspect_ratio: str = "16:9") -> str:
        """
        调用视频生成接口，支持纯文本生成，或文本+图像生成。
        :param prompt: 视频提示词（文本生成时必填，图生视频时可选）
        :param image_urls: 首帧图片的 URL 列表 (列表内仅传1张。传入此值即代表触发图生视频模式)
        :param frames: 帧数。121(对应5秒) 或 241(对应10秒)。
        :param aspect_ratio: 比例。如 "16:9", "4:3", "1:1", "9:16"。纯文本生成时生效，图生视频会自动根据首图截取推断。
        :return: 生成的视频下载链接字符串。失败返回空字符串。
        """
        import time
        if not prompt and not image_urls:
            print("❌ 'prompt' 和 'image_urls' 不能同时为空。至少需要提供一个用于生成视频的内容。")
            return ""

        # 1. 提交任务
        submit_query_params = {
            'Action': 'CVSync2AsyncSubmitTask',
            'Version': '2022-08-31',
        }
        submit_query = self._format_query(submit_query_params)

        submit_body_params = {
            "req_key": "jimeng_ti2v_v30_pro",
            "seed": -1,
            "frames": frames,
            "aspect_ratio": aspect_ratio
        }

        if prompt:
            submit_body_params["prompt"] = prompt
        
        if image_urls:
            submit_body_params["image_urls"] = image_urls
            
        submit_body = json.dumps(submit_body_params)
        
        submit_resp = self._sign_v4_request(submit_query, submit_body)

        if not submit_resp or submit_resp.get("code") != 10000:
            print(f"❌ 任务提交失败！返回值: {submit_resp}")
            return ""
            
        task_id = submit_resp['data']['task_id']
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 任务提交成功，任务ID: {task_id}")

        # 2. 轮询结果
        query_params = {
            'Action': 'CVSync2AsyncGetResult',
            'Version': '2022-08-31',
        }
        formatted_query = self._format_query(query_params)

        # 视频生成轮询可以空 ReqJson（或者传空字典/忽略），文档示例中目前主要是用作打隐形水印等操作
        query_body_params = {
            "req_key": "jimeng_ti2v_v30_pro",
            "task_id": task_id
        }
        query_body = json.dumps(query_body_params)

        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ 视频生成耗时较长，开始轮询等待...")

        while True:
            query_resp = self._sign_v4_request(formatted_query, query_body)
            if not query_resp or query_resp.get("code") != 10000:
                print(f"❌ 查询任务失败！返回值: {query_resp}")
                return ""
                
            status = query_resp['data']['status']
            
            if status == "done":
                print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✨ 视频处理完成！")
                video_url = query_resp['data'].get('video_url', "")
                # 清除常见的 json 转义符
                if video_url:
                    video_url = video_url.replace('\\u0026', '&')
                return video_url
                
            elif status in ["in_queue", "generating"]:
                # 视频生成等待通常比较久，我们打印一个点代表还在等待，等待周期可设为更长的5秒或10秒
                print(".", end="", flush=True)
                time.sleep(5)
                
            elif status in ["not_found", "expired"]:
                print(f"\n❌ 任务未找到或已过期: {status}")
                return ""
                
            else:
                print(f"\n❓ 未知状态: {status}")
                return ""


if __name__ == "__main__":
    import argparse

    # 命令行参数解析
    parser = argparse.ArgumentParser(description="调用即梦AI视频生成API，支持文生视频和图生视频，生成视频并保存到本地")
    parser.add_argument("--prompt", type=str, default=None, help="视频生成提示词（文生视频时必填，图生视频时可选）")
    parser.add_argument("--image_url", type=str, default=None, help="首帧图片的URL地址（传入即触发图生视频模式）")
    parser.add_argument("--output", type=str, required=True, help="视频保存的本地相对/绝对路径，包含文件名（例如 output.mp4）")
    parser.add_argument("--frames", type=int, default=121, choices=[121, 241], help="帧数：121 对应 5秒，241 对应 10秒，默认 121")
    parser.add_argument("--aspect_ratio", type=str, default="16:9", help="视频比例，如 '16:9', '4:3', '1:1', '9:16'，默认 '16:9'")

    args = parser.parse_args()

    # 校验：prompt 和 image_url 不能同时为空
    if not args.prompt and not args.image_url:
        parser.error("--prompt 和 --image_url 不能同时为空，至少需要提供一个")

    # 实例化调用类，自动从 .env 中读取 VOLC_ACCESS_KEY 和 VOLC_SECRET_KEY
    generator = JimengVideoGenerator()

    # 判断模式
    mode_name = "图生视频" if args.image_url else "文生视频"
    duration = "5秒" if args.frames == 121 else "10秒"

    # 打印执行信息
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎬 开始执行{mode_name}（{duration}）...")
    if args.prompt:
        print(f"- 提示词 (Prompt): {args.prompt}")
    if args.image_url:
        print(f"- 首帧图片 (Image URL): {args.image_url}")
    print(f"- 比例 (Aspect Ratio): {args.aspect_ratio}")
    print(f"- 目标路径 (Output): {args.output}")

    # 调用视频生成接口
    image_urls_param = [args.image_url] if args.image_url else None
    video_url = generator.generate_video(
        prompt=args.prompt,
        image_urls=image_urls_param,
        frames=args.frames,
        aspect_ratio=args.aspect_ratio
    )

    # 获取数据并下载
    if video_url:
        print(f"\n✅ {mode_name}成功！视频下载链接为：\n{video_url}")

        # 将视频保存到指定目录
        try:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ 正在下载视频保存到本地...")
            vid_response = requests.get(video_url, stream=True)
            vid_response.raise_for_status()

            # 若给出的路径涉及多层文件夹，则自动创建父文件夹
            output_dir = os.path.dirname(os.path.abspath(args.output))
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            with open(args.output, "wb") as f:
                for chunk in vid_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"✨ 完美！视频已成功保存至: {os.path.abspath(args.output)}")
        except Exception as e:
            print(f"❌ 下载或保存视频时出错: {e}")
    else:
        print(f"\n❌ {mode_name}失败，未返回视频链接。")

