from django import forms

from core.models import TaxonomyItem


class CustomerForm(forms.Form):
    """客户表单"""

    customer_name = forms.CharField(
        label="客户名称",
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入客户名称",
            }
        ),
    )

    customer_code = forms.CharField(
        label="客户代码",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入客户代码",
            }
        ),
    )

    customer_type = forms.ModelChoiceField(
        label="客户类型",
        queryset=TaxonomyItem.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    enterprise_name = forms.CharField(
        label="企业名称",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入企业名称",
            }
        ),
    )

    phone1 = forms.CharField(
        label="电话1",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入电话1",
            }
        ),
    )

    email1 = forms.EmailField(
        label="邮箱1",
        max_length=100,
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入邮箱1",
            }
        ),
    )

    phone2 = forms.CharField(
        label="电话2",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入电话2",
            }
        ),
    )

    email2 = forms.EmailField(
        label="邮箱2",
        max_length=100,
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入邮箱2",
            }
        ),
    )

    linkedin = forms.URLField(
        label="领英",
        max_length=200,
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入领英链接",
            }
        ),
    )

    country = forms.ModelChoiceField(
        label="国家",
        queryset=TaxonomyItem.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    province = forms.CharField(
        label="省份/城市",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入省份/城市",
            }
        ),
    )

    address = forms.CharField(
        label="详细地址",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入详细地址",
            }
        ),
    )

    postal_code = forms.CharField(
        label="邮政编码",
        max_length=10,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入邮政编码",
            }
        ),
    )

    industry = forms.CharField(
        label="所属行业",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入所属行业",
            }
        ),
    )

    enterprise_type = forms.ModelChoiceField(
        label="企业性质",
        queryset=TaxonomyItem.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    registered_capital = forms.DecimalField(
        label="注册资本",
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入注册资本",
            }
        ),
    )

    customer_level = forms.ModelChoiceField(
        label="客户等级",
        queryset=TaxonomyItem.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    has_whatsapp = forms.TypedChoiceField(
        label="WhatsApp",
        required=False,
        coerce=lambda x: {"True": True, "False": False}.get(x),
        empty_value=None,
        choices=[(None, "未检测"), ("True", "有"), ("False", "没有")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    credit_limit = forms.DecimalField(
        label="信用额度",
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入信用额度",
            }
        ),
    )

    website = forms.URLField(
        label="网站",
        max_length=200,
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入网站链接",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer_type"].queryset = TaxonomyItem.objects.filter(taxonomy__slug="customer_type")
        self.fields["country"].queryset = TaxonomyItem.objects.filter(taxonomy__slug="country")
        self.fields["enterprise_type"].queryset = TaxonomyItem.objects.filter(taxonomy__slug="economic_type")
        self.fields["customer_level"].queryset = TaxonomyItem.objects.filter(taxonomy__slug="customer_level")

    notes = forms.CharField(
        label="备注",
        max_length=2000,
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "请输入备注",
                "rows": 4,
            }
        ),
    )
