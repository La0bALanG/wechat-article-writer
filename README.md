<div align="center">

# 📝 WeChat Article Writer

### 微信公众号技术文章 · AI 全自动生成工具

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/OpenClaw-Compatible-orange?style=for-the-badge" alt="OpenClaw">
</p>

<p align="center">
  🔍 <strong>智能搜索</strong> · 🎨 <strong>AI 配图</strong> · 📐 <strong>智能排版</strong> · 🚀 <strong>一键发布</strong>
</p>

[//]: # (<img src="docs/demo-cover.png" alt="Demo" width="600">)

</div>

---

## 🌟 项目简介

**WeChat Article Writer** 是一款基于 AI 的微信公众号文章全自动生产工具。从选题、搜索、改写、配图到排版发布，全流程自动化，让你的内容生产效率提升 **10 倍**。

> 💡 原本需要 2 小时的公众号文章，现在只需 5 分钟

---

## ✨ 核心特性

<table>
<tr>
<td width="25%" align="center">

### 🔍 智能搜索
**深度信息挖掘**

- 多轮搜索策略
- 权威信源优先
- 自动摘要提取

</td>
<td width="25%" align="center">

### 🧠 AI 改写
**优质内容生成**

- 通俗化技术内容
- 保留核心要点
- 符合公众号调性

</td>
<td width="25%" align="center">

### 🎨 自动配图
**即梦 AI 驱动**

- 精美封面生成
- 内容图表制作
- 16:9 标准尺寸

</td>
<td width="25%" align="center">

### 📤 一键发布
**直达公众号**

- 智能排版优化
- 草稿箱同步
- 图片自动上传

</td>
</tr>
</table>

---

## 🛠️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    WeChat Article Writer                     │
├─────────────────────────────────────────────────────────────┤
│  🔍 搜索层  │  Tavily AI 搜索 · 多源信息聚合                 │
├─────────────────────────────────────────────────────────────┤
│  🧠 生成层  │  Claude API · 智能改写与创作                  │
├─────────────────────────────────────────────────────────────┤
│  🎨 视觉层  │  即梦 AI · 封面图 & 内容配图                  │
├─────────────────────────────────────────────────────────────┤
│  📐 排版层  │  Ziliu API · 专业公众号排版                  │
├─────────────────────────────────────────────────────────────┤
│  📤 发布层  │  微信开放平台 · 草稿箱同步                    │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Anthropic-Claude-FF6B6B?style=flat-square" alt="Claude">
  <img src="https://img.shields.io/badge/火山引擎-即梦AI-FF6A00?style=flat-square" alt="Jimeng">
  <img src="https://img.shields.io/badge/Ziliu-排版-00C48C?style=flat-square" alt="Ziliu">
  <img src="https://img.shields.io/badge/微信-公众号-07C160?style=flat-square&logo=wechat" alt="WeChat">
</p>

---

## 🚀 快速开始

### 1️⃣ 克隆仓库

```bash
git clone https://github.com/La0bALanG/wechat-article-writer.git
cd wechat-article-writer
```

### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
# 或
pip install anthropic requests markdown python-dotenv
```

### 3️⃣ 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

<details>
<summary>🔑 点击查看所需 API 清单</summary>

| 服务 | 用途 | 获取地址 |
|-----|------|---------|
| **Anthropic Claude** | 文章生成 | [console.anthropic.com](https://console.anthropic.com) |
| **火山引擎即梦 AI** | 图片生成 | [volcengine.com](https://www.volcengine.com) |
| **Ziliu** | 智能排版 | [ziliu.online](https://ziliu.online) |
| **微信公众号** | 文章发布 | [open.weixin.qq.com](https://open.weixin.qq.com) |

</details>

### 4️⃣ 生成你的第一篇文章

```bash
# 标准模式（2000-3000字）
python generate.py \
  --topic "Claude Sonnet 4 最新特性解析" \
  --url "https://example.com/article" \
  --type new_tool \
  --output ./output
```

### 5️⃣ 生成封面图

```bash
cd scripts
python generate_image_by_text.py \
  --prompt "Claude Sonnet 4 封面，蓝紫渐变，科技感，简洁大气，中文标题" \
  --output cover.png
```

### 6️⃣ 上传至公众号草稿箱

```bash
python upload_to_wechat_draft.py \
  "./output/article.md" \
  "./output/cover.png" \
  --author "你的名字"
```

✅ **完成！** 打开公众号后台即可看到生成的草稿。

---

## 📋 内容类型支持

| 类型 | 说明 | 适用场景 | 配图策略 |
|-----|------|---------|---------|
| `new_tool` | 新工具介绍 | AI 工具、开源项目、效率软件 | 封面 + 架构图 |
| `tutorial` | 教程指南 | 技术教程、使用指南 | 封面 + 流程图 |
| `industry_news` | 行业资讯 | 技术新闻、产品发布 | 仅封面图 |

---

## 🎨 视觉设计系统

### 封面图配色方案

<p align="center">

| 文章类型 | 配色方案 | 预览 |
|---------|---------|------|
| **AI/科技类** | 蓝紫渐变 | `linear-gradient(135deg, #1a1f5c 0%, #7c3aed 100%)` |
| **工具/效率类** | 绿橙渐变 | `linear-gradient(135deg, #10b981 0%, #f97316 100%)` |
| **数据/分析类** | 蓝绿渐变 | `linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)` |
| **创意/设计类** | 粉紫渐变 | `linear-gradient(135deg, #ec4899 0%, #a855f7 100%)` |

</p>

---

## 📚 文档导航

<table>
<tr>
<td>

**📖 使用指南**
- [写作风格指南](references/writing-style.md)
- [封面图生成指南](references/cover-image-guide.md)
- [内容配图指南](references/content-images-guide.md)
- [API 配置指南](references/api-configuration.md)

</td>
<td>

**💡 最佳实践**
- [完整使用示例](EXAMPLES.md)
- [事实核查要点](references/fact-checking.md)
- [图片处理标准](references/image-guidelines.md)

</td>
<td>

**🔧 技术文档**
- [SKILL.md](SKILL.md) - OpenClaw 技能规范
- [generate.py](generate.py) - 主生成脚本

</td>
</tr>
</table>

---

## 🏗️ 项目结构

```
wechat-article-writer/
├── 📄 generate.py              # 主生成脚本
├── 📖 SKILL.md                 # OpenClaw 技能规范
├── 📚 EXAMPLES.md              # 使用示例
├── 🎨 references/              # 参考文档
│   ├── writing-style.md        # 写作风格指南
│   ├── cover-image-guide.md    # 封面图设计指南
│   ├── content-images-guide.md # 内容配图指南
│   ├── api-configuration.md    # API 配置说明
│   └── ...
├── 🔧 scripts/                 # 实用脚本
│   ├── generate_image_by_text.py    # 即梦 AI 文生图
│   ├── generate_image_by_image.py   # 即梦 AI 图生图
│   ├── generate_video_by_text_or_firstImage.py  # 视频生成
│   ├── upload_to_wechat_draft.py    # 公众号上传
│   └── wecom_send_file.py           # 企业微信发送
├── ⚙️ .env.example             # 环境变量模板
└── 📜 README.md                # 本文件
```

---

## 🤝 如何贡献

1. **Fork** 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 **Pull Request**

---

## 📄 开源协议

本项目基于 [MIT](LICENSE) 协议开源。

---

## 🙏 致谢

<p align="center">
  <a href="https://github.com/openclaw/openclaw"><img src="https://img.shields.io/badge/OpenClaw-AI_Agent_Framework-6B46C1?style=flat-square" alt="OpenClaw"></a>
  <a href="https://jimeng.jianying.com/"><img src="https://img.shields.io/badge/即梦AI-文生图_视频-FF6A00?style=flat-square" alt="Jimeng"></a>
  <a href="https://ziliu.online/"><img src="https://img.shields.io/badge/Ziliu-智能排版-00C48C?style=flat-square" alt="Ziliu"></a>
</p>

---

<div align="center">

**Made with ❤️ by [La0bALanG](https://github.com/La0bALanG)**

⭐ **如果这个项目对你有帮助，请给个 Star！** ⭐

</div>
