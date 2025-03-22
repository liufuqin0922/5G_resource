from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Resource5G, User

class Resource5GResource(resources.ModelResource):
    """5G资源导入导出资源类"""
    # 处理外键字段
    user = fields.Field(
        column_name="user",
        attribute="user",
        widget=ForeignKeyWidget(User, "username")
    )

    # 资源类型显示名称
    resource_type_display = fields.Field(
        column_name="资源类型",
        attribute="get_resource_type_display"
    )

    # 状态显示
    status_display = fields.Field(
        column_name="状态",
        attribute="status"
    )

    class Meta:
        model = Resource5G
        fields = ("id", "name", "resource_type", "resource_type_display", 
                  "description", "location", "quantity", "status", 
                  "status_display", "user", "created_at", "updated_at")
        export_order = ("id", "name", "resource_type_display", "description", 
                        "location", "quantity", "status_display", "user", 
                        "created_at", "updated_at")

    def dehydrate_status_display(self, resource5g):
        """处理状态字段的显示"""
        return "可用" if resource5g.status else "不可用"
        
    def before_import_row(self, row, **kwargs):
        """导入前处理行数据"""
        # 将资源类型的显示名称转换为存储值
        resource_type_map = {
            "网络资源": "network",
            "频谱资源": "spectrum",
            "设备资源": "device",
        }
        if "资源类型" in row:
            row["resource_type"] = resource_type_map.get(row["资源类型"], "network")
            
        # 将状态的显示名称转换为布尔值
        if "状态" in row:
            row["status"] = True if row["状态"] == "可用" else False
