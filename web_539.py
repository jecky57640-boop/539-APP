import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime
import os

# ==========================================
# 1. 設定網頁標題與寬度
# ==========================================
st.set_page_config(page_title="金虎制霸分析系統", layout="wide")
st.title("📱 天天539專用 - 金虎制霸分析系統 (Web版)")
st.write("含：週牌策略(一/四/五) + 跨年修正 + 全維度分析")

# ==========================================
# 2. 側邊欄：輸入區
# ==========================================
st.sidebar.header("1. 上傳資料")
uploaded_file = st.sidebar.file_uploader("請選擇 TXT 或 CSV 檔", type=['txt', 'csv'])

st.sidebar.header("2. 輸入本期號碼")
user_input = st.sidebar.text_input("落球號碼 (5碼，空格隔開)", value="18 25 36 39 17")

btn_run = st.sidebar.button("🚀 開始分析")

# ==========================================
# 3. 核心邏輯 (與原本相同，只是輸出改為 st.write)
# ==========================================
def parse_nums(num_str):
    try:
        clean = num_str.replace(',', ' ').replace('，', ' ')
        return [int(n) for n in clean.split()]
    except:
        return []

def get_weekday_index(issue):
    if issue >= 115000: return (issue - 115001 + 3) % 6
    else: return (issue - 114311 + 3) % 6

if btn_run and uploaded_file is not None:
    # --- A. 解析號碼 ---
    user_nums_drop = parse_nums(user_input)
    if len(user_nums_drop) != 5:
        st.error("❌ 錯誤：請輸入 5 個號碼！")
    else:
        user_nums_size = sorted(user_nums_drop)

        # --- B. 讀取檔案 (Streamlit 特有讀法) ---
        data_records = []
        try:
            # 判斷副檔名
            file_ext = uploaded_file.name.split('.')[-1].lower()
            
            if file_ext == 'txt':
                # 讀取上傳的 bytes 並解碼
                stringio = uploaded_file.getvalue().decode("utf-8", errors='ignore')
                lines = stringio.splitlines()
                
                temp_nums = []
                current_issue = 0
                for line in lines:
                    t = line.strip()
                    if not t: continue
                    parts = t.split()
                    for p in parts:
                        if p.isdigit():
                            val = int(p)
                            if val > 100:
                                if len(temp_nums) == 5: data_records.append((current_issue, temp_nums))
                                temp_nums = []
                                current_issue = val
                            else:
                                temp_nums.append(val)
                if len(temp_nums) == 5: data_records.append((current_issue, temp_nums))

            elif file_ext == 'csv':
                df = pd.read_csv(uploaded_file)
                # 簡單處理 CSV (需依據實際格式調整，這裡做通用處理)
                # 假設最後一欄是號碼，第一欄是期數
                for idx, row in df.iterrows():
                    try:
                        # 這裡簡化處理，嘗試抓最後一個類似號碼的欄位
                        raw = str(row.iloc[-1]).replace('"', '')
                        nums = [int(n) for n in raw.split(',')]
                        if len(nums) == 5:
                            iss = 0
                            try: iss = int(row.iloc[0])
                            except: pass
                            data_records.append((iss, nums))
                    except: pass
                data_records = data_records[::-1]

        except Exception as e:
            st.error(f"讀取失敗：{e}")

        # --- C. 開始分析 ---
        if data_records:
            history_drop = [rec[1] for rec in data_records]
            history_size = [sorted(rec[1]) for rec in data_records]
            
            st.success(f"✅ 成功讀取：{len(history_drop)} 期資料")
            
            # === Tab 分頁顯示 ===
            tab1, tab2, tab3 = st.tabs(["📊 週牌回測報告", "🎯 落球序分析", "📏 大小序分析"])

            # ----------------------------------
            # Tab 1: 週牌策略
            # ----------------------------------
            with tab1:
                st.subheader("🔥 三週牌策略回測 (跨年修正版)")
                
                # 初始化統計
                stats = {
                    "mon": {"weeks":0, "wins":0, "cl":0, "ml":0, "log":[], "pend":None},
                    "thu": {"weeks":0, "wins":0, "cl":0, "ml":0, "log":[], "pend":None},
                    "fri": {"weeks":0, "wins":0, "cl":0, "ml":0, "log":[], "pend":None}
                }
                
                # 回測邏輯 (精簡版)
                for i in range(len(data_records)):
                    curr_iss, curr_nums = data_records[i]
                    if curr_iss == 0: continue
                    w_idx = get_weekday_index(curr_iss)

                    # 週一策略
                    if w_idx == 0:
                        if stats["mon"]["pend"]:
                            p = stats["mon"]["pend"]
                            stats["mon"]["weeks"]+=1
                            if p['hit']: stats["mon"]["wins"]+=1; stats["mon"]["cl"]=0
                            else: stats["mon"]["cl"]+=1; stats["mon"]["ml"]=max(stats["mon"]["ml"], stats["mon"]["cl"])
                        stats["mon"]["pend"] = {'iss':curr_iss, 'tar':[sorted(curr_nums)[0]+12], 'hit':False}
                    else:
                        if stats["mon"]["pend"] and not stats["mon"]["pend"]['hit']:
                            if any(t in curr_nums for t in stats["mon"]["pend"]['tar']): stats["mon"]["pend"]['hit']=True

                    # 週四策略
                    if w_idx == 3:
                        if stats["thu"]["pend"]:
                            p = stats["thu"]["pend"]
                            stats["thu"]["weeks"]+=1
                            if p['hit']: stats["thu"]["wins"]+=1; stats["thu"]["cl"]=0
                            else: stats["thu"]["cl"]+=1; stats["thu"]["ml"]=max(stats["thu"]["ml"], stats["thu"]["cl"])
                        stats["thu"]["pend"] = {'iss':curr_iss, 'tar':[sorted(curr_nums)[0]+12], 'hit':False}
                    else:
                        if stats["thu"]["pend"] and not stats["thu"]["pend"]['hit']:
                            if any(t in curr_nums for t in stats["thu"]["pend"]['tar']): stats["thu"]["pend"]['hit']=True

                    # 週五策略
                    if w_idx == 4:
                        if stats["fri"]["pend"]:
                            p = stats["fri"]["pend"]
                            stats["fri"]["weeks"]+=1
                            if p['hit']: stats["fri"]["wins"]+=1; stats["fri"]["cl"]=0
                            else: stats["fri"]["cl"]+=1; stats["fri"]["ml"]=max(stats["fri"]["ml"], stats["fri"]["cl"])
                        sn = sorted(curr_nums)
                        stats["fri"]["pend"] = {'iss':curr_iss, 'tar':[sn[1]+7, sn[1]+9], 'hit':False}
                    else:
                        if stats["fri"]["pend"] and not stats["fri"]["pend"]['hit']:
                            if any(t in curr_nums for t in stats["fri"]["pend"]['tar']): stats["fri"]["pend"]['hit']=True

                # 顯示函數
                def show_stat(title, s_key):
                    s = stats[s_key]
                    st.markdown(f"#### {title}")
                    col1, col2, col3 = st.columns(3)
                    if s["weeks"] > 0:
                        rate = (s["wins"]/s["weeks"])*100
                        col1.metric("回測次數", f"{s['weeks']}")
                        col2.metric("歷史勝率", f"{rate:.1f}%")
                        col3.metric("最長連倒", f"{s['ml']} 週")
                        
                        if s["pend"]:
                            p = s["pend"]
                            tar_str = ",".join(map(str, p['tar']))
                            status = "⚠️ 已開出 (休息)" if p['hit'] else "🔥 尚未開出 (追!)"
                            st.info(f"📅 最新一期 ({p['iss']}) 目標: **[{tar_str}]** | {status}")
                    else:
                        st.write("無資料")
                    st.divider()

                show_stat("策略 A (週一:最小+12)", "mon")
                show_stat("策略 B (週四:最小+12)", "thu")
                show_stat("策略 C (週五:第二+7,+9)", "fri")

            # ----------------------------------
            # Tab 2: 落球序
            # ----------------------------------
            with tab2:
                st.subheader("🔴 落球序拖牌 (含指定/不分位置)")
                pos_names = ["第一支", "第二支", "第三支", "第四支", "第五支"]
                for i, num in enumerate(user_nums_drop):
                    with st.expander(f"【{pos_names[i]}：{num:02d}】詳細數據", expanded=True):
                        # 這裡為了簡化，只做全期統計示範，完整版可依此類推
                        subset = history_drop
                        pos_pool = []
                        gen_pool = []
                        for k in range(len(subset)-1):
                            if subset[k][i] == num: pos_pool.extend(subset[k+1])
                            if num in subset[k]: gen_pool.extend(subset[k+1])
                        
                        c1, c2 = st.columns(2)
                        if pos_pool:
                            top = Counter(pos_pool).most_common(5)
                            c1.write(f"**🔴 指定位置前五名:**")
                            c1.write(", ".join([f"{n}({c})" for n,c in top]))
                        if gen_pool:
                            top = Counter(gen_pool).most_common(5)
                            c2.write(f"**🔵 不分位置前五名:**")
                            c2.write(", ".join([f"{n}({c})" for n,c in top]))

            # ----------------------------------
            # Tab 3: 大小序
            # ----------------------------------
            with tab3:
                st.subheader("🟢 大小序拖牌")
                pos_names_size = ["最小號", "第二小", "第三小", "第四小", "最大號"]
                for i, num in enumerate(user_nums_size):
                    with st.expander(f"【{pos_names_size[i]}：{num:02d}】詳細數據", expanded=False):
                        subset = history_size
                        pos_pool = []
                        for k in range(len(subset)-1):
                            if subset[k][i] == num: pos_pool.extend(subset[k+1])
                        
                        if pos_pool:
                            top = Counter(pos_pool).most_common(5)
                            st.write(f"**🟢 排序拖牌前五名:**")
                            st.write(", ".join([f"{n}({c})" for n,c in top]))

elif btn_run and not uploaded_file:
    st.warning("請先上傳檔案！")
