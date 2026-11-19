from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("projects", views.ProjectViewSet, basename="project")
router.register("rooms", views.RoomViewSet, basename="room")
router.register("contractors", views.ContractorViewSet, basename="contractor")
router.register("tasks", views.TaskViewSet, basename="task")
router.register("materials", views.MaterialViewSet, basename="material")
router.register("expenses", views.ExpenseViewSet, basename="expense")

urlpatterns = router.urls
