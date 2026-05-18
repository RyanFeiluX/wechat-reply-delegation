# WeChat Reply Delegation - 用户指南

## 概述

WeChat Reply Delegation 系统可以在微信群聊中，根据您配置的规则自动代替您回复消息。您可以设置时间段、在线状态、关键词等条件，让系统在合适的时机自动回复群消息。

## 安装步骤

### 快速安装（推荐）

使用以下单命令自动安装并配置所有内容：

```bash
pip install hermes-wechat-reply-delegation-plugin && hermes-wechat-reply-delegation-install
```

### 手动安装

如果您希望分步安装：

```bash
# 从 PyPI 安装包
pip install hermes-wechat-reply-delegation-plugin

# 运行安装程序设置配置
hermes-wechat-reply-delegation-install
```

### 从源代码安装

```bash
cd d:\src\wechat-reply-delegation
pip install .
hermes-wechat-reply-delegation-install
```

### 直接从 GitHub 安装

将代码推送到 GitHub 后，用户可以直接安装：

**从 GitHub 单命令安装：**

```bash
pip install git+https://github.com/RyanFeiluX/wechat-reply-delegation.git && hermes-wechat-reply-delegation-install
```

**从特定分支安装：**

```bash
pip install git+https://github.com/RyanFeiluX/wechat-reply-delegation.git@main && hermes-wechat-reply-delegation-install
```

## 配置说明

配置文件位于 `~/.hermes/wechat-reply-delegation/config.yaml`，使用文本编辑器打开即可修改。

### 全局配置

```yaml
# 是否启用代理回复功能
enabled: true

# 时区设置（建议使用 Asia/Shanghai）
timezone: "Asia/Shanghai"

# 默认回复消息（当没有匹配到特定话题时使用）
default_reply: "您好，我是智能助手，会将消息转达给用户。"
```

### 在线状态检测设置

```yaml
online_status:
  # 检测模式：passive（被动推断）| manual（手动设置）| hybrid（混合模式）
  mode: hybrid
  
  # 被动模式设置（根据用户活跃度推断）
  passive:
    # 用户无操作多少分钟后视为离线
    inactivity_timeout_minutes: 30
    # 检测来源：last_message（最后发言时间）
    source: last_message
  
  # 手动模式设置
  manual:
    # 是否启用 HTTP 接口
    webhook: true
    # 是否启用聊天指令
    slash_commands: true
```

### 代理回复标记设置

```yaml
proxy_marker:
  # 是否在回复前添加前缀
  prefix_enabled: true
  # 前缀文本
  prefix_text: "🤖 [代班] "
  # 是否添加签名
  signature_enabled: false
  # 签名文本
  signature_text: "\n—— 由 Hermes 代班回复"
```

### 群配置

每个群可以独立配置，在 `groups` 字段下添加群配置：

```yaml
groups:
  "群ID":
    # 是否启用该群的代理回复
    enabled: true
    # 显示名称（仅用于标识）
    display_name: "我的工作群"
    
    # 时间段规则
    schedule:
      enabled: true
      time_ranges:
        # 工作日 9:00-18:00
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "18:00"
        # 周末 10:00-16:00
        - days: [sat, sun]
          start: "10:00"
          end: "16:00"
    
    # 在线状态规则
    online_status:
      # 回复时机：always（始终）| online_only（仅在线）| offline_only（仅离线）
      reply_when: offline_only
    
    # 触发条件
    triggers:
      # 是否需要 @提及才触发
      at_mention: true
      # 关键词触发列表
      keywords:
        - "会议"
        - "报价"
        - "问题"
      # 是否响应 @所有人
      at_all: false
    
    # 回复指令
    instructions:
      # 默认回复
      default: "您好，我是智能助手，会将消息转达给用户。"
      # 话题特定回复
      topic_responses:
        - keywords: ["会议", "开会"]
          response: "收到会议通知，用户会尽快查看并回复。"
        - keywords: ["报价", "价格"]
          response: "关于报价的问题，用户会尽快提供详细信息。"
```

## 获取群 ID

您可以通过以下方式获取群 ID：

1. **自动检测**：当您在群里发消息时，系统会自动记录群 ID
2. **指令查询**：在群里发送 `/proxy status`，系统会返回当前群的 ID

## 聊天指令

在群聊中发送以下指令可以管理代理回复：

| 指令              | 功能             |
| --------------- | -------------- |
| `/proxy status` | 查看当前群的代理配置状态   |
| `/proxy on`     | 启用当前群的代理回复     |
| `/proxy off`    | 禁用当前群的代理回复     |
| `/proxy away`   | 设置"离开"状态（开启代理） |
| `/proxy back`   | 设置"回来"状态（关闭代理） |
| `/proxy config` | 查看当前群完整配置      |
| `/proxy reload` | 热重载配置（修改配置后生效） |

## Web 管理面板

通过可视化界面管理配置，操作更直观方便。

### 启动方式

```bash
# 确保已安装依赖
pip install .

# 启动 Web 服务
hermes-wechat-reply-delegation-web
```

### 访问地址

- 默认地址：`http://localhost:5100`
- 可通过环境变量 `WECHAT_REPLY_DELEGATION_PORT` 自定义端口

### 默认账号

- 用户名：`admin`
- 密码：`password123`

### 功能特性

- **全局配置管理**：系统启用状态、时区、日志级别、代理回复标记
- **群配置管理**：添加、编辑、删除群配置
- **在线状态规则**：设置回复时机（始终/仅在线/仅离线）
- **触发条件设置**：@提及、@所有人、关键词配置
- **时间段规则**：支持多个时间段配置
- **回复指令管理**：默认回复、话题特定回复
- **中英文双语支持**：配置支持中英文两种语言

### 安全提示

1. **修改默认密码**：首次登录后建议修改默认密码
2. **HTTPS 访问**：生产环境建议配置 HTTPS
3. **端口开放**：仅在信任的网络环境中开放端口
4. **会话安全**：操作完成后及时退出登录

## 使用场景示例

### 场景 1：工作时间代班

```yaml
groups:
  "工作群@chatroom":
    enabled: true
    display_name: "技术部工作群"
    schedule:
      enabled: true
      time_ranges:
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "18:00"
    online_status:
      reply_when: offline_only
    triggers:
      at_mention: true
      keywords: ["API", "接口", "故障", "bug"]
    instructions:
      default: "我已收到消息，会尽快转告用户。"
      topic_responses:
        - keywords: ["故障", "bug", "紧急"]
          response: "收到故障报告，已紧急通知用户！"
```

### 场景 2：离线自动应答

```yaml
groups:
  "业主群@chatroom":
    enabled: true
    display_name: "小区业主群"
    schedule:
      enabled: false
    online_status:
      reply_when: offline_only
    triggers:
      at_mention: true
    instructions:
      default: "您好，用户暂时不在，他看到消息后会尽快回复您。"
```

### 场景 3：话题定向代理

```yaml
groups:
  "客户群@chatroom":
    enabled: true
    display_name: "客户服务群"
    schedule:
      enabled: true
      time_ranges:
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "21:00"
    online_status:
      reply_when: always
    triggers:
      at_mention: true
      keywords: ["产品", "服务", "咨询"]
    instructions:
      default: "感谢您的咨询，我会记录下来并尽快回复。"
      topic_responses:
        - keywords: ["产品", "功能"]
          response: "关于产品功能的问题，我会请相关同事尽快解答。"
        - keywords: ["服务", "售后"]
          response: "售后服务热线：400-xxx-xxxx，或留下您的联系方式，我们会尽快联系您。"
```

## 配置热重载

修改配置文件后，可以通过以下方式让配置生效：

1. **聊天指令**：在群里发送 `/proxy reload`
2. **命令行**：运行 `hermes proxy reload`

## 注意事项

1. **频率限制**：同一群每分钟最多发送 1 条代理回复，避免过于频繁打扰群友
2. **配置校验**：配置文件有误时，系统会使用默认配置并记录错误日志
3. **在线状态**：用户发言后会自动重置离线状态计时器
4. **排除词**：可以通过 `stop_words` 配置排除某些关键词

## 故障排除

### 问题 1：代理回复没有生效

**检查步骤：**

1. 确认配置文件中 `enabled: true`
2. 确认群配置已正确添加
3. 检查时间段设置是否包含当前时间
4. 检查在线状态是否符合条件

### 问题 2：收到 "配置错误" 提示

**解决方法：**

1. 使用文本编辑器检查配置文件格式
2. 确保所有冒号后面有空格
3. 确保缩进正确（使用空格，不要使用 Tab）
4. 参考 `config-template.yaml` 检查格式

### 问题 3：回复过于频繁

**解决方法：**

1. 增加 `inactivity_timeout_minutes` 的值
2. 设置更严格的时间段规则
3. 添加更多关键词限制触发条件

## 联系支持

如果您遇到问题或有建议，请通过以下方式联系：

- 发送邮件至 <support@example.com>
- 在群里 @机器人 发送问题描述

