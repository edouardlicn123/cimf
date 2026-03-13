# Taxonomy 模块计划

## 一、概述

Taxonomy（词汇表）模块用于管理下拉选项集合，类似于 Drupal 的 Taxonomy 模块。

## 二、模块结构

```
app/modules/taxonomy/
├── __init__.py              # 模块注册器
├── models.py                # 数据模型
├── service.py               # 服务层
├── routes.py                # 路由
├── forms.py                 # 表单
└── templates/
    ├── taxonomies.html      # 词汇表列表
    ├── taxonomy_edit.html   # 词汇表编辑
    └── taxonomy_item.html   # 词汇项编辑
```

## 三、数据模型

### 3.1 Taxonomy (词汇表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 词汇表名称 |
| slug | String | URL 标识 |
| description | String | 描述 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.2 TaxonomyItem (词汇项)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| taxonomy_id | Integer | 关联 Taxonomy |
| name | String | 词汇名称 |
| description | String | 描述（可选） |
| weight | Integer | 排序权重 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 四、预置分类数据

系统初始化时自动创建以下分类：

| 分类名称 | Slug | 词汇项 |
|----------|------|--------|
| 性别 | gender | 男、女、其他 |
| 国家/地区 | country | 全部国家/地区（按拼音排序）|
| 客户类型 | customer_type | 潜在客户、正式客户、VIP客户 |
| 项目状态 | project_status | 进行中、已完成、已暂停、已取消 |
| 项目阶段 | project_phase | 需求调研、方案设计、开发中、测试阶段、验收阶段、交付完成 |
| 优先级 | priority | 高、中、低 |
| 部门 | department | 销售部、技术部、财务部、行政部 |
| 合同状态 | contract_status | 草稿、审批中、已签署、已到期 |
| 付款状态 | payment_status | 未付款、部分付款、已付清 |
| 客户跟进状态 | followup_status | 待联系、已联系、沟通中、意向明确、已报价、已签约、已流失 |
| 任务状态 | task_status | 待开始、进行中、待审核、已完成、已延期、已取消 |
| 风险等级 | risk_level | 低风险、中风险、高风险、严重 |
| 企业规模 | company_size | 小型(1-50人)、中型(51-500人)、大型(501-2000人)、超大型(2000人+) |
| 户籍类型 | household_type | 本地户籍、常住人口、流动人口、暂住证 |
| 居住状况 | residence_status | 自有住房、租房、借住、集体宿舍 |
| 社保状态 | insurance_status | 已缴纳、缴纳中、断缴、未缴纳 |
| 婚姻状况 | marital_status | 未婚、已婚、离异、丧偶 |
| 文化程度 | education_level | 小学、初中、高中/中专、大专、本科、硕士、博士 |

### 国家/地区列表（按拼音排序）

```
阿富汗、阿尔巴尼亚、阿尔及利亚、阿拉伯联合酋长国、阿根廷、亚美尼亚、澳大利亚、
奥地利、阿塞拜疆、巴哈马、巴林、孟加拉国、巴巴多斯、白俄罗斯、比利时、伯利兹、
贝宁、不丹、玻利维亚、波斯尼亚和黑塞哥维那、博茨瓦纳、巴西、文莱、保加利亚、
布基纳法索、布隆迪、喀麦隆、加拿大、佛得角、中非共和国、乍得、智利、中国、
哥伦比亚、科摩罗、刚果共和国、刚果民主共和国、哥斯达黎加、科特迪瓦、克罗地亚、
古巴、塞浦路斯、捷克、丹麦、多米尼加共和国、厄瓜多尔、埃及、萨尔瓦多、赤道几内亚、
厄立特里亚、爱沙尼亚、斯威士兰、埃塞俄比亚、斐济、芬兰、法国、加蓬、冈比亚、
格鲁吉亚、德国、加纳、希腊、格林纳达、危地马拉、几内亚、几内亚比绍、圭亚那、
海地、梵蒂冈、洪都拉斯、匈牙利、冰岛、印度、印度尼西亚、伊朗、伊拉克、爱尔兰、
以色列、意大利、牙买加、日本、约旦、哈萨克斯坦、肯尼亚、基里巴斯、朝鲜、韩国、
科威特、吉尔吉斯斯坦、老挝、拉脱维亚、黎巴嫩、莱索托、利比里亚、利比亚、列支敦士登、
立陶宛、卢森堡、马达加斯加、马拉维、马来西亚、马尔代夫、马里、马耳他、毛里塔尼亚、
毛里求斯、墨西哥、密克罗尼西亚、摩尔多瓦、摩纳哥、蒙古、黑山、摩洛哥、莫桑比克、
缅甸、纳米比亚、瑙鲁、尼泊尔、荷兰、新西兰、尼加拉瓜、尼日尔、尼日利亚、北马其顿、
挪威、阿曼、巴基斯坦、帕劳、巴拿马、巴布亚新几内亚、巴拉圭、秘鲁、菲律宾、波兰、
葡萄牙、卡塔尔、罗马尼亚、俄罗斯、卢旺达、圣基茨和尼维斯、圣卢西亚、圣文森特和格林纳丁斯、
萨摩亚、圣马力诺、沙特阿拉伯、塞内加尔、塞尔维亚、塞舌尔、塞拉利昂、新加坡、
斯洛伐克、斯洛文尼亚、索马里、南非、南苏丹、西班牙、斯里兰卡、苏丹、苏里南、瑞典、
瑞士、叙利亚、台湾省、塔吉克斯坦、坦桑尼亚、泰国、多哥、汤加、特立尼达和多巴哥、
突尼斯、土耳其、土库曼斯坦、图瓦卢、乌干达、乌克兰、英国、美国、乌拉圭、乌兹别克斯坦、
瓦努阿图、梵蒂冈、委内瑞拉、越南、也门、赞比亚、津巴布韦
```

## 五、服务层

### TaxonomyService

```python
class TaxonomyService:
    @staticmethod
    def get_all_taxonomies():
        """获取所有词汇表"""
        pass
    
    @staticmethod
    def get_taxonomy_by_id(taxonomy_id):
        """获取词汇表详情"""
        pass
    
    @staticmethod
    def get_taxonomy_by_slug(slug):
        """通过 slug 获取词汇表"""
        pass
    
    @staticmethod
    def create_taxonomy(data):
        """创建词汇表"""
        pass
    
    @staticmethod
    def update_taxonomy(taxonomy_id, data):
        """更新词汇表"""
        pass
    
    @staticmethod
    def delete_taxonomy(taxonomy_id):
        """删除词汇表"""
        pass
    
    # 词汇项管理
    @staticmethod
    def get_items(taxonomy_id):
        """获取词汇表的所有词汇项"""
        pass
    
    @staticmethod
    def create_item(taxonomy_id, data):
        """创建词汇项"""
        pass
    
    @staticmethod
    def update_item(item_id, data):
        """更新词汇项"""
        pass
    
    @staticmethod
    def delete_item(item_id):
        """删除词汇项"""
        pass
    
    @staticmethod
    def reorder_items(taxonomy_id, item_ids):
        """重新排序词汇项"""
        pass
    
    # 初始化预置数据
    @staticmethod
    def init_default_taxonomies():
        """初始化预置分类数据"""
        pass
    
    # AI 功能预留
    @staticmethod
    def generate_items_ai(taxonomy_id, count=10):
        """AI 生成词汇项（预留接口）"""
        pass
```

## 六、路由

| 方法 | URL | 说明 |
|------|-----|------|
| GET | `/nodes/taxonomies` | 词汇表列表 |
| POST | `/nodes/taxonomies` | 创建词汇表 |
| GET | `/nodes/taxonomies/<id>` | 查看词汇表及词汇项 |
| PUT | `/nodes/taxonomies/<id>` | 更新词汇表 |
| DELETE | `/nodes/taxonomies/<id>` | 删除词汇表 |
| POST | `/nodes/taxonomies/<id>/items` | 新增词汇项 |
| PUT | `/nodes/taxonomies/<id>/items/<item_id>` | 更新词汇项 |
| DELETE | `/nodes/taxonomies/<id>/items/<item_id>` | 删除词汇项 |
| POST | `/nodes/taxonomies/<id>/ai-generate` | AI 生成词汇项（预留）|

## 七、前端界面

### 7.1 词汇表列表页

采用折叠面板设计：

```
词汇表列表
├── 客户类型（点击展开）
│   ├── [编辑] [删除]
│   ├── 词汇项表格
│   │   ├── 潜在客户 [编辑] [删除]
│   │   ├── 正式客户 [编辑] [删除]
│   │   └── VIP客户 [编辑] [删除]
│   ├── [+ 新增词汇项]
│   └── [🤖 AI 生成] （预留）
├── 项目状态（点击展开）
│   └── ...
└── [+ 新增词汇表]
```

### 7.2 词汇表编辑页

- 名称输入
- Slug（自动生成或手动输入）
- 描述（可选）

### 7.3 词汇项管理

- 词汇项列表（支持拖拽排序）
- 批量新增
- 搜索过滤

## 八、字段关联

Taxonomy 需要与 NodeType 的字段关联：

1. 在字段类型中选择 `entity_reference` 或 `relation`
2. 在字段设置中选择关联类型为 `taxonomy`
3. 选择关联的词汇表

## 九、AI 功能预留

```python
# service.py 中预留接口
class TaxonomyService:
    @staticmethod
    def generate_items_ai(taxonomy_id, count=10):
        """AI 生成词汇项（预留接口）
        
        用户可通过 OpenCode 直接调用此接口生成词汇项
        """
        # TODO: 实现 AI 生成逻辑
        # 1. 根据词汇表名称和描述调用 AI
        # 2. 生成相关词汇项建议
        # 3. 返回生成的词汇项列表
        pass
```

## 十、实施步骤

### Step 1: 创建数据库模型

创建 `app/models/taxonomy.py`，添加 Taxonomy 和 TaxonomyItem 模型。
更新 `app/models/__init__.py` 导出新模型。

### Step 2: 创建服务层

创建 `app/modules/taxonomy/service.py`，包含 TaxonomyService 和预置数据初始化方法。

### Step 3: 创建表单

创建 `app/modules/taxonomy/forms.py`。

### Step 4: 创建路由

创建 `app/modules/taxonomy/routes.py`。

### Step 5: 创建模板

创建 `app/modules/taxonomy/templates/` 下的模板文件。

### Step 6: 注册 Blueprint

在 `app/routes/__init__.py` 中注册 taxonomy_bp。

### Step 7: 添加菜单入口

在管理界面添加词汇表管理入口。

### Step 8: 初始化预置数据

创建初始化脚本，导入 18 个预置分类数据。

## 十一、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-12 | 初始版本 |
| 1.1 | 2026-03-12 | 增加预置分类数据和初始化步骤 |
