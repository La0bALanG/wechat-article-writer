import os
import re
import json
import argparse
import requests
import markdown
import time

# 微信开放平台配置
# 请从环境变量或 .env 文件读取，详见 README 配置说明
APPID = os.environ.get("WECHAT_APPID", "your_appid_here")
APPSECRET = os.environ.get("WECHAT_APPSECRET", "your_appsecret_here")

# 缓存access_token的文件路径
TOKEN_CACHE_FILE = ".wechat_access_token.json"

def get_access_token():
    """获取 access_token，如果缓存有效则读取缓存，否则重新请求接口并缓存"""
    
    # 尝试读取缓存
    if os.path.exists(TOKEN_CACHE_FILE):
        try:
            with open(TOKEN_CACHE_FILE, 'r') as f:
                data = json.load(f)
                # 预留 5 分钟缓冲时间
                if time.time() < data.get('expires_at', 0) - 300:
                    return data.get('access_token')
        except Exception as e:
            print(f"读取 Token 缓存失败: {e}")
            
    # 请求新Token
    print("重新获取微信 Access Token...")
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    r = requests.get(url)
    res = r.json()
    
    if "access_token" in res:
        token = res["access_token"]
        expires_in = res.get("expires_in", 7200)
        
        # 缓存起来
        data = {
            "access_token": token,
            "expires_at": time.time() + expires_in
        }
        with open(TOKEN_CACHE_FILE, 'w') as f:
            json.dump(data, f)
            
        return token
    else:
        print("获取 Access Token 失败:", res)
        return None

def upload_permanent_material(access_token, file_path, material_type="image"):
    """上传永久素材 (如图文消息的封面图必填永久MediaID)"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={material_type}"
    print(f"[{file_path}] 正在上传为永久封面素材...")
    with open(file_path, 'rb') as f:
        files = {'media': f}
        r = requests.post(url, files=files)
    r.encoding = 'utf-8'
    return r.json()

def upload_content_image(access_token, file_path):
    """上传图文消息内的图片获取URL (不占用永久素材库)"""
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
    print(f"[{file_path}] 正在上传为正文图片获取链接...")
    with open(file_path, 'rb') as f:
        files = {'media': f}
        r = requests.post(url, files=files)
    r.encoding = 'utf-8'
    return r.json()

def add_draft(access_token, title, content, thumb_media_id, author="麦多多", digest=""):
    """调用新增草稿接口"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    
    article = {
        "article_type": "news",
        "title": title,
        "author": author,
        "content": content,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0
    }
    
    if digest:
        article["digest"] = digest
        
    payload = {
        "articles": [article]
    }
    
    # 微信API要求 title/author 等不使用Unicode转义格式，故确保 ensure_ascii=False
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    
    print("正在提交草稿箱请求...")
    r = requests.post(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    r.encoding = 'utf-8'
    return r.json()

def extract_title_from_md(md_content):
    """从Markdown中提取首个一级标题作为文章标题"""
    title = "无标题文档"
    lines = md_content.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
    return title

def format_markdown_with_ziliu(md_content):
    """使用 ziliu.online API 对 Markdown 文章进行智能排版"""
    ziliu_api_key = "ziliu_sk_c4b261c7cde04b3ac0d44ab16c216bf1f2bc1b1fd2ae1b8c"
    url = "https://ziliu.online/api/convert"
    headers = {
        "Authorization": f"Bearer {ziliu_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": md_content,
        "style": "tech",
        "platform": "wechat"
    }
    
    print("正在调用 Ziliu API 进行智能排版...")
    try:
        r = requests.post(url, json=payload, headers=headers)
        r.raise_for_status()
        res = r.json()
        
        # 尝试从返回结构中获取 html
        html_result = None
        if "data" in res and "html" in res["data"]:
            html_result = res["data"]["html"]
        elif "html" in res:
            html_result = res["html"]
            
        if html_result:
            print("✅ 智能排版成功！")
            return html_result
        else:
            print(f"⚠️ Ziliu API 返回格式意外: {res}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 调用 Ziliu API 失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误详情: {e.response.text}")
        return None

def process_markdown_content(md_content, base_dir, access_token):
    """处理Markdown内容：将本地图片上传并替换URL，然后转为HTML"""
    
    def replace_img(match):
        alt = match.group(1)
        src = match.group(2)
        
        # 忽略已经是网络链接的图片
        if src.startswith("http://") or src.startswith("https://"):
            return match.group(0)
            
        # 处理本地相对路径图片
        img_path = os.path.join(base_dir, src)
        if os.path.exists(img_path):
            img_res = upload_content_image(access_token, img_path)
            if 'url' in img_res:
                print(f" -> 替换成功: {img_res['url']}")
                return f"![{alt}]({img_res['url']})"
            else:
                print(f" -> 图片上传失败: {img_res}")
        else:
            print(f" -> 本地图片不存在，跳过: {img_path}")
            
        return match.group(0)

    # 1. 匹配 Markdown 图片语法: ![alt](src)，替换为微信图片链接
    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    md_content = pattern.sub(replace_img, md_content)
    
    # 2. 调用 Ziliu API 进行智能排版 (直接获取排版好的 HTML)
    formatted_html = format_markdown_with_ziliu(md_content)
    
    if formatted_html:
        return formatted_html
        
    print("⚠️ 智能排版失败，降级使用本地 Markdown 转 HTML")
    # 降级方案：本地将包含微信图片URL的Markdown转化为HTML，微信图文需要HTML标签格式
    # extensions=['extra'] 可以支持表格等各种Markdown增强语法
    html_content = markdown.markdown(md_content, extensions=['extra', 'tables', 'nl2br'])
    return html_content

def main():
    parser = argparse.ArgumentParser(description="新增Markdown文章到微信公众号草稿箱")
    parser.add_argument('md_file', help="输入的Markdown文件路径")
    parser.add_argument('cover_image', help="封面图片路径")
    parser.add_argument('--author', default="麦多多", help="文章作者名称")
    args = parser.parse_args()
    
    md_file = os.path.abspath(args.md_file)
    cover_image = os.path.abspath(args.cover_image)
    base_dir = os.path.dirname(md_file)
    
    if not os.path.exists(md_file):
        print(f"找不到Markdown文件: {md_file}")
        return
        
    if not os.path.exists(cover_image):
        print(f"找不到封面图: {cover_image}")
        return
        
    # 首先获取Access Token (自带过期检测和更新)
    access_token = get_access_token()
    if not access_token:
        print("无法获取有效的 Access Token，脚本退出。")
        return
        
    print("="*40)
    print(" 准备上传文章到微信公众号草稿箱")
    print(f" 文件: {md_file}")
    print(f" 封面: {cover_image}")
    print("="*40)
    
    # 1. 上传封面图片到永久素材，获取 thumb_media_id (图文消息必须是永久MediaID)
    cover_res = upload_permanent_material(access_token, cover_image, material_type="image")
    if "media_id" not in cover_res:
        print("❌ 上传封面素材失败:", json.dumps(cover_res, ensure_ascii=False))
        # 错误码40001, 40014, 42001表示Token异常
        if cover_res.get('errcode') in [40001, 40014, 42001, 40002]:
            print("❗ 提示：Access Token 已失效，正在清除缓存，请重新运行脚本。")
            if os.path.exists(TOKEN_CACHE_FILE):
                os.remove(TOKEN_CACHE_FILE)
        return
        
    thumb_media_id = cover_res["media_id"]
    print(f"✅ 封面永久素材上传成功，media_id: {thumb_media_id}\n")
    
    # 2. 读取并处理Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    title = extract_title_from_md(md_content)
    print(f"提取的文章标题: {title}")
    print(f"正在处理 Markdown 中的正文及图片转换...")
    
    html_content = process_markdown_content(md_content, base_dir, access_token)
    # console里展示前面几个字符确认下
    print(f"✅ Markdown转HTML成功，生成HTML长度: {len(html_content)} 字符\n")
    
    # 3. 新增此内容到草稿箱
    draft_res = add_draft(access_token, title, html_content, thumb_media_id, author=args.author)
    
    if "media_id" in draft_res:
        print(f"🎉 成功！图文消息已新增到草稿箱。")
        print(f"📝 draft media_id: {draft_res['media_id']}")
    else:
        print("❌ 创建草稿失败:", json.dumps(draft_res, ensure_ascii=False))

if __name__ == "__main__":
    main()
