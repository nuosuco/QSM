"""
YouTube 自动上传服务
"""
import json
import os
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle
import base64

# 配置路径
SERVER_DIR = Path("/root/SOM/server")
AUTH_CONFIG = SERVER_DIR / "auth_config.json"
TOKEN_FILE = SERVER_DIR / "youtube_token.pickle"
CLIENT_SECRET_FILE = SERVER_DIR / "youtube_client_secret.json"

# YouTube OAuth 范围
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def get_auth_config():
    """获取YouTube配置"""
    with open(AUTH_CONFIG, 'r') as f:
        cfg = json.load(f)
    return cfg.get('youtube', {})


def get_credentials():
    """获取YouTube凭据"""
    creds = None
    
    # 检查是否有保存的token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 如果没有凭据或凭据已过期
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("⚠️ 需要授权YouTube访问")
            return None, None
        
        # 保存token
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds, None


def init_auth():
    """初始化OAuth授权，返回授权URL"""
    with open(CLIENT_SECRET_FILE, 'r') as f:
        client_config = json.load(f)
    
    # 创建Flow但不保存，直接返回授权URL
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri='https://som.top/youtube-callback'
    )
    
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url, flow


def complete_auth(authorization_code, flow=None):
    """完成OAuth授权"""
    try:
        with open(CLIENT_SECRET_FILE, 'r') as f:
            client_config = json.load(f)
        
        # 使用相同的Flow或重新创建
        if flow:
            flow.redirect_uri = 'https://som.top/youtube-callback'
            flow.fetch_token(code=authorization_code)
            creds = flow.credentials
        else:
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri='https://som.top/youtube-callback'
            )
            flow.redirect_uri = 'https://som.top/youtube-callback'
            flow.fetch_token(code=authorization_code)
            creds = flow.credentials
        
        # 保存token
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        return True, "授权成功！"
    except Exception as e:
        return False, f"授权失败: {str(e)}"


def upload_video(
    video_path,
    title,
    description,
    keywords=None,
    category_id='22',
    privacy_status='public'
):
    """上传视频到YouTube"""
    creds, _ = get_credentials()
    
    if not creds:
        auth_url, _ = init_auth()
        return {
            "success": False,
            "error": "需要先完成OAuth授权",
            "auth_url": auth_url
        }
    
    try:
        youtube = build('youtube', 'v3', credentials=creds)
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': keywords or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        
        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        return {
            "success": True,
            "video_id": response['id'],
            "video_url": f"https://youtu.be/{response['id']}",
            "title": response['snippet']['title']
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_channel_info():
    """获取频道信息"""
    creds, _ = get_credentials()
    
    if not creds:
        return {"success": False, "error": "需要先完成OAuth授权"}
    
    try:
        youtube = build('youtube', 'v3', credentials=creds)
        
        request = youtube.channels().list(
            part='snippet,statistics',
            mine=True
        )
        
        response = request.execute()
        
        if response['items']:
            channel = response['items'][0]
            return {
                "success": True,
                "channel_id": channel['id'],
                "title": channel['snippet']['title'],
                "subscriber_count": channel['statistics'].get('subscriberCount', '0'),
                "video_count": channel['statistics'].get('videoCount', '0'),
                "view_count": channel['statistics'].get('viewCount', '0')
            }
        else:
            return {"success": False, "error": "未找到频道信息"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_videos(page_size=10):
    """列出最近上传的视频"""
    creds, _ = get_credentials()
    
    if not creds:
        return {"success": False, "error": "需要先完成OAuth授权"}
    
    try:
        youtube = build('youtube', 'v3', credentials=creds)
        
        request = youtube.search().list(
            part='snippet',
            mine=True,
            maxResults=page_size,
            order='date'
        )
        
        response = request.execute()
        
        videos = []
        for item in response.get('items', []):
            if item['id']['kind'] == 'youtube#video':
                videos.append({
                    "video_id": item['id']['videoId'],
                    "title": item['snippet']['title'],
                    "published_at": item['snippet']['publishedAt'],
                    "description": item['snippet']['description'][:100] + "..."
                })
        
        return {"success": True, "videos": videos}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
