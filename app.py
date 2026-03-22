import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="金饰利润计算", page_icon="💰", layout="centered")

# -----------------------------
# 历史记录文件
# -----------------------------
SUMMARY_HISTORY_FILE = "profit_history.json"
DETAIL_HISTORY_FILE = "profit_detail_history.json"


def load_json_file(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def resequence(records):
    for i, record in enumerate(records, start=1):
        record["序号"] = i
    return records


if "summary_history" not in st.session_state:
    st.session_state.summary_history = load_json_file(SUMMARY_HISTORY_FILE)

if "detail_history" not in st.session_state:
    st.session_state.detail_history = load_json_file(DETAIL_HISTORY_FILE)

# -----------------------------
# 固定参数
# -----------------------------
SALES_SHIPPING = 15
COST_SHIPPING = 13
SALES_CERT_FEE = 5
COST_CERT_FEE = 4
COST_LABOR_PER_G = 20

SILVER_CHAIN_COST = 33
SILVER_CHAIN_SALE = 59

CRAFT_OPTIONS = {
    "珐琅": 108,
    "素金": 98,
    "钻石": 118
}

# -----------------------------
# 页面标题
# -----------------------------
st.markdown("### 金饰利润计算工具")
st.caption("用于金首饰销售报价、利润与利润率核算")

# -----------------------------
# 基础输入
# -----------------------------
st.markdown("#### 基础信息")

col1, col2 = st.columns(2)

with col1:
    category = st.selectbox("品种", ["珐琅", "素金", "钻石"])
    weight = st.number_input("克重（g）", min_value=0.0, value=1.0, step=0.01)
    sale_gold_price_per_g = st.number_input("销售金价 / 克（元）", min_value=0.0, value=800.0, step=1.0)

with col2:
    cost_gold_price_per_g = st.number_input("成本金价 / 克（元）", min_value=0.0, value=700.0, step=1.0)
    tax_rate_percent = st.number_input("税率（输入 5 表示 5%）", min_value=0.0, value=5.0, step=0.1)

sale_labor_per_g = CRAFT_OPTIONS[category]

st.markdown("#### 配件选择")

col3, col4 = st.columns(2)

with col3:
    use_silver_chain = st.checkbox("银链", value=False)

with col4:
    use_braided_rope = st.checkbox("编绳", value=False)

braid_cost = 0
braid_sale = 0
braid_label = "无"

if use_braided_rope:
    braid_option = st.radio(
        "编绳档位",
        ["15/30", "20/40"],
        horizontal=True
    )
    if braid_option == "15/30":
        braid_cost = 15
        braid_sale = 30
        braid_label = "15/30"
    else:
        braid_cost = 20
        braid_sale = 40
        braid_label = "20/40"

silver_chain_cost = SILVER_CHAIN_COST if use_silver_chain else 0
silver_chain_sale = SILVER_CHAIN_SALE if use_silver_chain else 0

# -----------------------------
# 计算逻辑（口径B）
# -----------------------------
tax_rate = tax_rate_percent / 100.0

sale_gold_total = sale_gold_price_per_g * weight
cost_gold_total = cost_gold_price_per_g * weight

sale_labor_total = sale_labor_per_g * weight
cost_labor_total = COST_LABOR_PER_G * weight

# 未税销售合计
untaxed_sale_total = (
    sale_gold_total
    + sale_labor_total
    + SALES_SHIPPING
    + SALES_CERT_FEE
    + silver_chain_sale
    + braid_sale
)

# 税费
tax_fee = untaxed_sale_total * tax_rate

# 总销售价（含税）
customer_total_payment = untaxed_sale_total + tax_fee

# 原始成本（未加税）
base_cost = (
    cost_gold_total
    + cost_labor_total
    + COST_SHIPPING
    + COST_CERT_FEE
    + silver_chain_cost
    + braid_cost
)

# 总成本（口径B：加税）
total_cost = base_cost + tax_fee

# 利润与利润率（口径B）
profit = customer_total_payment - total_cost
profit_rate = 0 if total_cost == 0 else profit / total_cost

# 当前记录数据
current_summary_record = {
    "总成本": round(total_cost, 2),
    "总销售价": round(customer_total_payment, 2),
    "利润": round(profit, 2),
    "利润率(%)": round(profit_rate * 100, 2)
}

current_detail_record = {
    "品种": category,
    "克重": round(weight, 2),
    "销售金价/克": round(sale_gold_price_per_g, 2),
    "成本金价/克": round(cost_gold_price_per_g, 2),
    "税率(%)": round(tax_rate_percent, 2),
    "银链": "是" if use_silver_chain else "否",
    "编绳": braid_label,
    "销售手工费/克": round(sale_labor_per_g, 2),
    "成本手工费/克": round(COST_LABOR_PER_G, 2),
    "销售金价总额": round(sale_gold_total, 2),
    "成本金价总额": round(cost_gold_total, 2),
    "销售手工费总额": round(sale_labor_total, 2),
    "成本手工费总额": round(cost_labor_total, 2),
    "销售运费": round(SALES_SHIPPING, 2),
    "运费成本": round(COST_SHIPPING, 2),
    "证书销售费": round(SALES_CERT_FEE, 2),
    "证书成本": round(COST_CERT_FEE, 2),
    "银链售价": round(silver_chain_sale, 2),
    "银链成本": round(silver_chain_cost, 2),
    "编绳售价": round(braid_sale, 2),
    "编绳成本": round(braid_cost, 2),
    "未税销售合计": round(untaxed_sale_total, 2),
    "税费": round(tax_fee, 2),
    "原始成本": round(base_cost, 2),
    "总成本": round(total_cost, 2),
    "总销售价": round(customer_total_payment, 2),
    "利润": round(profit, 2),
    "利润率(%)": round(profit_rate * 100, 2)
}

# -----------------------------
# 结果展示
# -----------------------------
st.markdown("---")
st.markdown("#### 核算结果")

m1, m2, m3 = st.columns(3)
m1.metric("利润", f"¥ {profit:.2f}")
m2.metric("利润率", f"{profit_rate:.2%}")
m3.metric("总销售价", f"¥ {customer_total_payment:.2f}")

st.markdown("#### 核心明细")

c1, c2 = st.columns(2)

with c1:
    st.write(f"未税销售合计：¥ {untaxed_sale_total:.2f}")
    st.write(f"税费：¥ {tax_fee:.2f}")
    st.write(f"总销售价：¥ {customer_total_payment:.2f}")

with c2:
    st.write(f"原始成本：¥ {base_cost:.2f}")
    st.write(f"总成本：¥ {total_cost:.2f}")
    st.write(f"销售手工费 / 克：¥ {sale_labor_per_g:.2f}")

# -----------------------------
# 保存当前结果
# -----------------------------
btn1, btn2 = st.columns(2)

with btn1:
    if st.button("保存本次结果", use_container_width=True):
        summary_record = {"序号": len(st.session_state.summary_history) + 1, **current_summary_record}
        detail_record = {"序号": len(st.session_state.detail_history) + 1, **current_detail_record}

        st.session_state.summary_history.append(summary_record)
        st.session_state.detail_history.append(detail_record)

        save_json_file(SUMMARY_HISTORY_FILE, st.session_state.summary_history)
        save_json_file(DETAIL_HISTORY_FILE, st.session_state.detail_history)

        st.success("已保存本次结果和详细拆分")

with btn2:
    if st.button("清空全部记录", use_container_width=True):
        st.session_state.summary_history = []
        st.session_state.detail_history = []
        save_json_file(SUMMARY_HISTORY_FILE, st.session_state.summary_history)
        save_json_file(DETAIL_HISTORY_FILE, st.session_state.detail_history)
        st.success("全部记录已清空")

# -----------------------------
# 历史记录（简版）
# -----------------------------
with st.expander("查看历史记录"):
    if st.session_state.summary_history:
        summary_df = pd.DataFrame(st.session_state.summary_history)

        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        csv_summary = summary_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="导出历史记录为 CSV",
            data=csv_summary,
            file_name="profit_history.csv",
            mime="text/csv",
            use_container_width=True
        )

        delete_col1, delete_col2 = st.columns([2, 1])
        with delete_col1:
            delete_summary_id = st.selectbox(
                "选择要删除的历史记录序号",
                options=[row["序号"] for row in st.session_state.summary_history],
                key="delete_summary_id"
            )
        with delete_col2:
            st.write("")
            st.write("")
            if st.button("删除该条历史记录", use_container_width=True):
                st.session_state.summary_history = [
                    row for row in st.session_state.summary_history
                    if row["序号"] != delete_summary_id
                ]
                st.session_state.summary_history = resequence(st.session_state.summary_history)
                save_json_file(SUMMARY_HISTORY_FILE, st.session_state.summary_history)
                st.success(f"已删除历史记录第 {delete_summary_id} 条")
                st.rerun()
    else:
        st.caption("暂无保存记录")

# -----------------------------
# 当前详细拆分（当前结果）
# -----------------------------
with st.expander("查看当前详细拆分"):
    left, right = st.columns(2)

    with left:
        st.markdown("**销售端**")
        st.write(f"销售金价总额：¥ {sale_gold_price_per_g:.2f} × {weight:.2f} = ¥ {sale_gold_total:.2f}")
        st.write(f"销售手工费总额：¥ {sale_labor_per_g:.2f} × {weight:.2f} = ¥ {sale_labor_total:.2f}")
        st.write(f"销售运费：¥ {SALES_SHIPPING:.2f}")
        st.write(f"证书销售费：¥ {SALES_CERT_FEE:.2f}")
        st.write(f"银链售价：¥ {silver_chain_sale:.2f}")
        st.write(f"编绳售价：¥ {braid_sale:.2f}")
        st.write(
            f"未税销售合计：¥ {sale_gold_total:.2f} + ¥ {sale_labor_total:.2f} + "
            f"¥ {SALES_SHIPPING:.2f} + ¥ {SALES_CERT_FEE:.2f} + "
            f"¥ {silver_chain_sale:.2f} + ¥ {braid_sale:.2f} = ¥ {untaxed_sale_total:.2f}"
        )
        st.write(f"税费：¥ {untaxed_sale_total:.2f} × {tax_rate_percent:.2f}% = ¥ {tax_fee:.2f}")
        st.write(f"总销售价：¥ {untaxed_sale_total:.2f} + ¥ {tax_fee:.2f} = ¥ {customer_total_payment:.2f}")

    with right:
        st.markdown("**成本端**")
        st.write(f"成本金价总额：¥ {cost_gold_price_per_g:.2f} × {weight:.2f} = ¥ {cost_gold_total:.2f}")
        st.write(f"成本手工费总额：¥ {COST_LABOR_PER_G:.2f} × {weight:.2f} = ¥ {cost_labor_total:.2f}")
        st.write(f"运费成本：¥ {COST_SHIPPING:.2f}")
        st.write(f"证书成本：¥ {COST_CERT_FEE:.2f}")
        st.write(f"银链成本：¥ {silver_chain_cost:.2f}")
        st.write(f"编绳成本：¥ {braid_cost:.2f}")
        st.write(
            f"原始成本：¥ {cost_gold_total:.2f} + ¥ {cost_labor_total:.2f} + "
            f"¥ {COST_SHIPPING:.2f} + ¥ {COST_CERT_FEE:.2f} + "
            f"¥ {silver_chain_cost:.2f} + ¥ {braid_cost:.2f} = ¥ {base_cost:.2f}"
        )
        st.write(f"税费：¥ {tax_fee:.2f}")
        st.write(f"总成本：¥ {base_cost:.2f} + ¥ {tax_fee:.2f} = ¥ {total_cost:.2f}")

# -----------------------------
# 详细拆分记录（历史）
# -----------------------------
with st.expander("查看详细拆分记录"):
    if st.session_state.detail_history:
        detail_df = pd.DataFrame(st.session_state.detail_history)

        st.dataframe(detail_df, use_container_width=True, hide_index=True)

        csv_detail = detail_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="导出详细拆分记录为 CSV",
            data=csv_detail,
            file_name="profit_detail_history.csv",
            mime="text/csv",
            use_container_width=True
        )

        dcol1, dcol2 = st.columns([2, 1])
        with dcol1:
            delete_detail_id = st.selectbox(
                "选择要删除的详细记录序号",
                options=[row["序号"] for row in st.session_state.detail_history],
                key="delete_detail_id"
            )
        with dcol2:
            st.write("")
            st.write("")
            if st.button("删除该条详细记录", use_container_width=True):
                st.session_state.detail_history = [
                    row for row in st.session_state.detail_history
                    if row["序号"] != delete_detail_id
                ]
                st.session_state.detail_history = resequence(st.session_state.detail_history)
                save_json_file(DETAIL_HISTORY_FILE, st.session_state.detail_history)
                st.success(f"已删除详细记录第 {delete_detail_id} 条")
                st.rerun()
    else:
        st.caption("暂无详细记录")

st.caption(
    "口径B：税费 = 未税销售合计 × 税率；总销售价 = 未税销售合计 + 税费；"
    "总成本 = 原始成本 + 税费；利润 = 总销售价 - 总成本；利润率 = 利润 ÷ 总成本。"
)
