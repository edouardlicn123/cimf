# 01_WhatsApp 三模板随机发送实现方案

## 1. 需求概述

将 WhatsApp 发送功能从单模板改为三模板随机模式：发送界面提供三个模板选择器，每个可独立选择并可预览，允许重复选择同一模板；发送时从选中的模板列表中随机选择一个作为当条消息的内容。

## 2. 涉及文件

| # | 文件 | 变更类型 | 说明 |
|---|------|----------|------|
| 1 | `modules/whatsapp/models.py` | 修改 | `SendBatch` 新增 `template_ids` JSONField |
| 2 | `modules/whatsapp/services.py` | 修改 | `create_batch` 接收列表；发送函数随机选模板 |
| 3 | `modules/whatsapp/views.py` | 修改 | `api_send` 接收 `template_ids` 数组 |
| 4 | `modules/whatsapp/templates/whatsapp/send.html` | 修改 | 三模板选择器 + 三预览区 + JS 改造 |
| 5 | `modules/whatsapp/migrations/0004_sendbatch_template_ids.py` | 新增 | 自动生成迁移文件 |

## 3. 详细修改计划

### 3.1 `models.py` — SendBatch 新增字段

```python
class SendBatch(models.Model):
    # ... 现有字段不变 ...
    template_ids = models.JSONField(default=list, verbose_name='选中的模板ID列表')
```

- 保留 `template` FK 不变，用于向后兼容（已有数据和查询）
- `template_ids` 为空时，代码兜底使用 `[batch.template_id]`

### 3.2 `services.py` — 核心逻辑变更

#### 3.2.1 `create_batch(customer_ids, template_ids)`

- 签名：`template_id: int` → `template_ids: list[int]`
- 验证：检查所有模板 ID 都存在
- 存储：将 `template_ids` 存入 `batch.template_ids`
- `batch.template` FK 设为 `template_ids[0]` 对应的模板对象（保持向后兼容）

#### 3.2.2 新增辅助函数 `_pick_random_template(batch)`

```python
@staticmethod
def _pick_random_template(batch: SendBatch) -> WhatsAppTemplate:
    ids = batch.template_ids or [batch.template_id]
    template_id = random.choice(ids)
    return WhatsAppTemplate.objects.get(id=template_id)
```

#### 3.2.3 修改 `send_next_pending()` 第 279 行

原先：`template = batch.template`
改为：`template = WhatsAppService._pick_random_template(batch)`

#### 3.2.4 修改 `_send_next_log(batch, template)`

- 改为 `_send_next_log(batch)`，内部调用 `_pick_random_template` 获取模板
- 调用方（`_send_log_entry` 的 template 参数已由随机逻辑提供）

#### 3.2.5 `_send_log_entry(log, template)` 不变

该方法签名不变，每次传入的 `template` 已由调用方随机选择。

### 3.3 `views.py` — API 参数变更

#### 3.3.1 `api_send`

```python
template_id = data.get('template_id')           # 旧
template_ids = data.get('template_ids', [])      # 新

if not template_ids:
    return JsonResponse({'error': '请至少选择一个模板'}, status=400)
```

### 3.4 `send.html` — 模板和 JS 改造

#### 3.4.1 HTML 结构

将现有单选择器替换为三行，每行结构：

```
<div class="row g-3">
  <div class="col-12">
    <label class="form-label">模板 1</label>
    <div class="row">
      <div class="col-md-4">
        <select class="form-select template-select" data-index="1">...</select>
      </div>
      <div class="col-md-8">
        <div class="p-3 bg-light rounded preview-area" data-index="1">请选择模板查看内容</div>
      </div>
    </div>
  </div>
  <!-- 模板 2、模板 3 同上 -->
</div>
```

#### 3.4.2 JS 逻辑

- 模板变更事件绑定到 `.template-select`（用 class 而非 id）
- 预览更新使用 `data-index` 关联 select 和 preview
- 点击"发送"时收集三个选择器的值组成 `template_ids: [id1, id2, id3]`
- 过滤掉空值（未选择的模板不下发）
- `updateSendButton()` 改为：至少选了一个模板且至少选了一个客户才启用

## 4. 数据流

```
send.html                          views.py                       services.py
┌────────────────────────────┐    ┌──────────────────┐          ┌───────────────────────────┐
│ 模板1: [select ▼] [预览]   │    │                  │          │                           │
│ 模板2: [select ▼] [预览]   │───▶│  api_send        │─────────▶│  create_batch(ids)        │
│ 模板3: [select ▼] [预览]   │    │  template_ids[]  │          │  ├─ batch.template_ids=[]  │
│ 客户列表 [翻页]           │    │                  │          │  ├─ batch.template=ids[0] │
│ [发送消息]                │    └──────────────────┘          │  ├─ SendLog × N          │
└────────────────────────────┘                                 │  └─ _send_next_log()      │
                                                                                              
 cron 定时任务                                                 │                             
 ┌──────────────────┐                                          │  send_next_pending()      │
 │ send_next_pending│───▶ _pick_random_template(batch)         │  ├─ random.choice(ids)    │
 └──────────────────┘    ▶ _send_log_entry(log, template)      │  └─ 发送...               │
                                                               └───────────────────────────┘
```

## 5. 边界情况处理

| # | 场景 | 处理方式 |
|---|------|----------|
| 1 | `template_ids=[]`（旧数据） | 兜底用 `[batch.template_id]`，行为与改造前一致 |
| 2 | 三个选择器都选同一模板 | 允许，`template_ids=[5,5,5]`，随机永远返回模板 5 |
| 3 | 只选了一个模板 | 允许，`template_ids=[id]`，行为与改造前一致 |
| 4 | 客户列表翻页 | 模板选择器在独立 card 中，不受翻页影响 |
| 5 | 三个模板中有部分被删除 | `_pick_random_template` 过滤出仍存在的 ID；如全部不存在则抛异常并由外层 catch |

## 6. 不修改的部分

| 不修改 | 原因 |
|--------|------|
| `urls.py` | 路由不变 |
| `_process_send`（死代码） | 零引用 |
| `send_messages_async`（死代码） | 零引用 |
| `cron.py` | 只调 `send_next_pending()`，接口不变 |
| 模板管理页面 `manage.html` | 不涉及发送逻辑 |
| 日志页面 `logs.html` | 不涉及发送逻辑 |
