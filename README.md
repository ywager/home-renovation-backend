# 装修 App 后端（Django REST API）

一个装修 App 的后端示例，使用 **Django + Django REST Framework** 实现，覆盖装修项目从规划到施工、材料采购和费用记录的核心数据。

> This project is under active development and is being built by the **Devin Bots** team.
> Contributions, issues and feedback are welcome.

## 功能

- **装修项目**：面积、预算、风格、状态、开工/预计完工日期
- **空间管理**：客厅、卧室、厨房、卫生间、阳台等
- **施工人员**：设计师、工长、水电工、木工、油漆工等
- **施工任务**：按阶段（拆改/水电/泥瓦/木工/油漆/安装/验收）跟踪进度
- **材料清单**：主材/辅材/家具/家电，数量 × 单价自动算总价
- **费用记录**：设计费、材料费、人工费、管理费等
- **项目汇总接口**：预算、材料成本、实际支出、剩余预算、任务完成率

## API 一览

所有接口位于 `/api/` 下，使用标准的 RESTful 风格（列表/详情/创建/更新/删除）。

| 资源 | 路径 | 说明 |
|---|---|---|
| 装修项目 | `/api/projects/` | CRUD；支持 `?status=` |
| 项目汇总 | `/api/projects/{id}/summary/` | 预算、花费、任务进度汇总 |
| 空间 | `/api/rooms/` | 支持 `?project=<id>` |
| 施工人员 | `/api/contractors/` | 支持 `?project=<id>` |
| 施工任务 | `/api/tasks/` | 支持 `?project=&status=&phase=&room=` |
| 材料 | `/api/materials/` | 支持 `?project=&status=&category=&room=` |
| 费用 | `/api/expenses/` | 支持 `?project=&category=` |

Django Admin 位于 `/admin/`。

## 数据模型

```
Project (装修项目)
 ├── Room        (空间)
 ├── Contractor  (施工人员)
 ├── Task        (施工任务)  ── room / assignee 可为空
 ├── Material    (材料)      ── room 可为空
 └── Expense     (费用记录)
```

## 快速开始

需要 Python 3.10+。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo        # 可选：创建一条示例数据
python manage.py createsuperuser  # 可选：使用 Admin
python manage.py runserver
```

打开 <http://127.0.0.1:8000/api/projects/> 即可浏览 API（DRF 自带可浏览界面）。

## 示例

创建项目：

```bash
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "阳光花园 3-2-501",
    "address": "阳光花园 3 栋 2 单元 501",
    "area_sqm": "89.50",
    "budget": "200000.00",
    "style": "现代简约",
    "status": "in_progress"
  }'
```

创建材料（总价由 `quantity × unit_price` 自动计算）：

```bash
curl -X POST http://127.0.0.1:8000/api/materials/ \
  -H 'Content-Type: application/json' \
  -d '{
    "project": 1,
    "name": "强化复合地板",
    "brand": "圣象",
    "category": "main",
    "quantity": "30",
    "unit": "㎡",
    "unit_price": "159.00"
  }'
```

项目汇总：

```bash
curl http://127.0.0.1:8000/api/projects/1/summary/
```

```json
{
  "project_id": 1,
  "project_name": "阳光花园 3-2-501",
  "budget": "200000.00",
  "material_cost": "4770.00",
  "expense_total": "11500.00",
  "budget_remaining": "183730.00",
  "room_count": 3,
  "task_total": 3,
  "task_done": 1,
  "task_progress": 33.3
}
```

## 配置

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev 值 | 生产环境必须替换 |
| `DJANGO_DEBUG` | `1` | 生产环境设为 `0` |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | 逗号分隔 |
| `DJANGO_DB_PATH` | `db.sqlite3` | SQLite 路径 |

默认使用 SQLite，零配置即可运行。生产环境建议切换 PostgreSQL，只需修改 `config/settings.py` 中的 `DATABASES`。

## 测试

```bash
python manage.py test
```

覆盖了项目创建、参数校验、按项目过滤、材料总价计算和项目汇总接口。

## 说明

- 这是一个可运行的后端示例，鉴权使用 DRF 默认的 `AllowAny`。实际 App 中建议接入 Token/JWT 或 OAuth2，并按用户隔离数据。
- 材料成本与实际费用可能从不同维度统计，`summary` 中二者分别返回，业务上可按需去重。

## License

MIT
