from decimal import Decimal

from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Contractor, Expense, Material, Project, Room, Task
from .serializers import (
    ContractorSerializer,
    ExpenseSerializer,
    MaterialSerializer,
    ProjectSerializer,
    RoomSerializer,
    TaskSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD for renovation projects, plus an aggregated budget summary."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        project = self.get_object()
        material_cost = sum(
            (material.total_price for material in project.materials.all()),
            Decimal("0"),
        )
        expense_total = project.expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        task_total = project.tasks.count()
        task_done = project.tasks.filter(status=Task.Status.DONE).count()
        return Response(
            {
                "project_id": project.id,
                "project_name": project.name,
                "budget": project.budget,
                "material_cost": material_cost,
                "expense_total": expense_total,
                "budget_remaining": project.budget - material_cost - expense_total,
                "room_count": project.rooms.count(),
                "task_total": task_total,
                "task_done": task_done,
                "task_progress": round(task_done / task_total * 100, 1) if task_total else 0.0,
            }
        )


class ProjectScopedViewSet(viewsets.ModelViewSet):
    """Base viewset that filters by the ``?project=<id>`` query parameter."""

    project_lookup = "project"

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(**{f"{self.project_lookup}_id": project_id})
        return queryset


class RoomViewSet(ProjectScopedViewSet):
    queryset = Room.objects.select_related("project").all()
    serializer_class = RoomSerializer


class ContractorViewSet(ProjectScopedViewSet):
    queryset = Contractor.objects.select_related("project").all()
    serializer_class = ContractorSerializer


class TaskViewSet(ProjectScopedViewSet):
    queryset = Task.objects.select_related("project", "room", "assignee").all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in ("status", "phase", "room"):
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset


class MaterialViewSet(ProjectScopedViewSet):
    queryset = Material.objects.select_related("project", "room").all()
    serializer_class = MaterialSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in ("status", "category", "room"):
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset


class ExpenseViewSet(ProjectScopedViewSet):
    queryset = Expense.objects.select_related("project").all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset
