"""Create a small demo renovation project so the API has data to show."""
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from renovation.models import Contractor, Expense, Material, Project, Room, Task


class Command(BaseCommand):
    help = "Create demo data for the renovation API"

    def handle(self, *args, **options):
        project, created = Project.objects.get_or_create(
            name="阳光花园 3-2-501",
            defaults={
                "address": "阳光花园 3 栋 2 单元 501",
                "property_type": Project.PropertyType.APARTMENT,
                "area_sqm": Decimal("89.50"),
                "budget": Decimal("200000.00"),
                "style": "现代简约",
                "status": Project.Status.IN_PROGRESS,
                "start_date": date(2026, 3, 1),
                "expected_end_date": date(2026, 7, 15),
            },
        )
        if not created:
            self.stdout.write(self.style.WARNING(f"Project already exists: {project.name}"))
            return

        living_room = Room.objects.create(
            project=project, name="客厅", room_type=Room.RoomType.LIVING_ROOM,
            area_sqm=Decimal("25.00"),
        )
        kitchen = Room.objects.create(
            project=project, name="厨房", room_type=Room.RoomType.KITCHEN,
            area_sqm=Decimal("8.00"),
        )
        Room.objects.create(
            project=project, name="主卧", room_type=Room.RoomType.BEDROOM,
            area_sqm=Decimal("16.00"),
        )

        designer = Contractor.objects.create(
            project=project, name="李设计", role=Contractor.Role.DESIGNER,
            phone="13800000001", company="XX 设计工作室",
        )
        foreman = Contractor.objects.create(
            project=project, name="王工长", role=Contractor.Role.FOREMAN,
            phone="13800000002",
        )

        Task.objects.create(
            project=project, room=living_room, assignee=foreman,
            title="客厅拆改", phase=Task.Phase.DEMOLITION, status=Task.Status.DONE,
            planned_start=date(2026, 3, 1), planned_end=date(2026, 3, 5),
        )
        Task.objects.create(
            project=project, room=kitchen, assignee=foreman,
            title="厨房水电改造", phase=Task.Phase.WATER_ELECTRIC,
            status=Task.Status.IN_PROGRESS,
            planned_start=date(2026, 3, 6), planned_end=date(2026, 3, 15),
        )
        Task.objects.create(
            project=project, assignee=designer,
            title="软装方案确认", phase=Task.Phase.DESIGN, status=Task.Status.TODO,
            planned_start=date(2026, 6, 1), planned_end=date(2026, 6, 10),
        )

        Material.objects.create(
            project=project, room=living_room, name="强化复合地板",
            brand="圣象", category=Material.Category.MAIN,
            quantity=Decimal("30"), unit="㎡", unit_price=Decimal("159.00"),
            supplier="建材城 A 区", status=Material.Status.PURCHASED,
        )
        Material.objects.create(
            project=project, room=kitchen, name="石英石台面",
            brand="中讯", category=Material.Category.MAIN,
            quantity=Decimal("4"), unit="米", unit_price=Decimal("680.00"),
            status=Material.Status.PLANNED,
        )
        Material.objects.create(
            project=project, name="乳胶漆", brand="立邦",
            category=Material.Category.AUXILIARY,
            quantity=Decimal("6"), unit="桶", unit_price=Decimal("299.00"),
            status=Material.Status.DELIVERED,
        )

        Expense.objects.create(
            project=project, title="设计费", category=Expense.Category.DESIGN,
            amount=Decimal("8000.00"), paid_at=date(2026, 2, 20),
        )
        Expense.objects.create(
            project=project, title="拆改人工", category=Expense.Category.LABOR,
            amount=Decimal("3500.00"), paid_at=date(2026, 3, 5),
        )

        self.stdout.write(self.style.SUCCESS(f"Demo project created: {project.name} (id={project.id})"))
