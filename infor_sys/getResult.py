import pandas as pd
from openai import OpenAI
import time
import openpyxl  # 用于实时保存

schema = {
    "customers": {
        "id":           {"type": "INTEGER", "primary_key": True,  "notnull": False, "default": None},
        "first_name":   {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "last_name":    {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "email":        {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "phone":        {"type": "TEXT",    "primary_key": False, "notnull": False, "default": None},
        "city":         {"type": "TEXT",    "primary_key": False, "notnull": False, "default": None},
        "country":      {"type": "TEXT",    "primary_key": False, "notnull": False, "default": None},
        "created_at":   {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
    },

    "products": {
        "id":           {"type": "INTEGER", "primary_key": True,  "notnull": False, "default": None},
        "name":         {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "category":     {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "price":        {"type": "REAL",    "primary_key": False, "notnull": True,  "default": None},
        "cost":         {"type": "REAL",    "primary_key": False, "notnull": True,  "default": None},
        "sku":          {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "stock":        {"type": "INTEGER", "primary_key": False, "notnull": True,  "default": None},
        "created_at":   {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
    },

    "orders": {
        "id":              {"type": "INTEGER", "primary_key": True,  "notnull": False, "default": None},
        "customer_id":     {"type": "INTEGER", "primary_key": False, "notnull": True,  "default": None},
        "order_date":      {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "status":          {"type": "TEXT",    "primary_key": False, "notnull": True,  "default": None},
        "total_amount":    {"type": "REAL",    "primary_key": False, "notnull": True,  "default": 0},
        "shipping_address":{"type": "TEXT",    "primary_key": False, "notnull": False, "default": None},
    },

    "order_items": {
        "id":         {"type": "INTEGER", "primary_key": True,  "notnull": False, "default": None},
        "order_id":   {"type": "INTEGER", "primary_key": False, "notnull": True,  "default": None},
        "product_id": {"type": "INTEGER", "primary_key": False, "notnull": True,  "default": None},
        "quantity":   {"type": "INTEGER", "primary_key": False, "notnull": True,  "default": None},
        "unit_price": {"type": "REAL",    "primary_key": False, "notnull": True,  "default": None},
        "line_total": {"type": "REAL",    "primary_key": False, "notnull": True,  "default": None},
    },
}


# 初始化客户端
client = OpenAI(
    api_key="sk-81aac759ff554765aca7290d886c28cd",
    base_url="https://api.deepseek.com"
)
def getResult(text):

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": f"你是一个数据库专家，这是一个数据库的表结构信息{schema}。"
            "根据这些信息，仅仅返回SQL查询语句，不要返回任何多余的信息。"
            "不要添加任何解释、注释、说明或代码块标记,不要输出```sql```或```。"
            },
            {"role": "user", "content": f"'{text}'"}
        ],
        temperature=0.1,
        max_tokens=100
    )
    result = response.choices[0].message.content
    return result

def getResult_ForAnalysis(text):
    # 使用 LLM 生成 SQL 查询（假设你的 LLM 能识别并拆解复杂需求）
    response = client.chat.completions.create(
        model="deepseek-chat",  # 或使用其他合适的模型
        messages=[
            {
                "role": "system", 
                "content": f"""
                    你是一个数据库专家，以下是数据库的表结构信息：{schema}。
                    用户将提供与数据分析相关的需求，请返回相应的 SQL 查询语句。 
                    如果任务无法通过直接 SQL 查询完成，拆解为提取所需数据的 SQL 查询，并明确哪些字段和表格是必需的。
                    不要提供任何解释、注释或额外内容，只需要返回 SQL 查询语句。
                """
            },
            {
                "role": "user", 
                "content": f"用户的分析需求是：{text}。请根据这些需求生成相应的 SQL 查询语句。如果任务复杂，拆解为多个步骤。"
            }
        ],
        temperature=0.1,
        max_tokens=250  # 增加 token 以确保生成足够多的 SQL 查询
    )
    
    result = response.choices[0].message.content.strip()
    return result

def get_task_type(text):
    response = client.chat.completions.create(
        model="deepseek-chat",  # 使用适合的模型
        messages=[
            {
                "role": "system", 
                "content": f"""
                    你是一个数据科学专家，用户将提供与数据分析相关的需求，
                    如果是机器学习任务，返回“ML”;
                    如果是回归分析任务，返回“ECON”;
                    否则返回“TEXT”。
                    Note: 仅返回“ML”（大写字母）、“ECON”（大写字母）或“TEXT”(大写字母)不要添加任何解释或额外内容。只能返回一个关键词
                """
            },
            {
                "role": "user", 
                "content": f"用户的分析需求是：{text}。请根据这些需求判断任务类型。"
            }
        ],
        temperature=0.1,
        max_tokens=50  # 适当减少 token 数量，因为只需要判断
    )

    result = response.choices[0].message.content.strip().lower()

    # 返回布尔值
    return result.upper()  
def getTextAnalysis(text, data):
    
    sql_query = data.get("sql")
    columns = data.get("columns")
    rows = data.get("rows")
    # 纯文字分析任务（描述性分析）
    response = client.chat.completions.create(
        model="deepseek-chat",  # 或使用其他合适的模型
        messages=[
            {
                "role": "system", 
                "content": f"""
                    你是一个数据分析专家，下面是数据的内容，列名为：{columns}，数据行为：{rows}。
                    请根据这些需求进行描述性分析，并提供结果。
                    分析的结果需为文本，不包含任何代码、数学公式，只需要对数据进行简单描述。
                """
            },
            {
                "role": "user", 
                "content": f"用户的分析需求是：{text}。请根据这些需求生成相应的分析结果，2000字以内。"
            }
        ],
        temperature=0.1,
        max_tokens=2500  # 增加 token 以确保生成足够的分析结果
    )
    
    result = response.choices[0].message.content.strip()
    return result
    # 判断任务类型（回归分析或其他）

def getVariableList(text, data):

    sql_query = data.get("sql")
    columns = data.get("columns")
    rows = data.get("rows")
        # 回归分析任务
    response = client.chat.completions.create(
    model="deepseek-chat",  # 或使用其他合适的模型
    messages=[
        {
            "role": "system", 
            "content": f"""
                你是一个数据分析专家，下面是数据的内容，列名为：{columns}，数据行为：{rows}。
                用户将提供与数据分析相关的需求，
                请严格按照以下格式返回一个单行 JSON 字符串，确保没有换行符（\\n）和额外空格： 
                {{"predictor": "因变量", "features": ["自变量1", "自变量2", ...]}}。
                不要在字典内加入任何额外的换行符或空格。
                仅返回字典内容，不需要任何注释、解释或其他多余内容。
            """
        },
        {
            "role": "user", 
            "content": f"用户的分析需求是：{text}。请根据这些需求生成相应的变量字典。如果是回归分析类任务，请也把控制变量的一并输出到字典中，解释变量在前，控制变量在后。"
        }
    ],
    temperature=0.1,
    max_tokens=2500  # 增加 token 以确保生成足够多的 SQL 查询
    )

    result = response.choices[0].message.content.strip()
    return result

   
        
    

def ml_analysis(label_dict: str, data):
    import pandas as pd
    import json
    from autogluon.tabular import TabularPredictor
    from sklearn.model_selection import train_test_split

    # 提取列名和行数据
    columns = data["columns"]
    rows = data["rows"]
    label_dict = json.loads(label_dict)

    # 创建 DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # 提取 'income' 作为标签（target）
    target = label_dict['predictor']  # 目标变量
    split_point = int(len(df) * 0.5)

    # 按顺序切分
    train_data = df.iloc[:split_point]
    test_data = df.iloc[split_point:]

    # 训练模型
    predictor = TabularPredictor(label=target).fit(train_data,verbosity=0)

    # 进行预测
    # predictions = predictor.predict(test_data)
    # 计算模型的性能（如果需要）
    performance = predictor.evaluate(test_data)
    performance_str = "\n".join([f"{key}: {value}" for key, value in performance.items()])
    return performance_str


def econ_analysis(label_dict: str, data):
    import pandas as pd
    import statsmodels.api as sm
    import json

    # 提取列名和行数据
    columns = data["columns"]
    rows = data["rows"]
    label_dict = json.loads(label_dict)

    # 创建 DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # 提取目标变量（predictor）和特征（features）
    target = label_dict['predictor']  # 目标变量
    features = label_dict['features']  # 特征列表

    # 确保特征列表中至少有1个特征
    if len(features) == 0:
        raise ValueError("Feature list is empty, there must be at least one feature.")

    # 定义解释变量（第一个特征）和控制变量（其余特征）
    explanatory_variable = features[0]  # 第一个特征作为解释变量
    control_variables = features[1:]  # 其余特征作为控制变量

    # 自变量包含解释变量和控制变量
    X = df[[explanatory_variable] + control_variables]  # 解释变量和控制变量
    y = df[target]  # 因变量（目标变量）

    # 处理数据，确保没有空值（如果有空值，需填充或去除）
    X = X.fillna(0)  # 填充空值
    y = y.fillna(0)  # 填充空值

    # 加入常数项（截距）到自变量中
    X = sm.add_constant(X)  # 这一步是添加常数项（截距），以便回归分析中包含截距

    # 拟合 OLS 回归模型
    model = sm.OLS(y, X)  # 使用 OLS 模型
    results = model.fit()  # 拟合模型

    # 输出回归结果
    return results.summary()
