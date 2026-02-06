import streamlit as st
import pandas as pd

# --- 設定頁面 (Page Config) ---
st.set_page_config(page_title="Taiwan CDM 戰情室 Pro", layout="wide")

# --- 核心資料庫：台灣資安廠商清單 (作為預覽與 AI 推薦基礎) ---
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
    # Key=(資產名稱, 功能), Value=分數 (0~4)
    st.session_state.assessments = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 資產盤點"

# --- 側邊欄導航 (與 Session State 連動) ---
pages = ["1. 資產盤點", "2. 防禦診斷", "3. 風險戰情室"]
# 使用 radio 的 on_change 或 key 來確保與按鈕同步有點複雜，這裡用簡單的 key 綁定即可
# 我們讓主頁面的按鈕去修改 current_page，radio 只是顯示用，或者如果使用者點 radio 也能跳轉
st.sidebar.title("🛡️ Taiwan CDM Pro")
page_selection = st.sidebar.radio("導航", pages, index=pages.index(st.session_state.current_page))

# 如果使用者直接點擊側邊欄，更新 session state
if page_selection != st.session_state.current_page:
    st.session_state.current_page = page_selection
    st.rerun()

# --- 核心邏輯函數：計算 CDM 格子狀態 ---
def calculate_cell_status(category, function):
    # 1. 找資產
    df = st.session_state.assets
    if df.empty: return "no_asset", 0, []
    
    related_assets = df[df['類別'] == category]
    if related_assets.empty: return "no_asset", 0, []

    scores = []
    has_crown_risk = False
    details = []

    # 2. 算分數
    for index, row in related_assets.iterrows():
        asset_name = row['資產名稱']
        is_crown = row['皇冠寶石']
        key = (asset_name, function)
        
        # 預設 0 (N/A)
        score = st.session_state.assessments.get(key, 0)
        
        if score > 0: # 有評分才算
            scores.append(score)
            details.append(f"{asset_name}: Tier {score}")
            # 皇冠法則：皇冠資產分數 < 3 (Tier 1 or 2) 即為風險
            if is_crown and score < 3:
                has_crown_risk = True
    
    # 3. 判定狀態
    if not scores: return "not_assessed", 0, [] # 有資產但全 N/A 或未評

    if has_crown_risk: return "crown_risk", 1, details
    
    # 平均法則
    avg_score = sum(scores) / len(scores)
    if avg_score < 1.5: return "tier-1", 1, details
    elif avg_score < 2.5: return "tier-2", 2, details
    elif avg_score < 3.5: return "tier-3", 3, details
    else: return "tier-4", 4, details

# ==========================================
# 頁面 1: 資產盤點 (Inventory)
# ==========================================
if st.session_state.current_page == "1. 資產盤點":
    st.header("📍 步驟一：建立戰場地圖 (Inventory)")
    
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1: asset_name = st.text_input("資產名稱", placeholder="例: 核心資料庫")
        with col2: asset_type = st.selectbox("類別", ["裝置", "應用程式", "網路", "資料", "使用者"])
        with col3: is_crown = st.checkbox("👑 皇冠寶石?", help="勾選代表此資產極為重要，任何弱點都將觸發紅燈")
        with col4: 
            st.write("") # Spacer
            st.write("")
            add_btn = st.button("新增", use_container_width=True)
        
        if add_btn:
            if asset_name and asset_name not in st.session_state.assets['資產名稱'].values:
                new_row = {"資產名稱": asset_name, "類別": asset_type, "皇冠寶石": is_crown}
                st.session_state.assets = pd.concat([st.session_state.assets, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"已新增: {asset_name}")
            elif asset_name:
                st.warning("資產名稱重複！")
            else:
                st.error("請輸入名稱")

    if not st.session_state.assets.empty:
        st.subheader("📋 資產清單")
        def highlight_crown(val): return 'background-color: #ffd700; color: black' if val else ''
        st.dataframe(
            st.session_state.assets.style.applymap(highlight_crown, subset=['皇冠寶石']), 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("👈 請先輸入您的關鍵資產")

    st.divider()
    if st.button("下一步：防禦診斷 👉", use_container_width=True):
        st.session_state.current_page = "2. 防禦診斷"
        st.rerun()

# ==========================================
# 頁面 2: 防禦診斷 (Assessment)
# ==========================================
elif st.session_state.current_page == "2. 防禦診斷":
    st.header("🩺 步驟二：防禦成熟度診斷")
    
    # 選擇資產類別
    target_category = st.selectbox("請選擇要評估的類別：", ["裝置", "應用程式", "網路", "資料", "使用者"])
    
    # 篩選該類別資產
    assets_in_cat = st.session_state.assets[st.session_state.assets['類別'] == target_category]
    
    if assets_in_cat.empty:
        st.warning(f"⚠️ 尚未建立「{target_category}」類別的資產，請回上一步新增。")
    else:
        st.info(f"正在評估 {len(assets_in_cat)} 項資產。請依據 NIST CSF 定義給分。")
        
        # 使用 Tabs 分功能評估
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
                                    0: "⚪ N/A (不適用)",
                                    1: "🔴 Tier 1 (被動/不足)",
                                    2: "🟡 Tier 2 (部分覆蓋)",
                                    3: "🟢 Tier 3 (標準化)",
                                    4: "🏆 Tier 4 (自動化)"
                                }[x],
                                key=f"radio_{asset}_{func}",
                                horizontal=True # 電腦版好看，手機版會自動適應
                            )
                            st.session_state.assessments[key] = score
                        st.divider()

    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("👈 上一步", use_container_width=True):
            st.session_state.current_page = "1. 資產盤點"
            st.rerun()
    with col_next:
        if st.button("下一步：進入戰情室 👉", use_container_width=True):
            st.session_state.current_page = "3. 風險戰情室"
            st.rerun()

# ==========================================
# 頁面 3: 風險戰情室 (Dashboard)
# ==========================================
elif st.session_state.current_page == "3. 風險戰情室":
    st.header("📊 步驟三：CDM 風險戰情室")
    
    categories = ["裝置", "應用程式", "網路", "資料", "使用者"]
    functions = ["識別", "保護", "偵測", "應變", "復原"]
    recommendation_list = []

    # --- 繪製 HTML 矩陣 ---
    html_code = """
    <style>
        table {width: 100%; border-collapse: separate; border-spacing: 3px;}
        th {background-color: #333; color: white; padding: 8px; font-size: 0.85em;}
        td {
            padding: 5px; height: 70px; text-align: center; 
            border-radius: 6px; font-weight: bold; font-size: 0.9em; color: black;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
        .cat-head {background-color: #555; color: white; width: 15%;}
        
        .s-no-asset {background-color: #e0e0e0; color: #aaa; border: 1px dashed #ccc;}
        .s-pending {background-color: #f8f9fa; color: #888;}
        .s-crown-risk {background-color: #ff4b4b; color: white; border: 3px solid #ffd700; animation: pulse 2s infinite;}
        .s-t1 {background-color: #ffcccc; border: 1px solid red;}
        .s-t2 {background-color: #fff3cd; border: 1px solid orange;}
        .s-t3 {background-color: #d1e7dd; border: 1px solid green;}
        .s-t4 {background-color: #fff3cd; border: 2px solid gold;}
        
        @keyframes pulse { 0% {box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7);} 70% {box-shadow: 0 0 0 10px rgba(255, 75, 75, 0);} 100% {box-shadow: 0 0 0 0 rgba(255, 75, 75, 0);} }
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
            
            # 收集推薦清單
            if status in ["crown_risk", "tier-1", "tier-2"]:
                recommendation_list.append((cat, func, status))

            # 決定 CSS 樣式與文字
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

    # --- 智慧處方籤 (PMP 連結整合版) ---
    st.divider()
    st.subheader("💊 智慧處方籤 (AI 推薦 x SecPaaS)")
    
    SECPAAS_URL = "https://secpaas.org.tw/W_SecDocProduct"
    
    if recommendation_list:
        st.write(f"共偵測到 **{len(recommendation_list)}** 個需要強化的防禦區塊：")
        
        for cat, func, status in recommendation_list:
            # 定義標籤
            if status == "crown_risk":
                label = "🚨 皇冠風險 (Critical)"
                desc = "關鍵資產防護不足，需立即改善！"
            elif status == "tier-1":
                label = "🔴 嚴重缺口 (Tier 1)"
                desc = "缺乏基礎防禦或流程。"
            else:
                label = "🟡 建議強化 (Tier 2)"
                desc = "覆蓋率或標準化不足。"
            
            with st.expander(f"{label}：[{cat} - {func}]", expanded=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    # 顯示資料庫中的預覽廠商
                    vendors = solutions_db.get((cat, func), [])
                    vendor_txt = "、".join(vendors[:4]) + ("..." if len(vendors)>4 else "") if vendors else "請點擊右側查詢"
                    
                    st.markdown(f"**診斷：** {desc}")
                    st.markdown(f"👀 **參考廠商範例：** {vendor_txt}")
                with c2:
                    st.write("") # Spacer
                    st.link_button(
                        "🔍 找廠商 (SecPaaS)", 
                        url=SECPAAS_URL, 
                        help="前往資安防護矩陣地圖"
                    )
    else:
        if st.session_state.assets.empty:
            st.warning("⚠️ 目前無資產資料，無法進行分析。請回第一步。")
        else:
            st.success("🎉 恭喜！目前防禦矩陣無高風險紅燈。建議定期檢視 SecPaaS 最新方案。")
            st.link_button("前往 SecPaaS 資安地圖", SECPAAS_URL)

    # 返回按鈕
    st.write("")
    if st.button("🔄 重新盤點 (回到首頁)", use_container_width=True):
        st.session_state.current_page = "1. 資產盤點"
        st.rerun()
