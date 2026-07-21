"""
Node 节点系统模型，包含节点类型和节点主表
"""

from django.conf import settings
from django.db import models

from core.models import BaseModel, IsActiveMixin


class NodeType(BaseModel, IsActiveMixin):
    """节点类型模型"""

    name = models.CharField(max_length=100, verbose_name="节点类型名称")
    slug = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="标识符")
    description = models.CharField(max_length=500, blank=True, verbose_name="描述")
    icon = models.CharField(max_length=50, default="bi-folder", verbose_name="图标")
    author = models.CharField(max_length=100, blank=True, verbose_name="作者")
    fields_config = models.JSONField(default=list, verbose_name="字段配置")

    class Meta:
        db_table = "node_types"
        verbose_name = "节点类型"
        verbose_name_plural = "节点类型"
        ordering = ["name"]

    def __str__(self):
        return self.name or f"NodeType({self.pk})"

    def get_node_count(self):
        return self.nodes.count()


class Node(BaseModel):
    """节点主表"""

    node_type = models.ForeignKey(NodeType, on_delete=models.CASCADE, related_name="nodes", verbose_name="节点类型")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_nodes",
        verbose_name="创建人",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_nodes",
        verbose_name="更新人",
    )

    class Meta:
        db_table = "nodes"
        verbose_name = "节点"
        verbose_name_plural = "节点"
        ordering = ["-created_at"]

    def __str__(self):
        node_type_name = self.node_type.name if self.node_type_id else "?"
        return f"Node {self.id} ({node_type_name})"
