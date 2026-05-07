# 智能代理回复系统 — 技术方案

> **Version:** 0.1-draft  
> **Author:** Hermes Agent  
> **Date:** 2026-05-07  

---

## 1. 概述

### 1.1 目标

在 WeChat 群聊中，允许用户配置一组条件规则，当条件满足时，Hermes Agent 自动代替用户回复群消息。每个群可以独立配置，支持时间段、用户在线状态、用户提前预设指示等条件维度。

### 1.2 核心场景

| 场景 | 示例 |
|------|------|
| **工作时间代班** | 工作日 9:00-18:00，用户不在线时，代回技术咨询 |
| **离线自动应答** | 用户超过 30 分钟无操作，自动回复"稍后回复" |
| **话题定向代理** | 只对特定关键词（如"报价"、"会议"）触发代理回复 |
| **个性化规则** | 每个群不同的回复风格、签名、语气 |

### 1.3 非目标

- 本方案不处理 DM（私聊）代理回复（微信群私聊场景不同）
- 本方案不涉及多平台代理（仅 WeChat 群聊）
- 本方案不替代用户身份认证（仍使用现有 iLink 绑定）

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      WeChat Gateway                              │
│  ┌──────────────┐   ┌───────────────┐   ┌────────────────────┐  │
│  │ WeixinAdapter │──▶│ Message Inbox │──▶│ Proxy Reply Plugin │  │
│  └──────────────┘   └───────────────┘   └────────┬───────────┘  │
│                                                   │              │
│                                                   ▼              │
│                                       ┌──────────────────────┐   │
│                                       │   Condition Engine    │   │
│                                       │  ┌──────┐┌───┐┌───┐ │   │
│                                       │  │ Time ││Status││Topic│  │
│                                       │  └──────┘└───┘└───┘ │   │
│                                       └──────────┬───────────┘   │
│                                                  │              │
│                          Pass? ──── Yes ────────▶│              │
│                            │                     ▼              │
│                           No           ┌────────────────────┐   │
│                            │           │  Generate Reply     │   │
│                            ▼           │  + Send to Group    │   │
│                        Silently        └────────────────────┘   │
│                        Drop /                                  │
│                        Forward to AI                           │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────┐
                    │     Config Store          │
                    │  ~/.hermes/proxy/         │
                    │  ├── config.yaml          │
                    │  └── per-group/*.yaml     │
                    └──────────────────────────┘
```

### 2.1 消息处理流水线

```
群消息到达 WeChat Adapter
  │
  ▼
消息去重、类型过滤
  │
  ▼
判断 chat_type == "group"
  │
  ▼
[新] Proxy Reply Hook 介入
  ├── 查询该群的配置
  ├── 若无配置 → 走原有逻辑（忽略或转发给 AI）
  ├── 若有配置 →
  │    ├── 条件引擎评估 (ConditionEngine.evaluate)
  │    │    ├── 时间段匹配？
  │    │    ├── 用户在线状态？
  │    │    └── 话题/关键词触发？
  │    │
  │    ├── 全部通过 → 生成代理回复，直接发到群
  │    └── 任一不通过 → 静默丢弃 / 或转发给 AI 根据规则决定
  │
  ▼
继续原有 gateway 流程
```

---

## 3. 配置设计

### 3.1 全局配置

文件路径：`~/.hermes/proxy/config.yaml`

```yaml
# ============================================
# 智能代理回复系统 — 全局配置
# ============================================

# 全局开关
enabled: true

# 默认时区
timezone: "Asia/Shanghai"

# 在线状态检测
online_status:
  # 检测模式: passive | manual | hybrid
  #   passive  = 通过用户活跃度推断
  #   manual   = 用户手动设置状态
  #   hybrid   = 结合两者
  mode: hybrid

  # Passive 模式参数
  passive:
    # 用户无操作多少分钟后视为"离线"
    inactivity_timeout_minutes: 30
    # 检测依据: last_message (最后发言时间) | heartbeat (心跳)
    source: last_message

  # Manual 模式的 API
  manual:
    # 可通过 HTTP 接口切换状态
    webhook: true
    # 也支持在聊天中通过指令设置
    slash_commands: true

# 代理回复标记
proxy_marker:
  # 是否在代理回复前加上前缀
  prefix_enabled: true
  # 前缀文本
  prefix_text: "🤖 [代班] "
  # 代理回复是否带签名
  signature_enabled: false
  signature_text: "\n—— 由 Hermes 代班回复"

# 默认回复（当群配置中 instruction 未匹配时）
default_reply: "您好，Ryan 暂时不在，他看到消息后会尽快回复您 🙏"

# 日志级别
log_level: info
```

### 3.2 单群配置

每个群一个独立配置，或所有群集中管理。

**方案 A：集中式（推荐）**

`~/.hermes/proxy/config.yaml` 中嵌套 `groups:` 字段：

```yaml
groups:
  # 群聊标识符（WeChat 群 ID 或群名别名）
  "业主群_12345@chatroom":
    enabled: true
    # 显示名称（仅用于日志和 UI）
    display_name: "小区业主群"

    # ── 时间段规则 ──
    schedule:
      enabled: true
      time_ranges:
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "18:00"
        - days: [sat, sun]
          start: "10:00"
          end: "16:00"

    # ── 在线状态规则 ──
    online_status:
      # 回复时机: always | online_only | offline_only
      reply_when: offline_only

    # ── 触发条件 ──
    triggers:
      # @提及 触发回复
      at_mention: true
      # 关键词触发
      keywords:
        - "物业"
        - "维修"
        - "通知"
        - "业委会"
      # 群内@所有人 是否触发
      at_all: false

    # ── 回复指令 ──
    instructions:
      # 默认回复（无关键词匹配时）
      default: "您好，我是 Ryan 的智能助手。Ryan 暂时不在，我会记录您的消息并转达给他。"
      # 关键词 → 特定回复
      topic_responses:
        - keywords: ["维修", "漏水", "电路"]
          response: "收到维修报修信息，我已记录下来，会转告 Ryan 尽快跟进处理。"
        - keywords: ["物业费", "缴费"]
          response: "关于物业费的问题，请直接联系物业管理处咨询，Ryan 稍后也会跟进。"
        - keywords: ["会议", "业委会", "开会"]
          response: "收到会议相关通知，Ryan 会尽快查看并回复。"
      # 组合回复（同时匹配多个条件）
      compound:
        - if_all: ["紧急", "物业"]
          response: "紧急物业问题！我已立即通知 Ryan，他会尽快处理。如需联系物业，电话：XXXXX"

  "工作群_67890@chatroom":
    enabled: true
    display_name: "技术部工作群"
    schedule:
      enabled: true
      time_ranges:
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "12:00"
        - days: [mon, tue, wed, thu, fri]
          start: "14:00"
          end: "18:00"
    online_status:
      reply_when: offline_only
    triggers:
      at_mention: true
      keywords:
        - "API"
        - "接口"
        - "上线"
        - "故障"
        - "bug"
        - "紧急"
    instructions:
      default: "Ryan 暂时不在，我会将消息转告他。"
      topic_responses:
        - keywords: ["故障", "bug", "紧急"]
          response: "收到故障报告，已紧急通知 Ryan！"
        - keywords: ["API", "接口文档"]
          response: "相关 API 文档在这里：[链接] 我先发给你参考。"
      compound: []
```

**方案 B：分散式**

```
~/.hermes/proxy/
├── config.yaml            # 全局配置 + 默认行为
└── groups/
    ├── 业主群_12345@chatroom.yaml
    ├── 工作群_67890@chatroom.yaml
    └── 家庭群_abcd@chatroom.yaml
```

方案选择：推荐**方案 A（集中式）**，便于管理和修改时原子性写入。

### 3.3 群 ID 获取

群 ID 可通过以下方式获得：

1. **自动检测** — 当用户在群里发消息时，WeChat Adapter 收到的 `room_id` 即为群 ID
2. **指令查询** — 用户在群里发 `/proxy status`，机器人返回当前群 ID

---

## 4. 核心模块设计

### 4.1 Condition Engine（条件引擎）

```python
class ConditionEngine:
    """
    条件引擎：评估一组条件是否满足代理回复要求。
    所有条件为 AND 关系，全部通过才回复。
    """

    def evaluate(
        self,
        group_config: GroupConfig,
        message: MessageEvent,
        user_status: UserStatus,
    ) -> EvaluationResult:
        """
        返回:
          - passed: bool
          - reason: str  (失败原因，用于日志)
          - matched_topic: Optional[str]  (匹配的话题回复)
          - response_text: Optional[str]  (要回复的文本)
        """
```

条件评估顺序（短路优化）：

```
1. 群是否启用？              → 否则跳过
2. 时间段是否匹配？          → 否则跳过
3. 在线状态是否匹配？        → 否则跳过
4. 触发条件是否匹配？        → 否则跳过
   ├── @提及 触发
   ├── 关键词触发
   └── @所有人 触发
5. 匹配话题指令              → 选择对应回复
6. 生成回复（前缀 + 指令 + 签名）
```

### 4.2 Online Status Detector（在线状态检测器）

三种检测模式：

#### 模式 A：Passive（被动推断）

```
原理：基于用户最后活跃时间推断在线状态。

数据源：
  - 用户在各群的最后发言时间（从 WeChat Adapter 消息中提取）
  - 用户 DM 机器人的最后时间
  
算法：
  - 维护一个 HashMap: user_id → last_active_timestamp
  - 每次用户发出消息（任何群或 DM），更新时间戳
  - 当前时间 - last_active > timeout → 视为 offline
  - 否则视为 online

优点：无额外依赖
缺点：不精确（用户可能在看微信但不说话）
```

#### 模式 B：Manual（手动设置）

```
用户通过以下方式手动设置在线状态：

1. 聊天指令：
   /proxy online          # 设置为在线（默认回复自己）
   /proxy away            # 设置为离开状态
   /proxy offline         # 设置为离线（开启代理回复）
   /proxy status          # 查看当前状态

2. HTTP API（可选扩展）：
   POST /api/proxy/status
   {"status": "offline", "user_id": "..."}

优点：精确可控
缺点：需要用户手动操作
```

#### 模式 C：Hybrid（混合模式 — 推荐）

```
逻辑：
  - 用户手动设置状态时，以手动为准
  - 未手动设置时，自动推断
  - 用户手动设置 "away" 持续 N 分钟后，自动回退到推断模式

优先级：manual > passive
```

### 4.3 Time Matcher（时间段匹配器）

```python
class TimeMatcher:
    """
    检查当前时间是否在配置的时间段内。
    支持：星期几、时分范围、节假日排除（可选）。
    """

    def is_in_schedule(self, time_ranges: list, timezone: str) -> bool:
        """
        1. 获取当前指定时区的时间
        2. 获取今天是星期几
        3. 遍历 time_ranges，检查是否有匹配的 day + time 范围
        4. 任一匹配 → True
        """
```

### 4.4 Topic Matcher（话题匹配器）

```python
class TopicMatcher:
    """
    将消息文本与配置的关键词进行匹配，选出最合适的回复指令。
    """

    def match(
        self,
        text: str,
        topic_responses: list,
        compound_rules: list,
    ) -> Optional[MatchedResponse]:
        """
        匹配策略：
          1. 先检查 compound rules（多条件组合）
          2. 再检查单个 topic 的关键词
          3. 关键词匹配采用：包含匹配（非严格分词）
          4. 若多个关键词组都匹配，选关键词最多的那个
          5. 若无任何匹配，返回 None（使用 default reply）
        """
```

### 4.5 Proxy Reply Handler（代理回复处理器）

这是主要的入口，作为 WeChat Adapter 的消息处理 hook。

```python
class ProxyReplyHandler:
    """
    代理回复处理器，挂载到 WeChat Adapter 的消息流水线中。
    """

    def __init__(self, config_path: str):
        self.engine = ConditionEngine()
        self.status_detector = OnlineStatusDetector()
        self.config = ConfigLoader(config_path)

    async def handle_group_message(
        self,
        message: MessageEvent,
        adapter: WeixinAdapter,
    ) -> bool:
        """
        处理群消息。返回 True 表示已代理回复，False 表示未处理。

        流水线：
          1. 加载该群的配置
          2. 引擎评估条件
          3. 若通过 → 生成回复文本 → 通过 adapter 发送
          4. 若未通过 → 返回 False，允许原有流程继续
        """

    def _build_reply(
        self,
        instruction: str,
        config: GroupConfig,
    ) -> str:
        """
        组装回复文本:
          [prefix] + instruction + [signature]
        """
```

---

## 5. 集成方案

### 5.1 作为 Gateway 插件

首选方案：将本功能实现为一个 **Hermes Gateway Plugin**，挂载到 WeChat 平台的 `on_message` 事件。

```python
# 伪代码 — gateway/plugins/proxy_reply/plugin.py

class ProxyReplyPlugin:
    def __init__(self, gateway):
        self.gateway = gateway
        self.handler = ProxyReplyHandler()

    async def on_message(self, event: MessageEvent):
        """注册到 gateway 的 message 事件钩子"""
        if event.source.chat_type != "group":
            return  # 仅处理群消息

        if event.source.platform != "weixin":
            return  # 仅处理微信

        handled = await self.handler.handle_group_message(event, ...)
        if handled:
            # 已由代理回复，阻止后续 AI 处理
            event.stop_propagation()
```

### 5.2 作为 Skill

备选方案：将本功能封装为 **Hermes Skill**，加载到系统提示中，让 AI Agent 自主判断是否代理回复。

缺点：依赖 LLM 判断，延迟高、成本高、不可控。
优点：灵活性高，可以处理复杂语义。

**推荐使用 Plugin 方案**，Skill 仅用于辅助说明用户偏好。

### 5.3 配置管理

```python
class ConfigManager:
    """
    配置管理器：加载、验证、热更新配置。
    """

    CONFIG_PATH = "~/.hermes/proxy/config.yaml"

    def load(self) -> ProxyConfig:
        """加载配置，验证结构完整性"""

    def reload(self) -> bool:
        """热重载配置（不重启 gateway）"""

    def get_group_config(self, group_id: str) -> Optional[GroupConfig]:
        """获取指定群的配置"""

    def validate(self, config: dict) -> ValidationResult:
        """校验配置字段合法性"""
```

---

## 6. 用户交互界面

### 6.1 聊天指令（在群聊中通过 @机器人 触发）

| 指令 | 功能 |
|------|------|
| `/proxy status` | 查看当前群的代理配置状态 |
| `/proxy on` | 启用当前群的代理回复 |
| `/proxy off` | 禁用当前群的代理回复 |
| `/proxy away` | 设置"离开"状态（开启代理） |
| `/proxy back` | 设置"回来"状态（关闭代理） |
| `/proxy config` | 查看当前群完整配置 |

### 6.2 配置文件管理

用户通过编辑 YAML 文件来管理详细配置，支持热重载：

```bash
# 编辑配置
vim ~/.hermes/proxy/config.yaml

# 触发重载
hermes proxy reload
# 或通过微信发送: /proxy reload
```

---

## 7. 实施计划

### Phase 1：基础框架（2-3 天）

- [ ] 实现配置加载器（YAML → Pydantic Model）
- [ ] 实现 Condition Engine 核心
- [ ] 实现 Time Matcher
- [ ] 实现 Topic Matcher
- [ ] 单元测试

### Phase 2：Gateway 集成（2 天）

- [ ] 创建 ProxyReplyHandler
- [ ] 挂载到 WeChat Adapter 的消息流水线
- [ ] 实现 Passive 在线状态检测
- [ ] 实现代理回复发送
- [ ] 集成测试

### Phase 3：用户交互（1 天）

- [ ] 实现 Slash Commands（/proxy on/off/status）
- [ ] 实现配置热重载
- [ ] 实现 Manual 模式在线状态设置
- [ ] 错误处理与日志

### Phase 4：增强（可选）

- [ ] HTTP API 接口
- [ ] Web 管理面板
- [ ] 节假日排除
- [ ] 回复模板变量（{{user_name}}、{{time}} 等）
- [ ] 多语言支持
- [ ] 回复历史记录

---

## 8. 边界情况与风险

| 风险 | 缓解措施 |
|------|---------|
| 代理回复与用户本人回复冲突 | 条件引擎保证只有用户 offline 时触发；用户发言后重置 offline 计时器 |
| 关键词误触发 | 提供 `at_mention_only` 选项；支持排除词 `stop_words` |
| 配置写错导致异常行为 | 配置校验器 + 错误时 fallback 到安全默认值 |
| 回复过于频繁引起群友反感 | 内置频率限制：同一群每分钟最多 1 条代理回复 |
| iLink 不转发群消息 | 这是 iLink 平台限制，无法绕过；需使用公众号或企微方案 |
| 用户突然上线但代理仍在回复 | 在线状态实时更新，用户发一条消息立即恢复 online 状态 |

---

## 9. 附录：配置模板文件

```yaml
# ~/.hermes/proxy/config.yaml
# 完整配置模板，供用户直接使用

enabled: true
timezone: "Asia/Shanghai"

online_status:
  mode: hybrid
  passive:
    inactivity_timeout_minutes: 30
    source: last_message
  manual:
    webhook: true
    slash_commands: true

proxy_marker:
  prefix_enabled: true
  prefix_text: "🤖 [代班] "
  signature_enabled: false
  signature_text: ""

default_reply: "您好，Ryan 暂时不在，他看到消息后会尽快回复您 🙏"

# 每个群的配置
groups:
  # "群ID":
  #   enabled: true/false
  #   display_name: "群名称(仅用于标识)"
  #   schedule:
  #     enabled: true/false
  #     time_ranges:
  #       - days: [mon, tue, wed, thu, fri, sat, sun]
  #         start: "09:00"
  #         end: "18:00"
  #   online_status:
  #     reply_when: offline_only  # always | online_only | offline_only
  #   triggers:
  #     at_mention: true
  #     keywords: []
  #     stop_words: []
  #   instructions:
  #     default: "..."
  #     topic_responses:
  #       - keywords: ["关键词1", "关键词2"]
  #         response: "对应的回复文本"
```
