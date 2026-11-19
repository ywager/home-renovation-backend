from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Expense, Material, Project, Room, Task


class RenovationApiTests(APITestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="阳光花园 3-2-501",
            address="阳光花园 3 栋 2 单元 501",
            area_sqm=Decimal("89.50"),
            budget=Decimal("200000.00"),
            status=Project.Status.IN_PROGRESS,
        )
        self.other_project = Project.objects.create(
            name="另一个项目", area_sqm=Decimal("50.00"), budget=Decimal("80000.00"),
        )
        self.living_room = Room.objects.create(
            project=self.project, name="客厅", room_type=Room.RoomType.LIVING_ROOM,
            area_sqm=Decimal("25.00"),
        )
        Room.objects.create(
            project=self.other_project, name="客厅", room_type=Room.RoomType.LIVING_ROOM,
        )

    def test_create_project(self):
        response = self.client.post(
            reverse("project-list"),
            {"name": "新房", "area_sqm": "66.00", "budget": "120000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 3)

    def test_project_requires_positive_area(self):
        response = self.client.post(
            reverse("project-list"),
            {"name": "错误面积", "area_sqm": "0"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("area_sqm", response.data)

    def test_rooms_can_be_filtered_by_project(self):
        response = self.client.get(reverse("room-list"), {"project": self.project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "客厅")
        self.assertEqual(results[0]["project_name"], self.project.name)

    def test_material_total_price_is_computed(self):
        material = Material.objects.create(
            project=self.project,
            name="乳胶漆",
            quantity=Decimal("3"),
            unit_price=Decimal("299.50"),
        )
        response = self.client.get(reverse("material-detail", args=[material.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data["total_price"]), Decimal("898.50"))

    def test_project_summary_aggregates_costs_and_progress(self):
        Material.objects.create(
            project=self.project, name="瓷砖", quantity=Decimal("20"),
            unit_price=Decimal("80"),
        )
        Expense.objects.create(project=self.project, title="设计费", amount=Decimal("5000"))
        Expense.objects.create(project=self.project, title="人工", amount=Decimal("12000"))
        Task.objects.create(
            project=self.project, title="水电改造", phase=Task.Phase.WATER_ELECTRIC,
            status=Task.Status.DONE,
        )
        Task.objects.create(
            project=self.project, title="墙面刷漆", phase=Task.Phase.PAINTING,
            status=Task.Status.TODO,
        )

        response = self.client.get(reverse("project-summary", args=[self.project.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data["material_cost"]), Decimal("1600.00"))
        self.assertEqual(Decimal(response.data["expense_total"]), Decimal("17000.00"))
        self.assertEqual(Decimal(response.data["budget_remaining"]), Decimal("181400.00"))
        self.assertEqual(response.data["task_total"], 2)
        self.assertEqual(response.data["task_done"], 1)
        self.assertEqual(response.data["task_progress"], 50.0)

    def test_unknown_status_is_rejected(self):
        response = self.client.post(
            reverse("project-list"),
            {"name": "非法状态", "area_sqm": "10", "status": "whatever"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
