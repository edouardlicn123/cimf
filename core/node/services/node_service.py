from core.node.models import Node, NodeType
from core.services.base_service import BaseService


class NodeService(BaseService):
    model_class = Node

    @staticmethod
    def get_nodes(node_type_slug: str) -> list[Node]:
        node_type = NodeType.objects.filter(slug=node_type_slug).first()
        if not node_type:
            return []
        return Node.objects.filter(node_type=node_type)

    @staticmethod
    def get_node(node_type_slug: str, node_id: int) -> Node | None:
        return Node.objects.filter(id=node_id, node_type__slug=node_type_slug).first()

    @staticmethod
    def create_node(node_type_slug: str, _data: dict, user) -> Node | None:
        node_type = NodeType.objects.filter(slug=node_type_slug).first()
        if not node_type:
            return None

        node = Node.objects.create(node_type=node_type, created_by=user, updated_by=user)
        return node

    @staticmethod
    def update_node(node_id: int, data: dict) -> Node | None:
        node = Node.objects.filter(id=node_id).first()
        if not node:
            return None

        for key, value in data.items():
            if hasattr(node, key):
                setattr(node, key, value)
        node.save()
        return node

    @staticmethod
    def get_list(node_type_slug: str, search: str | None = None) -> list[Node]:
        from core.node.services.node_type_service import NodeTypeService  # noqa: PLC0415

        node_type = NodeTypeService.get_by_slug(node_type_slug)
        if not node_type:
            return []

        queryset = Node.objects.filter(node_type=node_type)

        if search:
            try:
                node_id = int(search)
                queryset = queryset.filter(id=node_id)
            except ValueError:
                pass

        return queryset.order_by("-created_at")
