"""Domain models for a home renovation (装修) app.

The data model is intentionally small but covers the usual moving parts of a
renovation project:

* Project      - one renovation project (a house/apartment being renovated)
* Room         - the spaces inside the project (living room, kitchen, ...)
* Contractor   - designers, foremen and trades working on the project
* Task         - construction phases/tasks (demolition, plumbing, painting...)
* Material     - the shopping list of main/auxiliary materials and furniture
* Expense      - money actually spent, split by category
"""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Project(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "公寓"
        HOUSE = "house", "住宅"
        VILLA = "villa", "别墅"
        OFFICE = "office", "办公空间"
        OTHER = "other", "其他"

    class Status(models.TextChoices):
        PLANNING = "planning", "规划中"
        IN_PROGRESS = "in_progress", "施工中"
        PAUSED = "paused", "暂停"
        COMPLETED = "completed", "已完工"

    name = models.CharField("项目名称", max_length=120)
    address = models.CharField("地址", max_length=255, blank=True)
    property_type = models.CharField(
        "房屋类型", max_length=20, choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
    )
    area_sqm = models.DecimalField(
        "面积(㎡)", max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    budget = models.DecimalField(
        "预算(元)", max_digits=12, decimal_places=2, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    style = models.CharField("装修风格", max_length=60, blank=True)
    status = models.CharField(
        "状态", max_length=20, choices=Status.choices, default=Status.PLANNING,
    )
    start_date = models.DateField("开工日期", null=True, blank=True)
    expected_end_date = models.DateField("预计完工日期", null=True, blank=True)
    notes = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "装修项目"
        verbose_name_plural = "装修项目"

    def __str__(self):
        return self.name


class Room(models.Model):
    class RoomType(models.TextChoices):
        LIVING_ROOM = "living_room", "客厅"
        BEDROOM = "bedroom", "卧室"
        KITCHEN = "kitchen", "厨房"
        BATHROOM = "bathroom", "卫生间"
        BALCONY = "balcony", "阳台"
        STUDY = "study", "书房"
        OTHER = "other", "其他"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="rooms", verbose_name="项目",
    )
    name = models.CharField("空间名称", max_length=80)
    room_type = models.CharField(
        "空间类型", max_length=20, choices=RoomType.choices, default=RoomType.OTHER,
    )
    area_sqm = models.DecimalField(
        "面积(㎡)", max_digits=8, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    notes = models.TextField("备注", blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "空间"
        verbose_name_plural = "空间"
        constraints = [
            models.UniqueConstraint(fields=["project", "name"], name="unique_room_name_per_project"),
        ]

    def __str__(self):
        return f"{self.project.name} / {self.name}"


class Contractor(models.Model):
    class Role(models.TextChoices):
        DESIGNER = "designer", "设计师"
        FOREMAN = "foreman", "工长"
        PLUMBER = "plumber", "水电工"
        ELECTRICIAN = "electrician", "电工"
        CARPENTER = "carpenter", "木工"
        MASON = "mason", "泥瓦工"
        PAINTER = "painter", "油漆工"
        OTHER = "other", "其他"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contractors", verbose_name="项目",
    )
    name = models.CharField("姓名", max_length=80)
    phone = models.CharField("联系电话", max_length=32, blank=True)
    role = models.CharField("角色", max_length=20, choices=Role.choices, default=Role.OTHER)
    company = models.CharField("所属公司", max_length=120, blank=True)
    notes = models.TextField("备注", blank=True)

    class Meta:
        ordering = ["role", "name"]
        verbose_name = "施工人员"
        verbose_name_plural = "施工人员"

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


class Task(models.Model):
    class Phase(models.TextChoices):
        DESIGN = "design", "设计"
        DEMOLITION = "demolition", "拆改"
        WATER_ELECTRIC = "water_electric", "水电"
        MASONRY = "masonry", "泥瓦"
        CARPENTRY = "carpentry", "木工"
        PAINTING = "painting", "油漆"
        INSTALLATION = "installation", "安装"
        INSPECTION = "inspection", "验收"

    class Status(models.TextChoices):
        TODO = "todo", "待开始"
        IN_PROGRESS = "in_progress", "进行中"
        DONE = "done", "已完成"
        BLOCKED = "blocked", "受阻"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks", verbose_name="项目",
    )
    room = models.ForeignKey(
        Room, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tasks", verbose_name="空间",
    )
    assignee = models.ForeignKey(
        Contractor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tasks", verbose_name="负责人",
    )
    title = models.CharField("任务名称", max_length=120)
    phase = models.CharField("施工阶段", max_length=20, choices=Phase.choices)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.TODO)
    planned_start = models.DateField("计划开始", null=True, blank=True)
    planned_end = models.DateField("计划结束", null=True, blank=True)
    actual_start = models.DateField("实际开始", null=True, blank=True)
    actual_end = models.DateField("实际结束", null=True, blank=True)
    notes = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["planned_start", "id"]
        verbose_name = "施工任务"
        verbose_name_plural = "施工任务"

    def __str__(self):
        return self.title


class Material(models.Model):
    class Category(models.TextChoices):
        MAIN = "main", "主材"
        AUXILIARY = "auxiliary", "辅材"
        FURNITURE = "furniture", "家具"
        APPLIANCE = "appliance", "家电"

    class Status(models.TextChoices):
        PLANNED = "planned", "待采购"
        PURCHASED = "purchased", "已采购"
        DELIVERED = "delivered", "已到场"
        INSTALLED = "installed", "已安装"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="materials", verbose_name="项目",
    )
    room = models.ForeignKey(
        Room, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="materials", verbose_name="空间",
    )
    name = models.CharField("材料名称", max_length=120)
    brand = models.CharField("品牌", max_length=80, blank=True)
    model = models.CharField("型号", max_length=80, blank=True)
    category = models.CharField(
        "类别", max_length=20, choices=Category.choices, default=Category.MAIN,
    )
    quantity = models.DecimalField(
        "数量", max_digits=10, decimal_places=2, default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    unit = models.CharField("单位", max_length=20, default="件")
    unit_price = models.DecimalField(
        "单价(元)", max_digits=12, decimal_places=2, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    supplier = models.CharField("供应商", max_length=120, blank=True)
    status = models.CharField(
        "状态", max_length=20, choices=Status.choices, default=Status.PLANNED,
    )
    notes = models.TextField("备注", blank=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "材料"
        verbose_name_plural = "材料"

    @property
    def total_price(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))

    def __str__(self):
        return self.name


class Expense(models.Model):
    class Category(models.TextChoices):
        DESIGN = "design", "设计费"
        MATERIAL = "material", "材料费"
        LABOR = "labor", "人工费"
        MANAGEMENT = "management", "管理费"
        OTHER = "other", "其他"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="expenses", verbose_name="项目",
    )
    title = models.CharField("费用名称", max_length=120)
    category = models.CharField(
        "类别", max_length=20, choices=Category.choices, default=Category.OTHER,
    )
    amount = models.DecimalField(
        "金额(元)", max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    paid_at = models.DateField("支付日期", null=True, blank=True)
    note = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["-paid_at", "-id"]
        verbose_name = "费用记录"
        verbose_name_plural = "费用记录"

    def __str__(self):
        return f"{self.title} - {self.amount}"
