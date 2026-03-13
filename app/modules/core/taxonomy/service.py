# 文件路径：app/modules/taxonomy/service.py
# 功能说明：Taxonomy 词汇表服务层

from app import db
from app.models.core.taxonomy import Taxonomy, TaxonomyItem
from typing import List, Optional, Dict, Any


DEFAULT_TAXONOMIES = [
    {
        "name": "性别",
        "slug": "gender",
        "description": "性别分类",
        "items": ["男", "女", "其他"]
    },
    {
        "name": "客户类型",
        "slug": "customer_type",
        "description": "客户类型分类",
        "items": ["潜在客户", "正式客户", "VIP客户"]
    },
    {
        "name": "国家/地区",
        "slug": "country",
        "description": "世界各国和地区",
        "items": [
            "阿富汗", "阿尔巴尼亚", "阿尔及利亚", "阿拉伯联合酋长国", "阿根廷", "亚美尼亚", "澳大利亚",
            "奥地利", "阿塞拜疆", "巴哈马", "巴林", "孟加拉国", "巴巴多斯", "白俄罗斯", "比利时", "伯利兹",
            "贝宁", "不丹", "玻利维亚", "波斯尼亚和黑塞哥维那", "博茨瓦纳", "巴西", "文莱", "保加利亚",
            "布基纳法索", "布隆迪", "喀麦隆", "加拿大", "佛得角", "中非共和国", "乍得", "智利", "中国",
            "哥伦比亚", "科摩罗", "刚果共和国", "刚果民主共和国", "哥斯达黎加", "科特迪瓦", "克罗地亚",
            "古巴", "塞浦路斯", "捷克", "丹麦", "多米尼加共和国", "厄瓜多尔", "埃及", "萨尔瓦多",
            "赤道几内亚", "厄立特里亚", "爱沙尼亚", "斯威士兰", "埃塞俄比亚", "斐济", "芬兰", "法国",
            "加蓬", "冈比亚", "格鲁吉亚", "德国", "加纳", "希腊", "格林纳达", "危地马拉", "几内亚",
            "几内亚比绍", "圭亚那", "海地", "梵蒂冈", "洪都拉斯", "匈牙利", "冰岛", "印度", "印度尼西亚",
            "伊朗", "伊拉克", "爱尔兰", "以色列", "意大利", "牙买加", "日本", "约旦", "哈萨克斯坦",
            "肯尼亚", "基里巴斯", "朝鲜", "韩国", "科威特", "吉尔吉斯斯坦", "老挝", "拉脱维亚", "黎巴嫩",
            "莱索托", "利比里亚", "利比亚", "列支敦士登", "立陶宛", "卢森堡", "马达加斯加", "马拉维",
            "马来西亚", "马尔代夫", "马里", "马耳他", "毛里塔尼亚", "毛里求斯", "墨西哥", "密克罗尼西亚",
            "摩尔多瓦", "摩纳哥", "蒙古", "黑山", "摩洛哥", "莫桑比克", "缅甸", "纳米比亚", "瑙鲁",
            "尼泊尔", "荷兰", "新西兰", "尼加拉瓜", "尼日尔", "尼日利亚", "北马其顿", "挪威", "阿曼",
            "巴基斯坦", "帕劳", "巴拿马", "巴布亚新几内亚", "巴拉圭", "秘鲁", "菲律宾", "波兰", "葡萄牙",
            "卡塔尔", "罗马尼亚", "俄罗斯", "卢旺达", "圣基茨和尼维斯", "圣卢西亚", "圣文森特和格林纳丁斯",
            "萨摩亚", "圣马力诺", "沙特阿拉伯", "塞内加尔", "塞尔维亚", "塞舌尔", "塞拉利昂", "新加坡",
            "斯洛伐克", "斯洛文尼亚", "索马里", "南非", "南苏丹", "西班牙", "斯里兰卡", "苏丹", "苏里南",
            "瑞典", "瑞士", "叙利亚", "台湾省", "塔吉克斯坦", "坦桑尼亚", "泰国", "多哥", "汤加",
            "特立尼达和多巴哥", "突尼斯", "土耳其", "土库曼斯坦", "图瓦卢", "乌干达", "乌克兰", "英国",
            "美国", "乌拉圭", "乌兹别克斯坦", "瓦努阿图", "梵蒂冈", "委内瑞拉", "越南", "也门", "赞比亚", "津巴布韦"
        ]
    },
    {
        "name": "客户类型",
        "slug": "customer_type",
        "description": "客户类型分类",
        "items": ["潜在客户", "正式客户", "VIP客户"]
    },
    {
        "name": "项目状态",
        "slug": "project_status",
        "description": "项目状态分类",
        "items": ["进行中", "已完成", "已暂停", "已取消"]
    },
    {
        "name": "项目阶段",
        "slug": "project_phase",
        "description": "项目阶段分类",
        "items": ["需求调研", "方案设计", "开发中", "测试阶段", "验收阶段", "交付完成"]
    },
    {
        "name": "优先级",
        "slug": "priority",
        "description": "优先级分类",
        "items": ["高", "中", "低"]
    },
    {
        "name": "部门",
        "slug": "department",
        "description": "部门分类",
        "items": ["销售部", "技术部", "财务部", "行政部"]
    },
    {
        "name": "合同状态",
        "slug": "contract_status",
        "description": "合同状态分类",
        "items": ["草稿", "审批中", "已签署", "已到期"]
    },
    {
        "name": "付款状态",
        "slug": "payment_status",
        "description": "付款状态分类",
        "items": ["未付款", "部分付款", "已付清"]
    },
    {
        "name": "客户跟进状态",
        "slug": "followup_status",
        "description": "客户跟进状态分类",
        "items": ["待联系", "已联系", "沟通中", "意向明确", "已报价", "已签约", "已流失"]
    },
    {
        "name": "任务状态",
        "slug": "task_status",
        "description": "任务状态分类",
        "items": ["待开始", "进行中", "待审核", "已完成", "已延期", "已取消"]
    },
    {
        "name": "风险等级",
        "slug": "risk_level",
        "description": "风险等级分类",
        "items": ["低风险", "中风险", "高风险", "严重"]
    },
    {
        "name": "企业规模",
        "slug": "company_size",
        "description": "企业规模分类",
        "items": ["小型(1-50人)", "中型(51-500人)", "大型(501-2000人)", "超大型(2000人+)"]
    },
    {
        "name": "户籍类型",
        "slug": "household_type",
        "description": "户籍类型分类",
        "items": ["本地户籍", "常住人口", "流动人口", "暂住证"]
    },
    {
        "name": "居住状况",
        "slug": "residence_status",
        "description": "居住状况分类",
        "items": ["自有住房", "租房", "借住", "集体宿舍"]
    },
    {
        "name": "社保状态",
        "slug": "insurance_status",
        "description": "社保状态分类",
        "items": ["已缴纳", "缴纳中", "断缴", "未缴纳"]
    },
    {
        "name": "婚姻状况",
        "slug": "marital_status",
        "description": "婚姻状况分类",
        "items": ["未婚", "已婚", "离异", "丧偶"]
    },
    {
        "name": "文化程度",
        "slug": "education_level",
        "description": "文化程度分类",
        "items": ["小学", "初中", "高中/中专", "大专", "本科", "硕士", "博士"]
    }
]


class TaxonomyService:
    
    @staticmethod
    def get_all_taxonomies() -> List[Taxonomy]:
        """获取所有词汇表"""
        return Taxonomy.query.order_by(Taxonomy.id).all()
    
    @staticmethod
    def get_taxonomy_by_id(taxonomy_id: int) -> Optional[Taxonomy]:
        """获取词汇表详情"""
        return Taxonomy.query.get(taxonomy_id)
    
    @staticmethod
    def get_taxonomy_by_slug(slug: str) -> Optional[Taxonomy]:
        """通过 slug 获取词汇表"""
        return Taxonomy.query.filter_by(slug=slug).first()
    
    @staticmethod
    def create_taxonomy(data: Dict[str, Any]) -> Taxonomy:
        """创建词汇表"""
        taxonomy = Taxonomy(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description', '')
        )
        db.session.add(taxonomy)
        db.session.commit()
        return taxonomy
    
    @staticmethod
    def update_taxonomy(taxonomy_id: int, data: Dict[str, Any]) -> Optional[Taxonomy]:
        """更新词汇表"""
        taxonomy = Taxonomy.query.get(taxonomy_id)
        if taxonomy:
            taxonomy.name = data.get('name', taxonomy.name)
            taxonomy.slug = data.get('slug', taxonomy.slug)
            taxonomy.description = data.get('description', taxonomy.description)
            db.session.commit()
        return taxonomy
    
    @staticmethod
    def delete_taxonomy(taxonomy_id: int) -> bool:
        """删除词汇表（同时删除所有关联的词汇项）"""
        taxonomy = Taxonomy.query.get(taxonomy_id)
        if taxonomy:
            # 先删除所有关联的词汇项
            TaxonomyItem.query.filter_by(taxonomy_id=taxonomy_id).delete()
            # 再删除词汇表
            db.session.delete(taxonomy)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_items(taxonomy_id: int) -> List[TaxonomyItem]:
        """获取词汇表的所有词汇项"""
        return TaxonomyItem.query.filter_by(taxonomy_id=taxonomy_id).order_by(TaxonomyItem.weight, TaxonomyItem.name).all()
    
    @staticmethod
    def create_item(taxonomy_id: int, data: Dict[str, Any]) -> TaxonomyItem:
        """创建词汇项"""
        max_weight = db.session.query(db.func.max(TaxonomyItem.weight)).filter_by(taxonomy_id=taxonomy_id).scalar() or 0
        item = TaxonomyItem(
            taxonomy_id=taxonomy_id,
            name=data['name'],
            description=data.get('description', ''),
            weight=data.get('weight', max_weight + 1)
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    @staticmethod
    def update_item(item_id: int, data: Dict[str, Any]) -> Optional[TaxonomyItem]:
        """更新词汇项"""
        item = TaxonomyItem.query.get(item_id)
        if item:
            item.name = data.get('name', item.name)
            item.description = data.get('description', item.description)
            if 'weight' in data:
                item.weight = data['weight']
            db.session.commit()
        return item
    
    @staticmethod
    def delete_item(item_id: int) -> bool:
        """删除词汇项"""
        item = TaxonomyItem.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def reorder_items(taxonomy_id: int, item_ids: List[int]) -> bool:
        """重新排序词汇项"""
        for idx, item_id in enumerate(item_ids):
            item = TaxonomyItem.query.filter_by(id=item_id, taxonomy_id=taxonomy_id).first()
            if item:
                item.weight = idx
        db.session.commit()
        return True
    
    @staticmethod
    def init_default_taxonomies() -> None:
        """初始化预置分类数据"""
        for tax_data in DEFAULT_TAXONOMIES:
            # 检查是否已存在
            existing = Taxonomy.query.filter_by(slug=tax_data['slug']).first()
            if existing:
                continue
            
            taxonomy = Taxonomy(
                name=tax_data['name'],
                slug=tax_data['slug'],
                description=tax_data.get('description', '')
            )
            db.session.add(taxonomy)
            db.session.flush()
            
            for idx, item_name in enumerate(tax_data['items']):
                # 检查词汇项是否已存在
                existing_item = TaxonomyItem.query.filter_by(
                    taxonomy_id=taxonomy.id, name=item_name
                ).first()
                if existing_item:
                    continue
                    
                item = TaxonomyItem(
                    taxonomy_id=taxonomy.id,
                    name=item_name,
                    weight=idx
                )
                db.session.add(item)
        
        db.session.commit()
    
    @staticmethod
    def generate_items_ai(taxonomy_id: int, count: int = 10) -> List[str]:
        """AI 生成词汇项（预留接口）"""
        return []
