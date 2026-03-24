# WeChat Article Writer

微信公众号技术文章自动生成工具 - 从选题到发布的完整自动化流程。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

## ✨ 功能特性

- 🔍 **智能搜索** - 自动搜索相关技术资讯和资料
- 📝 **内容改写** - 基于 AI 将技术内容改写成通俗易懂的公众号文章
- 🎨 **自动配图** - 使用即梦 AI 生成精美的封面图和内容配图
- 📐 **智能排版** - 集成 Ziliu 智能排版，一键优化文章格式
- 🚀 **一键发布** - 自动上传至微信公众号草稿箱

## 🏗️ 项目结构

```
wechat-article-writer/
├── generate.py              # 主生成脚本
├── SKILL.md                 # 完整技能文档（OpenClaw 格式）
├── EXAMPLES.md              # 使用示例
├── references/              # 参考文档
│   ├── writing-style.md     # 写作风格指南
│   ├── cover-image-guide.md # 封面图生成指南
│   ├── content-images-guide.md  # 内容配图指南
│   ├── api-configuration.md     # API 配置说明
│   └── ...
├── scripts/                 # 实用脚本
│   ├── generate_image_by_text.py    # 即梦 AI 文生图
│   ├── generate_image_by_image.py   # 即梦 AI 图生图
│   ├── generate_video_by_text_or_firstImage.py  # 即梦 AI 视频生成
│   ├── upload_to_wechat_draft.py    # 上传至公众号草稿箱
│   └── wecom_send_file.py           # 企业微信发送文件
├── .env.example             # 环境变量示例
└── README.md                # 本文件
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/La0bALanG/wechat-article-writer.git
cd wechat-article-writer
```

### 2. 安装依赖

```bash
pip install anthropic requests markdown python-dotenv
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 4. 生成文章

```bash
# 标准模式（2000-3000字）
python generate.py \
  --topic "Claude Sonnet 4 最新特性" \
  --url "https://example.com/article" \
  --type new_tool \
  --output ./output

# 深度模式（5000字）
python generate.py \
  --topic "AI 大模型发展趋势" \
  --url "https://example.com/article" \
  --type industry_news \
  --mode deep \
  --output ./output
```

### 5. 生成封面图

```bash
cd scripts
conda activate llm_env  # 或你的 Python 环境
python generate_image_by_text.py \
  --prompt "A stunning cover for Claude AI, gradient blue to purple, title 'Claude Sonnet 4' subtitle '下一代AI助手' in Chinese..." \
  --output cover.png
```

### 6. 上传至公众号草稿箱

```bash
python upload_to_wechat_draft.py \
  "./output/article.md" \
  "./output/cover.png" \
  --author "你的名字"
```

## ⚙️ 配置说明

### 即梦 AI API

1. 访问 [火山引擎](https://www.volcengine.com/)
2. 开通即梦 AI 服务
3. 获取 Access Key 和 Secret Key
4. 填入 `.env` 文件

### 微信公众号

1. 登录 [微信开放平台](https://open.weixin.qq.com/)
2. 注册并认证公众号
3. 获取 AppID 和 AppSecret
4. 填入 `.env` 文件

### Ziliu 智能排版

1. 访问 [Ziliu](https://ziliu.online/)
2. 注册账号获取 API Key
3. 填入 `.env` 文件

## 📝 内容类型

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| `new_tool` | 新工具介绍 | AI 工具、开源项目、效率软件 |
| `tutorial` | 教程指南 | 技术教程、使用指南、最佳实践 |
| `industry_news` | 行业资讯 | 技术新闻、产品发布、行业动态 |

## 🎨 封面图配色指南

| 文章类型 | 配色方案 | 色彩代码 |
|---------|---------|---------|
| AI/科技类 | 蓝紫渐变 | `#1a1f5c` → `#7c3aed` |
| 工具/效率类 | 绿橙渐变 | `#10b981` → `#f97316` |
| 数据/分析类 | 蓝绿渐变 | `#0891b2` → `#06b6d4` |
| 创意/设计类 | 粉紫渐变 | `#ec4899` → `#a855f7` |

## 📖 详细文档

- [写作风格指南](references/writing-style.md)
- [封面图生成指南](references/cover-image-guide.md)
- [内容配图指南](references/content-images-guide.md)
- [API 配置指南](references/api-configuration.md)
- [完整使用示例](EXAMPLES.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent 框架
- [即梦 AI](https://jimeng.jianying.com/) - 文生图/视频
- [Ziliu](https://ziliu.online/) - 智能排版服务
