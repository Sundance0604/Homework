// ========== 配置 ==========
const API_BASE = "http://localhost:8000"; // 后端根地址（FastAPI/Flask）

// ========== 状态 ==========
let selectedTable = "";
let limit = 100;
let currentColumns = [];
let currentRows = [];

// ========== DOM ==========
const tablesDiv = document.getElementById("tables");
const dataDiv = document.getElementById("dataContainer");
const analysisResult = document.getElementById("analysisResult"); // 可能未用到，但保留
const limitInput = document.getElementById("limit");

// ========== 工具函数 ==========
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

// ========== 表列表渲染（事件委托版本）==========
function renderTablesList(tables) {
  if (!Array.isArray(tables) || tables.length === 0) {
    tablesDiv.innerHTML = "没有找到用户表";
    return;
  }

  tablesDiv.innerHTML = tables
    .map(
      (t) =>
        `<button type="button" data-t="${escapeHTML(t)}" class="${
          t === selectedTable ? "active" : ""
        }">${escapeHTML(t)}</button>`
    )
    .join("");

  // 默认选中第一个表并加载
  if (!selectedTable) {
    selectedTable = tables[0];
    // 同步高亮
    const firstBtn = tablesDiv.querySelector('button[data-t]');
    if (firstBtn) firstBtn.classList.add('active');
  }
}

// 仅绑定一次：事件委托处理“切换表”
tablesDiv.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-t]");
  if (!btn) return;
  const t = btn.getAttribute("data-t");
  if (t === selectedTable) return;

  selectedTable = t;
  // 切换高亮
  [...tablesDiv.querySelectorAll("button[data-t]")].forEach((b) =>
    b.classList.toggle("active", b === btn)
  );

  await loadRows(); // 加载新表数据
});

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

// ========== 加载表名（后端）==========
async function loadTablesAPI() {
  try {
    tablesDiv.innerHTML = "加载表中...";
    const tables = await fetchJSON(`${API_BASE}/tables`);
    renderTablesList(tables);
    await loadRowsAPI(); // 默认加载 selectedTable（上面已保证有值）
  } catch (e) {
    tablesDiv.innerHTML = `<span style="color:#b91c1c">加载表失败：${escapeHTML(
      e.message
    )}</span>`;
  }
}

// ========== 加载行数据（后端）==========
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
    dataDiv.innerHTML = `<span style="color:#b91c1c">加载数据失败：${escapeHTML(
      e.message
    )}</span>`;
  }
}

// ========== 统一入口 ==========
async function loadTables() {
  selectedTable = "";
  currentColumns = [];
  currentRows = [];
  dataDiv.innerHTML = "";
  await loadTablesAPI();
}

// 供事件调用（之前缺失）
async function loadRows() {
  await loadRowsAPI();
}

// ========== 事件绑定 ==========
document.getElementById("reloadBtn").onclick = () => loadTables();

// 显示行数：实时 + 失焦，两者都触发（带 200ms 防抖）
let limitTimer = null;
function reloadRowsDebounced() {
  clearTimeout(limitTimer);
  limitTimer = setTimeout(async () => {
    const val = Number(limitInput.value);
    limit = Number.isFinite(val) && val > 0 ? val : 100;
    await loadRows();
  }, 200);
}
limitInput.addEventListener("input", reloadRowsDebounced);
limitInput.addEventListener("change", reloadRowsDebounced);

// 导出 CSV
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

// ========== 调用 LLM 查询 ==========

document.getElementById("analyzeBtn").onclick = async () => {
  const prompt = document.getElementById("prompt").value?.trim() || "";
  if (!prompt) {
    analysisResult.textContent = "请输入自然语言查询需求。";
    return;
  }

  analysisResult.textContent = "正在生成 SQL 并查询…";
  llmResultDiv.innerHTML = ""; // 清空旧结果
  llmSQLDiv.textContent = "";

  try {
    const res = await fetch(`${API_BASE}/nlq_query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, limit }),
    });
    const data = await res.json();

    if (data.error) {
      analysisResult.textContent = `❌ 失败：${data.error}`;
      return;
    }

    analysisResult.textContent = "✅ 查询成功";
    llmSQLDiv.textContent = `生成的 SQL：\n${data.sql}\n\n返回行数：${data.row_count}`;
    renderLLMTable(data.columns, data.rows);
  } catch (e) {
    analysisResult.textContent = `请求失败：${e.message}`;
  }
};

// 新的按钮事件处理
document.getElementById("dataScienceAnalyzeBtn").onclick = async () => {
  const prompt = document.getElementById("dataSciencePrompt").value?.trim() || "";
  if (!prompt) {
    document.getElementById("dataScienceAnalysisResult").textContent = "请输入数据科学分析指令。";
    return;
  }

  document.getElementById("dataScienceAnalysisResult").textContent = "正在生成 SQL 并查询…";

  // 调用 getResult_ForAnalysis 生成 SQL 查询
  let sqlQuery;
  try {
    const response = await fetch(`${API_BASE}/nlq_query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, limit: 100 }),
    });
    const data = await response.json();

    if (data.error) {
      document.getElementById("dataScienceAnalysisResult").textContent = `❌ 失败：${data.error}`;
      return;
    }

    sqlQuery = data.sql;
    document.getElementById("dataScienceAnalysisResult").textContent = "✅ 查询成功";

    // 获取后端返回的数据
    const tableData = await fetch(`${API_BASE}/nlq_query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, limit: 100 }),
    }).then(res => res.json());

    // 调用 getAnalysis 执行数据分析
    const analysisResult = await getAnalysis(prompt, tableData);

    // 输出分析结果
    document.getElementById("dataScienceAnalysisResult").textContent = analysisResult;
  } catch (error) {
    document.getElementById("dataScienceAnalysisResult").textContent = `请求失败：${error.message}`;
  }
};

// 调用 getAnalysis 函数进行数据分析
async function getAnalysis(prompt, data) {
  const response = await fetch(`${API_BASE}/data_science_analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, data }),
  });
  const result = await response.json();
  console.log("Analysis result:", result);  // 查看后端返回的数据
  return result.result || "没有分析结果";
}

// ========== 初始化 ==========
window.onload = () => {
  console.log("main.js loaded");
  loadTables();
};
