from rest_framework import serializers

from .models import Contractor, Expense, Material, Project, Room, Task


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id", "name", "address", "property_type", "area_sqm", "budget",
            "style", "status", "start_date", "expected_end_date", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Room
        fields = [
            "id", "project", "project_name", "name", "room_type", "area_sqm", "notes",
        ]
        read_only_fields = ["id"]


class ContractorSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Contractor
        fields = [
            "id", "project", "project_name", "name", "phone", "role", "company", "notes",
        ]
        read_only_fields = ["id"]


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True, default=None)
    assignee_name = serializers.CharField(source="assignee.name", read_only=True, default=None)

    class Meta:
        model = Task
        fields = [
            "id", "project", "project_name", "room", "room_name",
            "assignee", "assignee_name", "title", "phase", "status",
            "planned_start", "planned_end", "actual_start", "actual_end",
            "notes", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MaterialSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True, default=None)
    total_price = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Material
        fields = [
            "id", "project", "project_name", "room", "room_name",
            "name", "brand", "model", "category", "quantity", "unit",
            "unit_price", "total_price", "supplier", "status", "notes",
        ]
        read_only_fields = ["id"]


class ExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "project", "project_name", "title", "category",
            "amount", "paid_at", "note", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
