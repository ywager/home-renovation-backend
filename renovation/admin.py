from django.contrib import admin

from .models import Contractor, Expense, Material, Project, Room, Task


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "property_type", "area_sqm", "budget", "status", "start_date"]
    list_filter = ["status", "property_type"]
    search_fields = ["name", "address"]
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "room_type", "area_sqm"]
    list_filter = ["room_type"]
    search_fields = ["name", "project__name"]


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "project", "phone", "company"]
    list_filter = ["role"]
    search_fields = ["name", "phone", "company"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "phase", "status", "assignee", "planned_end"]
    list_filter = ["phase", "status"]
    search_fields = ["title", "project__name"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "category", "quantity", "unit", "unit_price", "status"]
    list_filter = ["category", "status"]
    search_fields = ["name", "brand", "model", "supplier"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "category", "amount", "paid_at"]
    list_filter = ["category"]
    search_fields = ["title", "project__name"]
