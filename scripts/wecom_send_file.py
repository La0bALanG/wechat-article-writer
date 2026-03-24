#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信自建应用发送文件工具

用法:
    python wecom_send_file.py --file /path/to/file.jpg
    python wecom_send_file.py --file /path/to/file.pdf --user yutian-anweichao
"""

import argparse
import json
import os
import requests
import sys
from urllib.parse import quote

# 企业微信配置
CORP_ID = "ww978049e5b0a2e29d"
CORP_SECRET = "DYXhAPykd95wO1D7zdGqbftepR6jp92k-LTkCDsHuj8"
AGENT_ID = 1000126

# API 地址
API_BASE = "https://qyapi.weixin.qq.com"


def get_access_token():
    """获取 access_token"""
    url = f"{API_BASE}/cgi-bin/gettoken"
    params = {
        "corpid": CORP_ID,
        "corpsecret": CORP_SECRET
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("errcode") == 0:
            return data.get("access_token")
        else:
            print(f"❌ 获取 access_token 失败: {data.get('errmsg')}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def upload_media(file_path, access_token):
    """上传临时素材，获取 media_id"""
    url = f"{API_BASE}/cgi-bin/media/upload"
    params = {
        "access_token": access_token,
        "type": "file"
    }
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    # 获取文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 根据扩展名判断类型
    if file_ext in ['.jpg', '.jpeg', '.png']:
        media_type = "image"
    elif file_ext in ['.mp3', '.amr']:
        media_type = "voice"
    elif file_ext in ['.mp4']:
        media_type = "video"
    else:
        media_type = "file"
    
    params["type"] = media_type
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'media': (os.path.basename(file_path), f, 'application/octet-stream')
            }
            response = requests.post(url, params=params, files=files, timeout=30)
            data = response.json()
            
            if data.get("errcode") == 0:
                return data.get("media_id")
            else:
                print(f"❌ 上传素材失败: {data.get('errmsg')}")
                return None
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return None


def send_file(user_id, media_id, access_token):
    """发送文件消息"""
    url = f"{API_BASE}/cgi-bin/message/send"
    params = {
        "access_token": access_token
    }
    
    message = {
        "touser": user_id,
        "msgtype": "file",
        "agentid": AGENT_ID,
        "file": {
            "media_id": media_id
        }
    }
    
    try:
        response = requests.post(url, params=params, json=message, timeout=10)
        data = response.json()
        
        if data.get("errcode") == 0:
            return True
        else:
            print(f"❌ 发送消息失败: {data.get('errmsg')}")
            return False
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


def send_file_message(file_path, user_id="@all"):
    """发送文件的主流程"""
    print(f"📤 开始发送文件: {file_path}")
    print(f"👤 接收用户: {user_id}")
    print("-" * 40)
    
    # 第1步：获取 access_token
    print("🔑 正在获取 access_token...")
    access_token = get_access_token()
    if not access_token:
        return False
    print(f"✅ access_token 获取成功")
    
    # 第2步：上传素材
    print("📤 正在上传文件...")
    media_id = upload_media(file_path, access_token)
    if not media_id:
        return False
    print(f"✅ 文件上传成功, media_id: {media_id}")
    
    # 第3步：发送消息
    print("📨 正在发送消息...")
    success = send_file(user_id, media_id, access_token)
    if success:
        print("✅ 文件发送成功!")
    else:
        print("❌ 文件发送失败")
    
    return success


def main():
    parser = argparse.ArgumentParser(description="企业微信发送文件工具")
    parser.add_argument("--file", "-f", required=True, help="要发送的文件路径")
    parser.add_argument("--user", "-u", default="@all", help="接收用户ID，默认 @all")
    
    args = parser.parse_args()
    
    success = send_file_message(args.file, args.user)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
