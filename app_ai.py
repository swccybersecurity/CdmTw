import streamlit as st
import pandas as pd
import time
import random

# --- 設定頁面 (AI 版要有未來感) ---
st.set_page_config(page_title="Taiwan CDM: Future AI Edition", layout="wide", page_icon="🤖")

# --- 核心資料庫：台灣資安廠商清單 ---
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
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. AI 智慧盤點"

# --- 側邊欄導航 ---
st.sidebar.title("🤖 CDM Future AI")
st.sidebar.caption("版本: v4.0-Alpha (AI Engine Enabled)")
pages = ["1. AI 智慧盤點", "2. 防禦診斷", "3. 風險戰情室"]
page_selection = st.sidebar.radio("導航", pages, index=pages.index(st.session_state.current_page))

if page_selection != st.session_state.current_page:
    st.session_state.current_page = page_selection
    st.rerun()

# --- 邏輯函數：計算 CDM 格子狀態 ---
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

# ==========================================
# 頁面 1: AI 智慧盤點 (Inventory)
# ==========================================
if st.session_state.current_page == "1. AI 智慧盤點":
    st.header("📍 步驟一：建立戰場地圖 (AI Assisted)")
    st.caption("支援自然語言處理 (NLP) 與非結構化資料匯入")

    # --- AI 匯入區塊 (The "Flashy" Part) ---
    st.markdown("### 🤖 AI 智慧批次匯入引擎")
    with st.container():
        st.info("💡 提示：您可以直接複製 Excel、Email 或 IT 資產清單的原始文字，AI 將自動完成分類與權重判斷。")
        
        raw_text = st.text_area(
            "請貼上原始資產資料 (支援多行輸入)", 
            height=150,
            value="CrowdStrike Falcon (EDR)\nCisco Catalyst 9200 核心交換器\nHR 員工個資 SQL Database\nSynology NAS 機房備份機\n林總經理的 iPad Pro\nAWS EC2 生產環境主機\n外部廠商 VPN 帳號清單",
            help="此區域模擬串接 LLM API (OpenAI/Gemini/Ollama) 的行為"
        )
        
        col_ai, col_manual = st.columns([1, 3])
        with col_ai:
            run_ai = st.button("🚀 啟動 AI 分析", use_container_width=True, type="primary")
        
        if run_ai:
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            if not lines:
                st.warning("請先輸入資料！")
            else:
                # 模擬 AI 處理進度條
                progress_text = "連線至企業私有 LLM 模型 (Ollama)..."
                my_bar = st.progress(0, text=progress_text)
                
                new_assets = []
                
                # 模擬 AI 逐行分析
                for i, line in enumerate(lines):
                    # 更新進度條視覺效果
                    percent = int(((i + 1) / len(lines)) * 100)
                    my_bar.progress(percent, text=f"AI 正在推理: {line} ...")
                    time.sleep(0.3) # 故意延遲創造 Vibe
                    
                    # --- 模擬 AI 判斷邏輯 (關鍵字規則) ---
                    line_lower = line.lower()
                    category = "裝置" # 預設
                    is_crown = False
                    
                    if any(x in line_lower for x in ['sql', 'db', 'data', '個資', 'database']):
                        category = "資料"
                        is_crown = True # 假設資料庫都很重要
                    elif any(x in line_lower for x in ['ad', 'admin', 'user', '帳號', 'vpn']):
                        category = "使用者"
                    elif any(x in line_lower for x in ['cisco', 'switch', 'wifi', 'router', 'net']):
                        category = "網路"
                        is_crown = True if '核心' in line else False
                    elif any(x in line_lower for x in ['office', 'erp', 'slack', 'app', 'aws']):
                        category = "應用程式"
                        is_crown = True if '生產' in line else False
                    else:
                        category = "裝置"
                        is_crown = True if '總經理' in line or 'nas' in line_lower else False
                    
                    new_assets.append({"資產名稱": line, "類別": category, "皇冠寶石": is_crown})
                
                my_bar.empty()
                st.success(f"🎉 AI 分析完成！成功識別並歸類 {len(new_assets)} 筆資產。")
                
                # 寫入 Session State
                new_df = pd.DataFrame(new_assets)
                st.session_state.assets = pd.concat([st.session_state.assets, new_df], ignore_index=True).drop_duplicates(subset=['資產名稱'])
                st.rerun()

    # --- 傳統手動區塊 (保留給 Hybrid 策略) ---
    with st.expander("🛠️ 手動新增/修正資產 (Human-in-the-loop)", expanded=False):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        with c1: a_name = st.text_input("資產名稱")
        with c2: a_type = st.selectbox("類別", ["裝置", "應用程式", "網路", "資料", "使用者"])
        with c3: a_crown = st.checkbox("👑 皇冠寶石?")
        with c4: 
            st.write("")
            st.write("")
            if st.button("新增"):
                if a_name:
                    new_row = {"資產名稱": a_name, "類別": a_type, "皇冠寶石": a_crown}
                    st.session_state.assets = pd.concat([st.session_state.assets, pd.DataFrame([new_row])], ignore_index=True)
                    st.rerun()

    # --- 顯示清單 ---
    if not st.session_state.assets.empty:
        st.divider()
        st.subheader("📋 資產戰略地圖 (AI Generated)")
        def highlight_crown(val): return 'background-color: #ffd700; color: black' if val else ''
        st.dataframe(
            st.session_state.assets.style.applymap(highlight_crown, subset=['皇冠寶石']), 
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    if st.button("下一步：防禦診斷 👉", use_container_width=True):
        st.session_state.current_page = "2. 防禦診斷"
        st.rerun()

# ==========================================
# 頁面 2: 防禦診斷 (Assessment)
# ==========================================
elif st.session_state.current_page == "2. 防禦診斷":
    st.header("🩺 步驟二：防禦成熟度診斷")
    
    target_category = st.selectbox("請選擇要評估的類別：", ["裝置", "應用程式", "網路", "資料", "使用者"])
    assets_in_cat = st.session_state.assets[st.session_state.assets['類別'] == target_category]
    
    if assets_in_cat.empty:
        st.warning(f"⚠️ 尚未建立「{target_category}」類別的資產，請回上一步使用 AI 匯入。")
    else:
        st.info(f"正在評估 {len(assets_in_cat)} 項資產。")
        tabs = st.tabs(["識別 (ID)", "保護 (PR)", "偵測 (DE)", "應變 (RS)", "復原 (RC)"])
        functions = ["識別", "保護", "偵測", "應變", "復原"]
        
        for i, func in enumerate(functions):
            with tabs[i]:
                for idx, row in assets_in_cat.iterrows():
                    asset = row['資產名稱']
                    is_crown = row['皇冠寶石']
                    crown_label = "👑" if is_crown else ""
                    key = (asset, func)
                    current_val = st.session_state.assessments.get(key, 0)
                    
                    with st.container():
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.markdown(f"#### {asset} {crown_label}")
                            if is_crown: st.caption("⚠️ 關鍵資產")
                        with c2:
                            score = st.radio(
                                f"成熟度 ({asset}-{func})",
                                options=[0, 1, 2, 3, 4],
                                index=current_val,
                                format_func=lambda x: {
                                    0: "⚪ N/A",
                                    1: "🔴 Tier 1 (不足)",
                                    2: "🟡 Tier 2 (部分)",
                                    3: "🟢 Tier 3 (標準)",
                                    4: "🏆 Tier 4 (自動)"
                                }[x],
                                key=f"radio_{asset}_{func}",
                                horizontal=True
                            )
                            st.session_state.assessments[key] = score
                        st.divider()

    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("👈 上一步", use_container_width=True):
            st.session_state.current_page = "1. AI 智慧盤點"
            st.rerun()
    with col_next:
        if st.button("下一步：進入戰情室 👉", use_container_width=True):
            st.session_state.current_page = "3. 風險戰情室"
            st.rerun()

# ==========================================
# 頁面 3: 風險戰情室 (Dashboard)
# ==========================================
elif st.session_state.current_page == "3. 風險戰情室":
    st.header("📊 步驟三：CDM 風險戰情室 (AI-Driven)")
    
    categories = ["裝置", "應用程式", "網路", "資料", "使用者"]
    functions = ["識別", "保護", "偵測", "應變", "復原"]
    recommendation_list = []

    # HTML 樣式 (深色模式優化)
    html_code = """
    <style>
        table {width: 100%; border-collapse: separate; border-spacing: 4px;}
        th {background-color: #2b2d42; color: white; padding: 10px; font-size: 0.9em; text-transform: uppercase;}
        td {
            padding: 8px; height: 80px; text-align: center; 
            border-radius: 8px; font-weight: bold; font-size: 0.95em; color: black;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2); transition: all 0.3s ease;
        }
        td:hover {transform: scale(1.02);}
        .cat-head {background-color: #4a4e69; color: white; width: 15%;}
        
        .s-no-asset {background-color: #edf2f4; color: #8d99ae; border: 1px dashed #8d99ae;}
        .s-pending {background-color: #f8f9fa; color: #6c757d;}
        .s-crown-risk {background-color: #d90429; color: white; border: 3px solid #ffd700; animation: pulse 1.5s infinite;}
        .s-t1 {background-color: #ef233c; color: white;}
        .s-t2 {background-color: #ffb703; color: black;}
        .s-t3 {background-color: #52b788; color: white;}
        .s-t4 {background-color: #7209b7; color: white; border: 2px solid #ffd700;}
        
        @keyframes pulse { 0% {box-shadow: 0 0 0 0 rgba(217, 4, 41, 0.7);} 70% {box-shadow: 0 0 0 10px rgba(217, 4, 41, 0);} 100% {box-shadow: 0 0 0 0 rgba(217, 4, 41, 0);} }
    </style>
    <table>
        <tr><th>CDM</th>
    """
    for f in functions: html_code += f"<th>{f}</th>"
    html_code += "</tr>"

    for cat in categories:
        html_code += f"<tr><td class='cat-head'>{cat}</td>"
        for func in functions:
            status, tier, details = calculate_cell_status(cat, func)
            
            if status in ["crown_risk", "tier-1", "tier-2"]:
                recommendation_list.append((cat, func, status))

            css_class = ""
            display_text = ""
            
            if status == "no_asset":
                css_class = "s-no-asset"
                display_text = "無資產"
            elif status == "not_assessed":
                css_class = "s-pending"
                display_text = "待評估"
            elif status == "crown_risk":
                css_class = "s-crown-risk"
                display_text = "⚠️ 關鍵風險"
            else:
                css_class = f"s-t{tier}"
                display_text = f"Tier {tier}"
            
            html_code += f"<td class='{css_class}'>{display_text}</td>"
        html_code += "</tr>"
    html_code += "</table>"
    
    st.markdown(html_code, unsafe_allow_html=True)

    # --- 智慧處方籤 (整合 SecPaaS) ---
    st.divider()
    st.subheader("💊 智慧處方籤 (AI Recommendation)")
    
    SECPAAS_URL = "https://secpaas.org.tw/W_SecDocProduct"
    
    if recommendation_list:
        st.write(f"AI 引擎偵測到 **{len(recommendation_list)}** 個潛在風險區塊，已為您匹配台灣合格資安廠商：")
        
        for cat, func, status in recommendation_list:
            if status == "crown_risk":
                label = "🚨 皇冠風險 (Critical)"
                desc = "關鍵資產暴露於高風險中，需立即處置！"
            elif status == "tier-1":
                label = "🔴 嚴重缺口 (Tier 1)"
                desc = "基礎防禦能力不足。"
            else:
                label = "🟡 建議強化 (Tier 2)"
                desc = "部分防禦未標準化。"
            
            with st.expander(f"{label}：[{cat} - {func}]", expanded=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    vendors = solutions_db.get((cat, func), [])
                    vendor_txt = "、".join(vendors[:4]) + ("..." if len(vendors)>4 else "") if vendors else "查無特定廠商"
                    st.markdown(f"**診斷：** {desc}")
                    st.markdown(f"👀 **AI 推薦廠商：** {vendor_txt}")
                with c2:
                    st.write("")
                    st.link_button("🔍 SecPaaS 媒合", url=SECPAAS_URL)
    else:
        if st.session_state.assets.empty:
            st.warning("⚠️ 無數據。")
        else:
            st.success("🎉 AI 診斷完畢：您的防禦矩陣處於健康狀態。")
            st.link_button("前往 SecPaaS 資安地圖", SECPAAS_URL)

    st.write("")
    if st.button("🔄 重新啟動分析", use_container_width=True):
        st.session_state.current_page = "1. AI 智慧盤點"
        st.rerun()
