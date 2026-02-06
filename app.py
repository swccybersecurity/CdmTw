import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="Taiwan CDM 戰情室 (Demo)", layout="wide")

# --- 核心資料庫：模擬你上傳圖片中的台灣資安廠商清單 (部分範例) ---
# 這是為了讓 Demo 看起來很真實，自動帶出解決方案
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

# --- 初始化 Session State (讓資料在網頁重整時不會消失) ---
if 'assets' not in st.session_state:
    st.session_state.assets = pd.DataFrame(columns=["資產名稱", "類別", "皇冠寶石(關鍵資產)"])
if 'defenses' not in st.session_state:
    st.session_state.defenses = {} # 格式: (Asset, Function): {Tier, Coverage, ToolName}

# --- 側邊欄：導航 ---
st.sidebar.title("🛡️ 台灣資安防禦矩陣 (CDM)")
page = st.sidebar.radio("導航", ["1. 資產盤點 (Inventory)", "2. 防禦診斷 (Analysis)", "3. 戰情室與處方 (Action)"])

# --- 頁面 1: 資產盤點 ---
if page == "1. 資產盤點 (Inventory)":
    st.header("📍 步驟一：建立戰場地圖 (資產盤點)")
    
    with st.expander("➕ 新增資產", expanded=True):
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            asset_name = st.text_input("資產名稱 (例如: 核心資料庫, 員工筆電)")
        with col2:
            asset_type = st.selectbox("CDM 類別", ["裝置", "應用程式", "網路", "資料", "使用者"])
        with col3:
            is_crown_jewel = st.checkbox("👑 這是皇冠寶石 (關鍵資產)?")
        
        if st.button("加入盤點清單"):
            if asset_name:
                new_row = {"資產名稱": asset_name, "類別": asset_type, "皇冠寶石(關鍵資產)": is_crown_jewel}
                st.session_state.assets = pd.concat([st.session_state.assets, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"已新增: {asset_name}")
            else:
                st.error("請輸入資產名稱")

    st.subheader("📋 目前資產總表")
    if not st.session_state.assets.empty:
        # 特別標示皇冠寶石
        def highlight_crown(val):
            return 'background-color: #ffd700; color: black' if val else ''
        
        st.dataframe(st.session_state.assets.style.applymap(highlight_crown, subset=['皇冠寶石(關鍵資產)']), use_container_width=True)
        
        # 統計圖表
        st.caption("資產分佈統計：")
        st.bar_chart(st.session_state.assets['類別'].value_counts())
    else:
        st.info("目前尚無資產，請由上方新增。")

# --- 頁面 2: 防禦診斷 ---
elif page == "2. 防禦診斷 (Analysis)":
    st.header("🩺 步驟二：診斷防禦體質")
    
    col_main, col_info = st.columns([2, 1])
    
    with col_main:
        st.subheader("填報現有防禦工具")
        c1, c2 = st.columns(2)
        with c1:
            target_asset = st.selectbox("針對哪個資產維度?", ["裝置", "應用程式", "網路", "資料", "使用者"])
        with c2:
            target_func = st.selectbox("針對哪個功能維度?", ["識別", "保護", "偵測", "應變", "復原"])
            
        tool_name = st.text_input("工具/產品名稱 (例如: TrendMicro Apex One, Splunk)")
        
        # NIST CSF Tiers 邏輯
        tier = st.select_slider(
            "成熟度評估 (NIST CSF Tiers)",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Tier 1: 被動反應 (紅燈 - 覆蓋率 < 25%)",
                2: "Tier 2: 風險感知 (黃燈 - 覆蓋率 ~ 50%)",
                3: "Tier 3: 制度化 (綠燈 - 全公司適用)",
                4: "Tier 4: 自適應 (金燈 - AI/自動化)"
            }[x]
        )
        
        if st.button("更新防禦矩陣狀態"):
            key = (target_asset, target_func)
            st.session_state.defenses[key] = {
                "tool": tool_name,
                "tier": tier
            }
            st.success(f"已更新 [{target_asset}-{target_func}] 的狀態！")

    with col_info:
        st.info("""
        **評分標準參考：**
        * 🔴 **Tier 1**: 沒有 SOP，想到才做。
        * 🟡 **Tier 2**: 有買工具，但沒裝滿。
        * 🟢 **Tier 3**: 標準化，全員部署。
        * 🟡 **Tier 4**: AI 自動防禦 (理想目標)。
        """)

# --- 頁面 3: 戰情室 ---
elif page == "3. 戰情室與處方 (Action)":
    st.header("📊 步驟三：CDM 熱區圖與解決方案")
    
    # 定義 CDM 結構
    assets = ["裝置", "應用程式", "網路", "資料", "使用者"]
    functions = ["識別", "保護", "偵測", "應變", "復原"]
    
    # 準備繪製 HTML 表格
    html = """<style>
        table {width: 100%; border-collapse: collapse; text-align: center; font-family: sans-serif;}
        th {background-color: #333; color: white; padding: 10px;}
        td {border: 1px solid #ddd; padding: 15px; height: 100px; vertical-align: top; width: 18%;}
        .tier-1 {background-color: #ffcccc; border: 2px solid red;} /* 紅 */
        .tier-2 {background-color: #fff4cc; border: 2px solid orange;} /* 黃 */
        .tier-3 {background-color: #ccffcc; border: 2px solid green;} /* 綠 */
        .tier-4 {background-color: #fffae6; border: 2px solid gold; box-shadow: 0 0 10px gold;} /* 金 */
        .empty {background-color: #f9f9f9; color: #aaa;}
        .cell-title {font-weight: bold; display: block; margin-bottom: 5px; font-size: 0.9em;}
        .tool-name {font-size: 0.8em; color: #333;}
    </style><table><tr><th>資產 \\ 功能</th>"""
    
    for f in functions:
        html += f"<th>{f}</th>"
    html += "</tr>"

    recommendations = []

    for a in assets:
        html += f"<tr><td style='background-color: #eee; font-weight:bold;'>{a}</td>"
        for f in functions:
            key = (a, f)
            data = st.session_state.defenses.get(key)
            
            # 判斷顏色與內容
            if data:
                tier_class = f"tier-{data['tier']}"
                content = f"<span class='tool-name'>{data['tool']}</span>"
                
                # 如果是紅燈或黃燈，加入推薦清單
                if data['tier'] <= 2:
                    recommendations.append((a, f, data['tier']))
            else:
                tier_class = "empty"
                content = "<span style='font-size:0.8em'>未填報<br>(視為缺口)</span>"
                # 空白視為最嚴重缺口
                recommendations.append((a, f, 0))
            
            html += f"<td class='{tier_class}'><span class='cell-title'></span>{content}</td>"
        html += "</tr>"
    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- 自動處方籤區域 ---
    st.subheader("💊 智慧處方籤 (AI 推薦解決方案)")
    
    if recommendations:
        st.write("根據您的熱區圖，系統偵測到以下紅區/黃區，並依據「台灣資安防護矩陣地圖」推薦廠商：")
        
        for asset, func, tier in recommendations:
            # 只顯示前 5 個缺口以免版面太長
            solutions = solutions_db.get((asset, func), ["暫無特定廠商資料，請查詢 SecPaaS"])
            sol_str = "、".join(solutions[:5]) # 顯示前5家
            
            if tier == 0:
                status = "🔴 嚴重缺口 (未部署)"
                st.error(f"**[{asset} - {func}]**：{status}\n\n👉 **推薦解決方案：** {sol_str} 等...")
            elif tier == 1:
                status = "🔴 Tier 1 (被動/不足)"
                st.error(f"**[{asset} - {func}]**：{status}\n\n👉 **建議升級或替換方案：** {sol_str} 等...")
            elif tier == 2:
                status = "🟡 Tier 2 (覆蓋率不足)"
                st.warning(f"**[{asset} - {func}]**：{status}\n\n👉 **建議擴大採購：** {sol_str} 等...")
    else:
        st.success("🎉 恭喜！您的防禦矩陣目前非常健康 (全綠/金)！")

