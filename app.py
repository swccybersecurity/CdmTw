import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="Taiwan CDM 戰情室 Pro", layout="wide")

# --- 核心資料庫：台灣資安廠商清單 (已補回) ---
solutions_db = {
    ("裝置", "識別"): ["一休資訊", "台達電子", "思邦科技", "瑞恩資訊", "中芯數據", "中華龍網"],
    ("裝置", "保護"): ["三甲科技", "安碁資訊", "勤業眾信", "趨勢科技", "奧義智慧"],
    ("裝置", "偵測"): ["元盾資安", "伊雲谷", "動力安全", "誠雲科技"],
    ("裝置", "應變"): ["中芯數據", "元盾資安", "安碁資訊"],
    ("裝置", "復原"): ["扇原科技", "肇真數位"],
    
    ("應用程式", "識別"): ["又碩電腦", "元盾資安", "系微", "保華資安"],
    ("應用程式", "保護"): ["三甲科技", "台眾電腦", "安侯企管", "瑞恩資訊"],
    ("應用程式", "偵測"): ["安碁資訊", "鼎原科技"],
    ("應用程式", "應變"): ["中芯數據", "宏基資訊", "動力安全"],
    ("應用程式", "復原"): ["安碁資訊"],

    ("網路", "識別"): ["三甲科技", "安碁資訊", "承映資訊"],
    ("網路", "保護"): ["一休資訊", "台眾電腦", "池安量子", "威碩系統"],
    ("網路", "偵測"): ["中飛科技", "思邦科技", "雲智維"],
    ("網路", "應變"): ["三甲科技", "元盾資安", "如梭世代"],
    ("網路", "復原"): ["如梭世代", "動力安全"],

    ("資料", "識別"): ["台眾電腦", "安碁資訊", "中華電信"],
    ("資料", "保護"): ["三甲科技", "台灣信威", "帝璽智慧"],
    ("資料", "偵測"): ["安碁資訊"],
    ("資料", "應變"): ["三甲科技", "元盾資安"],
    ("資料", "復原"): ["三甲科技", "云碩科技", "華碩雲端"],

    ("使用者", "識別"): ["一休資訊", "帝濶智慧", "全球系統"],
    ("使用者", "保護"): ["又碩電腦", "全域科技", "希臘智慧"],
    ("使用者", "偵測"): ["伊雲谷"],
    ("使用者", "應變"): ["三甲科技", "肇真數位"],
    ("使用者", "復原"): ["思邦科技"],
}

# --- 初始化 Session State ---
if 'assets' not in st.session_state:
    st.session_state.assets = pd.DataFrame(columns=["資產名稱", "類別", "皇冠寶石"])
if 'assessments' not in st.session_state:
    st.session_state.assessments = {}

# --- 側邊欄導航 ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 資產盤點"

pages = ["1. 資產盤點", "2. 防禦診斷", "3. 風險戰情室"]
page = st.sidebar.radio("導航", pages, key="current_page_radio")

# --- 邏輯函數 ---
def calculate_cell_status(category, function):
    df = st.session_state.assets
    if df.empty: return "no_asset", 0, []
    
    related_assets = df[df['類別'] == category]
    if related_assets.empty: return "no_asset", 0, []

    scores = []
    has_crown_risk = False
    details = []

    for index, row in related_assets.iterrows():
        asset_name = row['資產名稱']
        is_crown = row['皇冠寶石']
        key = (asset_name, function)
        score = st.session_state.assessments.get(key, 0)
        
        if score > 0:
            scores.append(score)
            details.append(f"{asset_name}: Tier {score}")
            if is_crown and score < 3:
                has_crown_risk = True
    
    if not scores: return "not_assessed", 0, []

    if has_crown_risk: return "crown_risk", 1, details
    
    avg_score = sum(scores) / len(scores)
    if avg_score < 1.5: return "tier-1", 1, details
    elif avg_score < 2.5: return "tier-2", 2, details
    elif avg_score < 3.5: return "tier-3", 3, details
    else: return "tier-4", 4, details

# --- 頁面 1: 資產盤點 ---
if st.session_state.current_page_radio == "1. 資產盤點":
    st.header("📍 步驟一：建立戰場地圖")
    with st.expander("➕ 新增資產", expanded=True):
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1: asset_name = st.text_input("資產名稱")
        with col2: asset_type = st.selectbox("CDM 類別", ["裝置", "應用程式", "網路", "資料", "使用者"])
        with col3: is_crown = st.checkbox("👑 皇冠寶石?")
        
        if st.button("加入清單"):
            if asset_name and asset_name not in st.session_state.assets['資產名稱'].values:
                new_row = {"資產名稱": asset_name, "類別": asset_type, "皇冠寶石": is_crown}
                st.session_state.assets = pd.concat([st.session_state.assets, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"已新增: {asset_name}")
            elif asset_name: st.warning("名稱重複！")
            else: st.error("請輸入名稱")

    if not st.session_state.assets.empty:
        st.subheader("📋 資產總表")
        def highlight_crown(val): return 'background-color: #ffd700; color: black' if val else ''
        st.dataframe(st.session_state.assets.style.applymap(highlight_crown, subset=['皇冠寶石']), use_container_width=True)

    st.divider()
    st.info("下一步：請切換至「2. 防禦診斷」")

# --- 頁面 2: 防禦診斷 ---
elif st.session_state.current_page_radio == "2. 防禦診斷":
    st.header("🩺 步驟二：資產關聯診斷")
    target_category = st.selectbox("選擇資產類別：", ["裝置", "應用程式", "網路", "資料", "使用者"])
    assets_in_cat = st.session_state.assets[st.session_state.assets['類別'] == target_category]
    
    if assets_in_cat.empty:
        st.warning(f"⚠️ 無「{target_category}」資產，請回上一步新增。")
    else:
        tabs = st.tabs(["識別", "保護", "偵測", "應變", "復原"])
        for i, func in enumerate(["識別", "保護", "偵測", "應變", "復原"]):
            with tabs[i]:
                for idx, row in assets_in_cat.iterrows():
                    asset = row['資產名稱']
                    is_crown = row['皇冠寶石']
                    crown_icon = "👑" if is_crown else ""
                    current_score = st.session_state.assessments.get((asset, func), 0)
                    
                    st.markdown(f"**{asset}** {crown_icon}")
                    score = st.radio(f"評分 ({asset})", [0, 1, 2, 3, 4], 
                        format_func=lambda x: {0:"⚪ N/A", 1:"🔴 Tier 1", 2:"🟡 Tier 2", 3:"🟢 Tier 3", 4:"🏆 Tier 4"}[x],
                        index=current_score, key=f"r_{asset}_{func}")
                    st.session_state.assessments[(asset, func)] = score
    st.divider()
    st.info("下一步：請切換至「3. 風險戰情室」")

# --- 頁面 3: 風險戰情室 ---
elif st.session_state.current_page_radio == "3. 風險戰情室":
    st.header("📊 步驟三：CDM 風險矩陣與處方")
    
    # 這裡收集需要推薦的缺口
    recommendation_list = []

    # 繪製矩陣
    categories = ["裝置", "應用程式", "網路", "資料", "使用者"]
    functions = ["識別", "保護", "偵測", "應變", "復原"]
    
    html = """<style>
        table {width: 100%; border-collapse: separate; border-spacing: 2px;}
        th {background-color: #222; color: white; padding: 5px; font-size: 0.8em;}
        td {padding: 5px; height: 60px; text-align: center; border-radius: 4px; font-weight: bold; font-size: 0.8em; color: black;}
        .cat-header {background-color: #444; color: white; width: 15%;}
        .status-no-asset {background-color: #e0e0e0; color: #999; border: 1px dashed #bbb;}
        .status-not-assessed {background-color: #f0f0f0; color: #666;}
        .status-crown-risk {background-color: #ff4b4b; color: white; border: 3px solid #ffd700; box-shadow: 0 0 5px red;}
        .status-tier-1 {background-color: #ffcccc; border: 1px solid red;} 
        .status-tier-2 {background-color: #fff4cc; border: 1px solid orange;}
        .status-tier-3 {background-color: #ccffcc; border: 1px solid green;}
        .status-tier-4 {background-color: #fffae6; border: 2px solid gold;}
    </style><table><tr><th>CDM</th>"""
    
    for f in functions: html += f"<th>{f}</th>"
    html += "</tr>"

    for cat in categories:
        html += f"<tr><td class='cat-header'>{cat}</td>"
        for func in functions:
            status, tier, details = calculate_cell_status(cat, func)
            
            # 收集推薦需求：如果是「皇冠風險」或「Tier 1/2」
            if status == "crown_risk" or status == "tier-1" or status == "tier-2":
                recommendation_list.append((cat, func, status))

            css_class = f"status-{status}".replace("_", "-")
            text = "無資產" if status=="no_asset" else "待評估" if status=="not_assessed" else "⚠️風險" if status=="crown_risk" else f"Tier {tier}"
            html += f"<td class='{css_class}'>{text}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    # --- 智慧處方籤 (已補回) ---
    st.divider()
    st.subheader("💊 智慧處方籤 (AI 推薦解決方案)")
    
    if recommendation_list:
        st.write("系統偵測到以下風險區域，建議參考廠商：")
        for cat, func, status in recommendation_list:
            vendors = solutions_db.get((cat, func), ["請查詢 SecPaaS 型錄"])
            vendor_str = "、".join(vendors[:6]) # 顯示前6家
            
            risk_label = "🚨 皇冠風險" if status == "crown_risk" else "🔴 嚴重缺口" if status == "tier-1" else "🟡 加強部署"
            st.error(f"**[{cat}-{func}] {risk_label}**：\n 👉 建議廠商：{vendor_str}")
    else:
        if st.session_state.assets.empty:
            st.info("請先至步驟一新增資產。")
        else:
            st.success("🎉 太棒了！您的防禦矩陣目前相當健康。")
