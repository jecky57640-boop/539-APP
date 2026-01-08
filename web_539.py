import streamlit as st
import pandas as pd
from collections import Counter
import io

# ==========================================
# 1. 網頁設定 (標題與寬度)
# ==========================================
st.set_page_config(page_title="金虎制霸分析系統", page_icon="🎱", layout="wide")
st.title("📱 天天539專用 - 金虎制霸分析系統 (WEB版)")
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .report-box { border: 1px solid #ddd; padding: 15px; border-radius: 5px; background-color: #f9f9f9; font-family: monospace; white-space: pre-wrap;}
</style>
""", unsafe_allow_html=True)

st.markdown("### 🔥 功能：週一/四/五策略 + 跨年修正 + 三榜終極神號")

# ==========================================
# 2. 側邊欄：輸入區
# ==========================================
with st.sidebar:
    st.header("1. 上傳資料")
    uploaded_file = st.file_uploader("請選擇 TXT 或 CSV 檔", type=['txt', 'csv'])

    st.header("2. 輸入本期號碼")
    default_nums = "18 25 36 39 17"
    user_input = st.text_input("落球號碼 (5碼，空格隔開)", value=default_nums)
    
    st.markdown("---")
    st.info("💡 提示：此版本運算邏輯與電腦版完全一致。")

# ==========================================
# 3. 核心邏輯函數 (移植自電腦版)
# ==========================================
def parse_nums(num_str):
    try:
        clean = num_str.replace(',', ' ').replace('，', ' ')
        return [int(n) for n in clean.split()]
    except:
        return []

def get_weekday_index(issue):
    # 跨年修正引擎
    if issue >= 115000:
        diff = issue - 115001
        return (diff + 3) % 6
    else:
        diff = issue - 114311
        return (diff + 3) % 6

# ==========================================
# 4. 主程式執行
# ==========================================
if uploaded_file is not None:
    # --- A. 解析使用者號碼 ---
    user_nums_drop = parse_nums(user_input)
    if len(user_nums_drop) != 5:
        st.error("❌ 錯誤：請輸入 5 個號碼！")
    else:
        user_nums_size = sorted(user_nums_drop)

        # --- B. 讀取檔案 (適配 Streamlit) ---
        data_records = []
        try:
            file_ext = uploaded_file.name.split('.')[-1].lower()
            
            if file_ext == 'txt':
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
                for idx, row in df.iterrows():
                    try:
                        # 嘗試抓取最後一欄當作號碼，第一欄當作期數 (簡易通用邏輯)
                        raw = str(row.iloc[-1]).replace('"', '').replace("'", "")
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
            
            # 使用 Tabs 分頁讓手機版面更整潔
            tab_strategy, tab_analysis, tab_rank = st.tabs(["🔥 三策略回測", "📊 拖牌分析", "🏆 終極神號"])

            # ==========================================
            # Tab 1: 三週牌策略 (完全移植)
            # ==========================================
            with tab_strategy:
                st.subheader("★ 三週牌策略回測 (跨年度精準版)")
                st.markdown("策略A(一): 最小+12 | 策略B(四): 最小+12 | 策略C(五): 第二位+7,+9")
                
                stats = {
                    "mon": {"weeks":0, "wins":0, "cl":0, "ml":0, "log":[], "pend":None},
                    "thu": {"weeks":0, "wins":0, "cl":0, "ml":0, "log":[], "pend":None},
                    "fri": {"weeks":0, "wins":0, "cl":0, "ml":0, "log":[], "pend":None}
                }
                
                for i in range(len(data_records)):
                    curr_iss, curr_nums = data_records[i]
                    if curr_iss == 0: continue
                    w_idx = get_weekday_index(curr_iss)

                    # 週一
                    if w_idx == 0:
                        if stats["mon"]["pend"]:
                            p = stats["mon"]["pend"]
                            stats["mon"]["weeks"]+=1
                            if p['hit']: stats["mon"]["wins"]+=1; stats["mon"]["cl"]=0; status="✅"
                            else: stats["mon"]["cl"]+=1; stats["mon"]["ml"]=max(stats["mon"]["ml"], stats["mon"]["cl"]); status="❌"
                            stats["mon"]["log"].append(f"週一{p['iss']} | 追 {p['tar'][0]:02d} | {status}")
                        stats["mon"]["pend"] = {'iss':curr_iss, 'tar':[sorted(curr_nums)[0]+12], 'hit':False}
                    else:
                        if stats["mon"]["pend"] and not stats["mon"]["pend"]['hit']:
                            if any(t in curr_nums for t in stats["mon"]["pend"]['tar']): stats["mon"]["pend"]['hit']=True

                    # 週四
                    if w_idx == 3:
                        if stats["thu"]["pend"]:
                            p = stats["thu"]["pend"]
                            stats["thu"]["weeks"]+=1
                            if p['hit']: stats["thu"]["wins"]+=1; stats["thu"]["cl"]=0; status="✅"
                            else: stats["thu"]["cl"]+=1; stats["thu"]["ml"]=max(stats["thu"]["ml"], stats["thu"]["cl"]); status="❌"
                            stats["thu"]["log"].append(f"週四{p['iss']} | 追 {p['tar'][0]:02d} | {status}")
                        stats["thu"]["pend"] = {'iss':curr_iss, 'tar':[sorted(curr_nums)[0]+12], 'hit':False}
                    else:
                        if stats["thu"]["pend"] and not stats["thu"]["pend"]['hit']:
                            if any(t in curr_nums for t in stats["thu"]["pend"]['tar']): stats["thu"]["pend"]['hit']=True

                    # 週五
                    if w_idx == 4:
                        if stats["fri"]["pend"]:
                            p = stats["fri"]["pend"]
                            stats["fri"]["weeks"]+=1
                            if p['hit']: stats["fri"]["wins"]+=1; stats["fri"]["cl"]=0; status="✅"
                            else: stats["fri"]["cl"]+=1; stats["fri"]["ml"]=max(stats["fri"]["ml"], stats["fri"]["cl"]); status="❌"
                            tar_str = ",".join([f"{t:02d}" for t in p['tar']])
                            stats["fri"]["log"].append(f"週五{p['iss']} | 追 {tar_str} | {status}")
                        sn = sorted(curr_nums)
                        stats["fri"]["pend"] = {'iss':curr_iss, 'tar':[sn[1]+7, sn[1]+9], 'hit':False}
                    else:
                        if stats["fri"]["pend"] and not stats["fri"]["pend"]['hit']:
                            if any(t in curr_nums for t in stats["fri"]["pend"]['tar']): stats["fri"]["pend"]['hit']=True

                # 顯示回測結果
                def show_stats_ui(title, s_key, color_bar):
                    s = stats[s_key]
                    with st.container():
                        st.markdown(f"#### {title}")
                        c1, c2, c3 = st.columns(3)
                        if s["weeks"] > 0:
                            rate = (s["wins"]/s["weeks"])*100
                            c1.metric("回測次數", s['weeks'])
                            c2.metric("勝率", f"{rate:.1f}%")
                            c3.metric("最長連倒", s['ml'], delta=f"目前連倒 {s['cl']}", delta_color="inverse")
                            
                            if s["pend"]:
                                p = s["pend"]
                                tar_str = "、".join([f"{t:02d}" for t in p['tar']])
                                if p['hit']:
                                    st.success(f"🎉 基準期 {p['iss']} | 目標 **[{tar_str}]** | 狀態：已開出 (任務達成)")
                                else:
                                    st.error(f"🔥 基準期 {p['iss']} | 目標 **[{tar_str}]** | 狀態：尚未開出 (追!)")
                                
                                with st.expander("查看近期戰績"):
                                    for log in s["log"][-5:]:
                                        st.text(log)
                        else:
                            st.write("資料不足")
                        st.markdown(f"<hr style='border-top: 3px solid {color_bar};'>", unsafe_allow_html=True)

                show_stats_ui("🗓️ 策略 A (週一:最小+12)", "mon", "#4CAF50")
                show_stats_ui("🗓️ 策略 B (週四:最小+12)", "thu", "#2196F3")
                show_stats_ui("🗓️ 策略 C (週五:第二+7,+9)", "fri", "#F44336")

            # ==========================================
            # Tab 2: 拖牌分析 (完整重現 Part1 & Part2)
            # ==========================================
            with tab_analysis:
                windows = [50, 100, 300, 0]
                final_pos_drop = []
                final_pos_size = []
                final_gen_all = []

                # --- PART 1: 落球序 ---
                st.subheader("🔴 PART 1 : 落球序慣性分析")
                pos_names_drop = ["第一支", "第二支", "第三支", "第四支", "第五支"]
                
                for idx, target_num in enumerate(user_nums_drop):
                    with st.expander(f"【{pos_names_drop[idx]}：{target_num:02d}】詳細數據", expanded=False):
                        for win in windows:
                            if win == 0 or win > len(history_drop): subset = history_drop; win_label = "全  期"
                            else: subset = history_drop[-win:]; win_label = f"近{win:3d}期"
                            
                            gen_pool = []; pos_pool = []; pos_tails = []
                            for i in range(len(subset) - 1):
                                this_draw = subset[i]; next_draw = subset[i+1]
                                if target_num in this_draw: gen_pool.extend(next_draw)
                                if this_draw[idx] == target_num: 
                                    pos_pool.extend(next_draw)
                                    pos_tails.extend([n % 10 for n in next_draw])
                            
                            # 收集數據
                            if win == 0: # 只收集全期的數據做排名
                                for n in pos_pool: final_pos_drop.append(n)
                                for n in gen_pool: final_gen_all.append(n)

                            # 格式化顯示
                            pos_str = "無"
                            if pos_pool:
                                top3 = Counter(pos_pool).most_common(3)
                                pos_str = ','.join([f'{n:02d}({c})' for n,c in top3])
                                tails = Counter(pos_tails).most_common(2)
                                tail_str = ','.join([f'{t}尾' for t,c in tails])
                                pos_str += f" [尾:{tail_str}]"
                            
                            gen_str = "無"
                            if gen_pool:
                                top3 = Counter(gen_pool).most_common(3)
                                gen_str = ','.join([f'{n:02d}({c})' for n,c in top3])

                            st.markdown(f"`{win_label}` | 🔴落球: **{pos_str}** | 🔵不分: {gen_str}")

                # --- PART 2: 大小序 ---
                st.markdown("---")
                st.subheader("🟢 PART 2 : 大小序分佈分析")
                pos_names_size = ["最小號", "第二小", "第三小", "第四小", "最大號"]

                for idx, target_num in enumerate(user_nums_size):
                    with st.expander(f"【{pos_names_size[idx]}：{target_num:02d}】詳細數據", expanded=False):
                        for win in windows:
                            if win == 0 or win > len(history_size): subset = history_size; win_label = "全  期"
                            else: subset = history_size[-win:]; win_label = f"近{win:3d}期"
                            
                            pos_pool = []; pos_tails = []
                            for i in range(len(subset) - 1):
                                this_draw = subset[i]; next_draw = subset[i+1]
                                if this_draw[idx] == target_num: 
                                    pos_pool.extend(next_draw)
                                    pos_tails.extend([n % 10 for n in next_draw])
                            
                            if win == 0:
                                for n in pos_pool: final_pos_size.append(n)

                            pos_str = "無"
                            if pos_pool:
                                top3 = Counter(pos_pool).most_common(3)
                                pos_str = ','.join([f'{n:02d}({c})' for n,c in top3])
                                tails = Counter(pos_tails).most_common(2)
                                tail_str = ','.join([f'{t}尾' for t,c in tails])
                                pos_str += f" [尾:{tail_str}]"
                            
                            st.markdown(f"`{win_label}` | 🟢排序: **{pos_str}**")

            # ==========================================
            # Tab 3: 總結算 (三榜 + 終極神號)
            # ==========================================
            with tab_rank:
                st.subheader("🏆🏆🏆 最終三榜總結算 🏆🏆🏆")
                
                c1, c2, c3 = st.columns(3)
                
                def show_rank(col, title, data):
                    col.markdown(f"**{title}**")
                    if data:
                        top5 = Counter(data).most_common(5)
                        for r, (n, c) in enumerate(top5, 1):
                            col.text(f"No.{r} : {n:02d} ({c}次)")
                    else:
                        col.text("無資料")

                show_rank(c1, "🔴 落球序・共振王", final_pos_drop)
                show_rank(c2, "🟢 大小序・共振王", final_pos_size)
                show_rank(c3, "🔵 不分位置・共振王", final_gen_all)
                
                st.markdown("---")
                st.subheader("⭐【終極神號】(三榜交集)")
                
                if final_pos_drop and final_pos_size and final_gen_all:
                    s1 = {n for n,c in Counter(final_pos_drop).most_common(5)}
                    s2 = {n for n,c in Counter(final_pos_size).most_common(5)}
                    s3 = {n for n,c in Counter(final_gen_all).most_common(5)}
                    
                    super_strong = s1 & s2 & s3
                    strong = (s1 & s2) | (s1 & s3) | (s2 & s3)
                    
                    if super_strong:
                        nums_str = '  '.join([f"[{n:02d}]" for n in sorted(list(super_strong))])
                        st.success(f"👑👑👑 完美神號 (三榜皆有)： {nums_str}")
                    else:
                        st.info("本次無「三榜皆有」的完美號碼。")
                        
                    if strong - super_strong:
                        nums_str = '  '.join([f"[{n:02d}]" for n in sorted(list(strong - super_strong))])
                        st.warning(f"🔥🔥 重點關注 (兩榜皆有)： {nums_str}")
                else:
                    st.write("資料不足，無法計算交集。")

else:
    st.info("👋 請從左側上傳 TXT 或 CSV 檔案以開始分析。")
