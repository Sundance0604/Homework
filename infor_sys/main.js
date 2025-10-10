// ========== 配置 ==========
const API_BASE = "http://localhost:8000"; // 后端地址（FastAPI/Flask）
const demoData = {
  users: {
    columns: ["id", "name", "age", "city"],
    rows: [
      [1, "Alice", 23, "Shanghai"],
      [2, "Bob", 27, "Beijing"],
      [3, "Carol", 23, "Shenzhen"],
      [4, "Dave", 31, "Shanghai"],
      [5, "Eve", 27, "Guangzhou"],
    ],
  },
  orders: {
    columns: ["order_id", "user_id", "amount", "date"],
    rows: [
      [101, 1, 199.0, "2025-09-01"],
      [102, 2, 49.9, "2025-09-02"],
      [103, 1, 299.0, "2025-09-02"],
      [104, 3, 19.9, "2025-09-03"],
      [105, 5, 129.0, "2025-09-03"],
    ],
  },
};

// ========== 状态 ==========
let selectedTable = "";
let limit = 100;
let currentColumns = [];
let currentRows = [];

// ========== DOM ==========
const demoModeCb = document.getElementById("demoMode");
const tablesDiv = document.getElementById("tables");
const dataDiv = document.getElementById("dataContainer");
const analysisResult = document.getElementById("analysisResult");

// ========== 工具 ==========
async function fetchJSON(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}
function escapeHTML(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

// ========== 表列表渲染 ==========
function renderTablesList(tables) {
  tablesDiv.innerHTML = "";
  tables.forEach((t) => {
    const btn = document.createElement("button");
    btn.textContent = t;
    btn.className = t === selectedTable ? "active" : "";
    btn.onclick = async () => {
      selectedTable = t;
      renderTablesList(tables);
      await loadRows();
    };
    tablesDiv.appendChild(btn);
  });

  if (!selectedTable && tables.length) {
    selectedTable = tables[0];
    renderTablesList(tables);
  }
}

// ========== 表格渲染 ==========
function renderTableData() {
  if (!currentColumns.length) {
    dataDiv.innerHTML = "（无数据）";
    return;
  }
  let html = "<table><thead><tr>";
  currentColumns.forEach((c) => (html += `<th>${escapeHTML(c)}</th>`));
  html += "</tr></thead><tbody>";

  currentRows.slice(0, limit).forEach((r) => {
    html +=
      "<tr>" +
      r.map((v) => `<td>${escapeHTML(v == null ? "" : v)}</td>`).join("") +
      "</tr>";
  });
  html += "</tbody></table>";
  dataDiv.innerHTML = html;
}

// ========== 加载：演示模式 ==========
async function loadTablesDemo() {
  const names = Object.keys(demoData);
  renderTablesList(names);
  await loadRowsDemo();
}
async function loadRowsDemo() {
  if (!selectedTable) return;
  const t = demoData[selectedTable];
  currentColumns = t.columns;
  currentRows = t.rows;
  renderTableData();
}

// ========== 加载：后端模式 ==========
async function loadTablesAPI() {
  try {
    tablesDiv.innerHTML = "加载表中...";
    const tables = await fetchJSON(`${API_BASE}/tables`);
    if (!tables?.length) {
      tablesDiv.innerHTML = "没有找到用户表";
      dataDiv.innerHTML = "";
      return;
    }
    renderTablesList(tables);
    await loadRowsAPI();
  } catch (e) {
    tablesDiv.innerHTML = `<span style="color:#b91c1c">加载表失败：${escapeHTML(e.message)}</span>`;
  }
}
async function loadRowsAPI() {
  if (!selectedTable) return;
  try {
    dataDiv.innerHTML = "加载数据中...";
    const data = await fetchJSON(
      `${API_BASE}/rows?table=${encodeURIComponent(selectedTable)}&limit=${limit}`
    );
    currentColumns = data?.columns || [];
    currentRows = data?.rows || [];
    renderTableData();
  } catch (e) {
    dataDiv.innerHTML = `<span style="color:#b91c1c">加载数据失败：${escapeHTML(e.message)}</span>`;
  }
}

// ========== 对外统一加载函数 ==========
async function loadTables() {
  selectedTable = "";
  currentColumns = [];
  currentRows = [];
  dataDiv.innerHTML = "";
  if (demoModeCb.checked) {
    await loadTablesDemo();
  } else {
    await loadTablesAPI();
  }
}
async function loadRows() {
  if (demoModeCb.checked) {
    await loadRowsDemo();
  } else {
    await loadRowsAPI();
  }
}

// ========== 事件 ==========
document.getElementById("reloadBtn").onclick = () => loadTables();
document.getElementById("limit").onchange = async (e) => {
  limit = Number(e.target.value) || 100;
  await loadRows();
};
demoModeCb.onchange = () => loadTables();

document.getElementById("exportBtn").onclick = () => {
  if (!currentColumns.length) return;
  const lines = [currentColumns.join(",")];
  currentRows.forEach((r) =>
    lines.push(
      r
        .map((v) => {
          if (v == null) return "";
          const s = String(v).replaceAll('"', '""');
          return s.includes(",") || s.includes("\n") ? `"${s}"` : s;
        })
        .join(",")
    )
  );
  const blob = new Blob(["\ufeff" + lines.join("\n")], {
    type: "text/csv;charset=utf-8;",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = (selectedTable || "data") + ".csv";
  a.click();
  URL.revokeObjectURL(url);
};

document.getElementById("analyzeBtn").onclick = async () => {
  const prompt = document.getElementById("prompt").value || "";
  if (!currentRows.length) {
    analysisResult.textContent = "没有数据可供分析";
    return;
  }

  if (demoModeCb.checked) {
    const preview = currentRows.slice(0, 3);
    const text =
      `【演示模式】表 "${selectedTable}" 共 ${currentRows.length} 行\n` +
      `示例(前3行)：\n` +
      JSON.stringify({ columns: currentColumns, rows: preview }, null, 2) +
      `\n—— 分析要点：\n1) 分布与集中度\n2) 分组统计\n3) 异常与极值\n4) 清洗建议\n\n提示词：\n${prompt}`;
    analysisResult.textContent = text;
  } else {
    analysisResult.textContent = "分析中…";
    try {
      const res = await fetchJSON(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          columns: currentColumns,
          rows: currentRows.slice(0, limit),
          prompt,
        }),
      });
      analysisResult.textContent = res?.analysis || "(无返回内容)";
    } catch (e) {
      analysisResult.textContent = `分析失败：${e.message}`;
    }
  }
};

// ========== 初始化 ==========
window.onload = () => {
  loadTables(); // 根据勾选状态加载演示或后端
};
