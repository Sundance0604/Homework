from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

# 你的 NLQ -> SQL 函数模块
import getResult  # 确保 getResult.py 与本文件同目录，且有 getResult(prompt:str)->str

# 本地 SQLite 文件路径
DB_PATH = "commerce.sqlite"  # 改成你的 SQLite 文件路径

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
class DataScienceRequest(BaseModel):
    prompt: str            # 用户的分析需求
    data: dict             # 后端返回的数据，包含 sql, columns, rows 等

# 获取数据库连接
def get_conn():
    # row_factory 不设置也行；前端目前用的是二维数组
    return sqlite3.connect(DB_PATH)

# 获取所有表名
@app.get("/tables")
def list_tables():
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        return [r[0] for r in cur.fetchall()]

# 获取表的数据
@app.get("/rows")
def get_rows(table: str = Query(...), limit: int = Query(100)):
    safe_table = table.replace("'", "''")  # 简单转义
    with get_conn() as conn:
        # 获取表的列名
        cur = conn.execute(f"PRAGMA table_info('{safe_table}')")
        columns = [r[1] for r in cur.fetchall()]

        # 获取表数据
        cur = conn.execute(f"SELECT * FROM '{safe_table}' LIMIT ?", (limit,))
        rows = cur.fetchall()

    return {"columns": columns, "rows": rows}

# ---------------- 新增：NLQ -> SQL -> 执行 ----------------

class NLQBody(BaseModel):
    prompt: str
    limit: int | None = None  # 可选：让后端对返回结果做裁剪

@app.post("/nlq_query")
def nlq_query(body: NLQBody):
    """
    接收自然语言 prompt，调用 getResult.getResult(prompt) 生成 SQL，
    仅允许 SELECT，执行并返回结果。
    """
    prompt = (body.prompt or "").strip()
    if not prompt:
        return {"error": "prompt is empty"}

    # 1) 调你写好的函数生成 SQL
    try:
        sql = getResult.getResult(prompt)
        if not isinstance(sql, str) or not sql.strip():
            return {"error": "LLM did not return a valid SQL."}
        sql = sql.strip().rstrip(";")
    except Exception as e:
        return {"error": f"getResult error: {e}"}

    # 2) 安全兜底：只允许 SELECT
    if not sql.lower().lstrip().startswith("select"):
        return {"error": f"Only SELECT is allowed. got: {sql}"}

    # 3) 执行 SQL
    try:
        with get_conn() as conn:
            cur = conn.execute(sql)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []

        # 按需截断返回行数
        if body.limit is not None and body.limit > 0:
            rows = rows[: body.limit]

        return {
            "sql": sql,
            "columns": cols,
            "rows": rows,
            "row_count": len(rows),
        }
    except Exception as e:
        return {"error": f"SQL execute error: {e}", "sql": sql}

# ---------------- 仍保留：/analyze（占位） ----------------
@app.post("/analyze")
def analyze(payload: dict):
    cols = payload.get("columns", [])
    rows = payload.get("rows", [])
    prompt = payload.get("prompt", "")
    return {"analysis": f"收到 {len(rows)} 行数据，列 {len(cols)}；分析提示词：{prompt[:60]}..."}



@app.post("/data_science_analysis")
def data_science_analysis(payload: DataScienceRequest):
    prompt = payload.prompt    # 获取用户的分析需求
    data = payload.data        # 获取后端返回的数据（包含 sql, columns, rows）
    task_type = getResult.get_task_type(prompt)
    if task_type == "TEXT":
        return {"result": getResult.getTextAnalysis(prompt, data)}
    else:
        label_dict = getResult.getVariableList(prompt, data)
        if task_type == "ML":
            return {"result": getResult.ml_analysis(label_dict, data)}
        elif task_type == "ECON":
            return {"result": getResult.econ_analysis(label_dict, data)}



app = FastAPI()

# 数据分析请求体
class DataScienceRequest(BaseModel):
    prompt: str  # 用户的分析需求
    data: dict   # 后端返回的数据，包含 sql, columns, rows 等字段

# 用来存储训练的结果
performance_results = {}

# 后台任务：执行机器学习或计量经济学任务
def perform_data_science_analysis(task_id: str, prompt: str, data: dict):
    # 处理分析任务
    task_type = getResult.get_task_type(prompt)  # 获取任务类型
    print(f"Task type: {task_type}")

    # 根据任务类型执行不同的分析
    if task_type == "TEXT":
        result = getResult.getTextAnalysis(prompt, data)
    else:
        label_dict = getResult.getVariableList(prompt, data)
        if task_type == "ML":
            result = getResult.ml_analysis(label_dict, data)
        elif task_type == "ECON":
            result = getResult.econ_analysis(label_dict, data)
        else:
            result = "Unknown task type"

    # 将训练结果存储到 performance_results 字典
    performance_results[task_id] = result
    print(f"Task {task_id} completed with result: {result}")

# 后端接口：开始数据科学分析任务（异步）
@app.post("/data_science_analysis")
async def data_science_analysis(payload: DataScienceRequest, background_tasks: BackgroundTasks):
    prompt = payload.prompt  # 获取用户的分析需求
    data = payload.data      # 获取后端返回的数据

    # 创建任务 ID
    task_id = str(time.time())  # 使用时间戳作为唯一任务 ID

    # 启动后台任务进行数据分析
    background_tasks.add_task(perform_data_science_analysis, task_id, prompt, data)

    # 返回任务开始的消息
    return {"message": "Training started in the background.", "task_id": task_id}

# 后端接口：获取性能结果
@app.get("/get_performance")
async def get_performance(task_id: str):
    # 获取后台训练结果
    result = performance_results.get(task_id)
    if result is None:
        return {"error": "Performance not yet available"}
    return {"result": result}
