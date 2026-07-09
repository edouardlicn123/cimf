# LinkedIn 模块技术规范

> 文档版本：1.0  
> 创建日期：2026-04-12  
> 最后更新：2026-04-12

**状态**：暂无实施计划

---

## 一、概述

LinkedIn 模块用于管理 LinkedIn 账户信息，包括自动加好友、群发消息等功能。由于 LinkedIn 没有官方公开 API，本模块需要集成第三方服务（推荐 ConnectSafely）来实现自动化操作。

---

## 二、技术架构

### 2.1 第三方 API 选择

| 服务商 | 价格 | 功能 | 文档 |
|--------|------|------|------|
| ConnectSafely | $10/月 | 连接请求、消息、搜索 | [Docs](https://connectsafely.ai/docs/api) |
| OutX AI | 按消息数收费 | 消息发送 | [Docs](https://outx.ai/docs/linkedin-api) |

推荐使用 **ConnectSafely**，因为：
- 价格相对便宜（$10/月）
- API 功能完整
- 有 n8n、HubSpot 等集成
- 社区活跃

### 2.2 LinkedIn API 端点

```
连接请求: POST /linkedin/connect
        - profileId: 目标用户ID
        - customMessage: 自定义消息（最大300字符）
        - 频率限制: 90次/周

发送消息: POST /linkedin/messaging/send
        - recipientProfileId: 收件人ID
        - message: 消息内容
        - 频率限制: 100条/天

搜索用户: GET /linkedin/search/people
        - keyword: 搜索关键词
        - includeContact: true
```

---

## 三、数据模型

### 3.1 LinkedInAccount（账户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| account_name | CharField(100) | 账户名称（，用于识别） |
| api_key | CharField(255) | ConnectSafely API Key |
| linkedin_profile_id | CharField(100) | LinkedIn Profile ID |
| is_active | BooleanField | 是否启用 |
| daily_connect_limit | IntegerField | 每日加好友上限 |
| daily_message_limit | IntegerField | 每日消息上限 |
| today_connect_used | IntegerField | 今日已发送连接请求数 |
| today_message_used | IntegerField | 今日已发送消息数 |
| last_reset_date | DateField | 最后重置日期 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

### 3.2 LinkedInContact（联系人表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| account | ForeignKey(LinkedInAccount) | 所属账户 |
| linkedin_urn | CharField(100) | LinkedIn URN |
| public_id | CharField(100) | LinkedIn 公开ID |
| first_name | CharField(100) | 名 |
| last_name | CharField(100) | 姓 |
| company | CharField(255) | 公司 |
| title | CharField(255) | 职位 |
| location | CharField(255) | 地点 |
| connection_status | CharField(20) | 连接状态 |
| connection_date | DateTimeField | 成为好友时间 |
| notes | TextField | 备注 |
| tags | ManyToManyField(Tag) | 标签 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

**connection_status 选项**：
- `PENDING`：已发送请求，等待对方接受
- `CONNECTED`：已连接
- `UNCONNECTED`：未连接

### 3.3 LinkedInCampaign（营销活动表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| account | ForeignKey(LinkedInAccount) | 所属账户 |
| name | CharField(200) | 活动名称 |
| campaign_type | CharField(20) | 活动类型 |
| message_template | TextField | 消息模板 |
| target_contacts | ManyToManyField(LinkedInContact) | 目标联系人 |
| scheduled_at | DateTimeField | 计划执行时间 |
| started_at | DateTimeField | 实际开始时间 |
| completed_at | DateTimeField | 完成时间 |
| status | CharField(20) | 状态 |
| success_count | IntegerField | 成功数 |
| failed_count | IntegerField | 失败数 |
| created_by | ForeignKey(User) | 创建人 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

**campaign_type 选项**：
- `CONNECTION_REQUEST`：加好友
- `MESSAGE`：发送消息
- `FOLLOW_UP`：跟进消息

**status 选项**：
- `DRAFT`：草稿
- `SCHEDULED`：已计划
- `RUNNING`：执行中
- `COMPLETED`：已完成
- `PAUSED`：已暂停
- `CANCELLED`：已取消

### 3.4 LinkedInMessageLog（消息日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| campaign | ForeignKey(LinkedInCampaign) | 关联活动 |
| contact | ForeignKey(LinkedInContact) | 关联联系人 |
| message_type | CharField(20) | 消息类型 |
| message_content | TextField | 消息内容 |
| response_status | CharField(20) | 响应状态 |
| api_response | JSONField | API 响应内容 |
| sent_at | DateTimeField | 发送时间 |
| created_at | DateTimeField | 创建时间 |

---

## 四、服务层

### 4.1 LinkedInAccountService

```python
class LinkedInAccountService:
    def create_account(name, api_key, profile_id): 创建账户
    def update_account(account_id, **kwargs): 更新账户
    def delete_account(account_id): 删除账户
    def get_account(account_id): 获取账户
    def list_accounts(): 列出所有账户
    def check_limits(account_id): 检查当日限制
    def reset_daily_limits(account_id): 重置每日限制
```

### 4.2 LinkedInContactService

```python
class LinkedInContactService:
    def import_from_linkedin(account_id, contacts): 从LinkedIn导入联系人
    def add_contact(account_id, contact_data): 添加联系人
    def update_contact(contact_id, **kwargs): 更新联系人
    def delete_contact(contact_id): 删除联系人
    def get_contact(contact_id): 获取联系人
    def list_contacts(account_id, status=None): 列出联系人
    def search_contacts(account_id, keyword): 搜索联系人
    def add_tag(contact_id, tag_id): 添加标签
    def remove_tag(contact_id, tag_id): 移除标签
```

### 4.3 LinkedInCampaignService

```python
class LinkedInCampaignService:
    def create_campaign(account_id, campaign_data): 创建活动
    def update_campaign(campaign_id, **kwargs): 更新活动
    def delete_campaign(campaign_id): 删除活动
    def get_campaign(campaign_id): 获取活动
    def list_campaigns(account_id, status=None): 列出活动
    def start_campaign(campaign_id): 启动活动
    def pause_campaign(campaign_id): 暂停活动
    def cancel_campaign(campaign_id): 取消活动
    def get_campaign_stats(campaign_id): 获取活动统计
```

### 4.4 LinkedInAPIService

```python
class LinkedInAPIService:
    def __init__(account): 初始化
    
    def send_connection_request(profile_id, message=None): 发送连接请求
    def send_message(recipient_urn, message): 发送消息
    def search_people(keyword, limit=10): 搜索用户
    def get_connections(): 获取好友列表
    def get_profile(profile_id): 获取用户资料
    def check_relationship(profile_id): 检查关系状态
```

---

## 五、API 调用示例

### 5.1 发送连接请求

```python
import requests

def send_connection_request(api_key, profile_id, custom_message=None):
    url = "https://api.connectsafely.ai/linkedin/connect"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "profileId": profile_id,
        "customMessage": custom_message
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

### 5.2 发送消息

```python
def send_message(api_key, recipient_profile_id, message):
    url = "https://api.connectsafely.ai/linkedin/messaging/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipientProfileId": recipient_profile_id,
        "message": message
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

---

## 六、安全注意事项

### 6.1 API Key 安全

- 存储时使用加密（如 Django 的 `encrypted.CharField` 或环境变量）
- 不在代码中硬编码
- 定期轮换 API Key

### 6.2 频率限制

| 操作 | 限制 | 建议值 |
|------|------|--------|
| 连接请求 | 90次/周 | 10-15次/天 |
| 消息发送 | 100次/天 | 30-50次/天 |

### 6.3 风控策略

- 添加随机延迟（1-3秒）模拟人类行为
- 分散执行时间（不集中在同一时段）
- 监控账户健康状态
- 异常自动暂停

### 6.4 遵守 LinkedIn 服务条款

- 不过度自动化
- 保持真实互动
- 避免垃圾信息

---

## 七、模块目录结构

```
modules/linkedin/
├── __init__.py
├── module.py          # 模块定义
├── models.py         # 数据模型
├── forms.py         # 表单定义
├── services.py      # 服务层
├── views.py        # 视图函数
├── urls.py        # URL路由
├── admin.py       # Django Admin
├── apps.py        # App配置
├── migrations/
│   └── 0001_initial.py
└── templates/
    ├── linkedin/
    │   ├── account_list.html
    │   ├── account_edit.html
    │   ├── contact_list.html
    │   ├── contact_import.html
    │   ├── campaign_list.html
    │   ├── campaign_create.html
    │   ├── campaign_detail.html
    │   └── message_log.html
```

---

## 八、后续扩展

- **多账户轮换**：支持多账户轮流操作，分散风险
- **消息模板变量**：支持 `{{first_name}}`、`{{company}}` 等变量
- **A/B 测试**：对比不同消息模板的效果
- **AI 生成消息**：集成 AI 生成个性化消息
- **Analytics 看板**：展示营销效果统计

---

## 九、参考资料

- [ConnectSafely API 文档](https://connectsafely.ai/docs/api)
- [LinkedIn Automation 安全指南](https://connectsafely.ai/articles/is-linkedin-automation-safe-tos-scraping-guide)
- [LinkedIn Messaging API 2026](https://connectsafely.ai/articles/linkedin-messaging-api-complete-guide-2026)
