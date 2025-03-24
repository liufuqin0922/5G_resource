from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from datetime import datetime, date
from django.utils import timezone
from .models import DeviceArrival, DeviceDelivery, DeviceSecurityStatus, User

class DeviceArrivalResource(resources.ModelResource):
    """设备到货清单导入导出资源类"""
    created_by = fields.Field(
        column_name="创建人",
        attribute="created_by",
        widget=ForeignKeyWidget(User, "username")
    )
    
    # 添加日期字段的处理
    arrival_date = fields.Field(
        column_name='到货日期',
        attribute='arrival_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    
    # 添加项目名称字段
    project_name = fields.Field(
        column_name='项目名称',
        attribute='project_name',
    )
    
    # 添加设备型号字段
    device_model = fields.Field(
        column_name='设备型号',
        attribute='device_model',
    )
    
    # 添加条码字段
    barcode = fields.Field(
        column_name='条码',
        attribute='barcode',
    )
    
    class Meta:
        model = DeviceArrival
        fields = ('id', 'project_name', 'arrival_date', 'device_model', 'barcode', 'created_by')
        export_order = ('id', 'project_name', 'arrival_date', 'device_model', 'barcode', 'created_by')
        import_id_fields = ['barcode']  # 使用条码作为唯一标识
        skip_unchanged = True
    
    def before_import_row(self, row, **kwargs):
        """导入前处理行数据"""
        # 尝试查找各种可能的列名映射
        # 项目名称可能的列名
        project_name_fields = ['项目名称', '项目', '工程名称', '项目名', '工程', '工程名', '站点名称', '站点', '名称']
        # 到货日期可能的列名
        date_fields = ['到货日期', '日期', '时间', '到货时间', '安装日期', '入库日期', '入库时间']
        # 设备型号可能的列名
        model_fields = ['设备型号', '型号', '规格型号', '设备规格', '规格', '型号规格']
        # 条码可能的列名
        barcode_fields = ['条码', '设备条码', '设备编号', '编号', 'ID', 'SN', '序列号', '资产编号']
        
        # 查找并映射项目名称
        for field in project_name_fields:
            if field in row:
                row['项目名称'] = row[field]
                break
        
        # 查找并映射到货日期
        date_found = False
        for field in date_fields:
            if field in row and row[field]:
                row['到货日期'] = row[field]
                date_found = True
                break
        
        # 如果没有日期字段,设置为当前日期
        if not date_found or not row.get('到货日期'):
            row['到货日期'] = date.today().strftime('%Y-%m-%d')
        
        # 查找并映射设备型号
        for field in model_fields:
            if field in row:
                row['设备型号'] = row[field]
                break
        
        # 查找并映射条码
        for field in barcode_fields:
            if field in row:
                row['条码'] = row[field]
                break
        
        # 检查必要字段是否都有值,如果没有,提供默认值
        if not row.get('项目名称'):
            row['项目名称'] = '默认项目'
        
        if not row.get('设备型号'):
            row['设备型号'] = '未知型号'
        
        if not row.get('条码'):
            # 生成一个基于时间戳的唯一条码
            timestamp = int(datetime.now().timestamp())
            row['条码'] = f"AUTO-{timestamp}-{kwargs.get('row_number', 0)}"


class DeviceDeliveryResource(resources.ModelResource):
    """设备出货清单导入导出资源类"""
    created_by = fields.Field(
        column_name="创建人",
        attribute="created_by",
        widget=ForeignKeyWidget(User, "username")
    )
    
    # 添加日期字段的处理
    delivery_date = fields.Field(
        column_name='出货日期',
        attribute='delivery_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    
    # 添加设备型号字段
    device_model = fields.Field(
        column_name='设备型号',
        attribute='device_model',
    )
    
    # 添加条码字段
    barcode = fields.Field(
        column_name='条码',
        attribute='barcode',
    )
    
    # 添加接收单位字段
    recipient_unit = fields.Field(
        column_name='接收单位',
        attribute='recipient_unit',
    )
    
    # 添加接收人字段
    recipient = fields.Field(
        column_name='接收人',
        attribute='recipient',
    )
    
    class Meta:
        model = DeviceDelivery
        fields = ('id', 'delivery_date', 'device_model', 'barcode', 'recipient_unit', 'recipient', 'created_by')
        export_order = ('id', 'delivery_date', 'device_model', 'barcode', 'recipient_unit', 'recipient', 'created_by')
        import_id_fields = ['barcode']  # 使用条码作为唯一标识
        skip_unchanged = True

    def before_import_row(self, row, **kwargs):
        """导入前处理行数据"""
        # 尝试查找各种可能的列名映射
        # 出货日期可能的列名
        date_fields = ['出货日期', '日期', '时间', '出货时间', '交付日期', '交付时间']
        # 设备型号可能的列名
        model_fields = ['设备型号', '型号', '规格型号', '设备规格', '规格', '型号规格']
        # 条码可能的列名
        barcode_fields = ['条码', '设备条码', '设备编号', '编号', 'ID', 'SN', '序列号', '资产编号']
        # 接收单位可能的列名
        unit_fields = ['接收单位', '单位', '收货单位', '收货方', '目标单位', '客户单位', '客户']
        # 接收人可能的列名
        recipient_fields = ['接收人', '收货人', '签收人', '负责人', '客户联系人']
        
        # 查找并映射出货日期
        date_found = False
        for field in date_fields:
            if field in row and row[field]:
                row['出货日期'] = row[field]
                date_found = True
                break
        
        # 如果没有日期字段,设置为当前日期
        if not date_found or not row.get('出货日期'):
            row['出货日期'] = date.today().strftime('%Y-%m-%d')
        
        # 查找并映射设备型号
        for field in model_fields:
            if field in row:
                row['设备型号'] = row[field]
                break
        
        # 查找并映射条码
        for field in barcode_fields:
            if field in row:
                row['条码'] = row[field]
                break
        
        # 查找并映射接收单位
        for field in unit_fields:
            if field in row:
                row['接收单位'] = row[field]
                break
        
        # 查找并映射接收人
        for field in recipient_fields:
            if field in row:
                row['接收人'] = row[field]
                break
        
        # 检查必要字段是否都有值,如果没有,提供默认值
        if not row.get('设备型号'):
            row['设备型号'] = '未知型号'
        
        if not row.get('条码'):
            # 生成一个基于时间戳的唯一条码
            timestamp = int(datetime.now().timestamp())
            row['条码'] = f"AUTO-{timestamp}-{kwargs.get('row_number', 0)}"
        
        if not row.get('接收单位'):
            row['接收单位'] = '未指定单位'
        
        if not row.get('接收人'):
            row['接收人'] = '未指定接收人'


class DeviceSecurityStatusResource(resources.ModelResource):
    """设备安全状态导入导出资源类"""
    created_by = fields.Field(
        column_name="创建人",
        attribute="created_by",
        widget=ForeignKeyWidget(User, "username")
    )
    
    # 网元名称字段
    network_element_name = fields.Field(
        column_name='网元名称',
        attribute='network_element_name',
    )
    
    # 在线状态字段
    is_online = fields.Field(
        column_name='在线状态',
        attribute='is_online',
    )
    
    # 资产序列号字段
    asset_serial_number = fields.Field(
        column_name='资产序列号',
        attribute='asset_serial_number',
    )
    
    # 检查日期字段
    check_date = fields.Field(
        column_name='检查日期',
        attribute='check_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    
    # 最后检查时间字段
    last_check_time = fields.Field(
        column_name='最后检查时间',
        attribute='last_check_time',
        widget=DateWidget(format='%Y-%m-%d')
    )
    
    class Meta:
        model = DeviceSecurityStatus
        fields = ('id', 'network_element_name', 'is_online', 'asset_serial_number', 'check_date', 'last_check_time', 'created_by')
        export_order = ('id', 'network_element_name', 'is_online', 'asset_serial_number', 'check_date', 'last_check_time', 'created_by')
        import_id_fields = ['asset_serial_number']  # 使用资产序列号作为唯一标识
        skip_unchanged = True
    
    def dehydrate_online_status_display(self, device_status):
        """处理在线状态字段的显示"""
        return "在线" if device_status.is_online else "离线"
        
    def before_import_row(self, row, **kwargs):
        """导入前处理行数据"""
        # 尝试查找各种可能的列名映射
        # 网元名称可能的列名
        name_fields = ['网元名称', '名称', '设备名称', '网元', '设备']
        # 在线状态可能的列名
        status_fields = ['在线状态', '状态', '是否在线', '在线', '运行状态']
        # 资产序列号可能的列名
        serial_fields = ['资产序列号', '序列号', 'SN', 'S/N', '编号', '资产编号']
        # 检查日期可能的列名
        check_date_fields = ['检查日期', '检查时间', '更新时间', '状态更新时间']
        # 最后检查时间可能的列名
        check_time_fields = ['最后检查时间', '检查时间', '更新时间', '状态更新时间']
        
        # 查找并映射网元名称
        for field in name_fields:
            if field in row:
                row['网元名称'] = row[field]
                break
        
        # 查找并映射资产序列号
        serial_found = False
        serial_value = None
        for field in serial_fields:
            if field in row and row[field]:
                row['资产序列号'] = row[field]
                serial_value = row[field]
                serial_found = True
                break
        
        # 如果资产序列号为空或不存在，标记这行跳过导入
        if not serial_found or not serial_value or not str(serial_value).strip():
            # 根据django-import-export库的机制，通过将必需字段设置为空以防止这行被导入
            row['资产序列号'] = None
            # 提前返回，不处理后续逻辑
            return
        
        # 有资产序列号的记录自动设置为在线
        row['在线状态'] = True
        
        # 查找并映射检查日期
        check_date_found = False
        for field in check_date_fields:
            if field in row and row[field]:
                row['检查日期'] = row[field]
                check_date_found = True
                break
        
        # 如果没有检查日期字段,设置为当前日期
        if not check_date_found or not row.get('检查日期'):
            row['检查日期'] = date.today().strftime('%Y-%m-%d')
        
        # 查找并映射最后检查时间
        check_time_found = False
        for field in check_time_fields:
            if field in row and row[field]:
                row['最后检查时间'] = row[field]
                check_time_found = True
                break
        
        # 如果没有检查时间字段,设置为当前日期
        if not check_time_found or not row.get('最后检查时间'):
            row['最后检查时间'] = date.today().strftime('%Y-%m-%d')
        
        # 检查必要字段是否都有值,如果没有,提供默认值
        if not row.get('网元名称'):
            row['网元名称'] = '未知网元'
