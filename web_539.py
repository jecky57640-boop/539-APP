import streamlit as st
import pandas as pd
from collections import Counter
import io

# ==========================================
# 1. 網頁設定
# ==========================================
st.set_page_config(page_title="金虎制霸全能分析", page_icon="🎱", layout="wide")
st.title("📱 539專用 - 金虎制霸分析系統 (WEB版)")
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .report-box { border: 1px solid #ddd; padding: 15px; border-radius: 5px; background-color: #f9f9f9; font-family: monospace; white-space: pre-wrap;}
</style>
""", unsafe_allow_html=True)
st.markdown("### 🔥 功能：三週牌策略 + 跨年修正 + 三榜共振 (同步單機版邏輯)")

# ==========================================
# 2. 側邊欄與函數
# ==========================================
with st.sidebar:
    st.header("1. 上傳資料")
    uploaded_file = st.file_uploader("請選擇 TXT 或 CSV 檔", type=['txt', 'csv'])
    st.header("2. 輸入本期號碼")
    user_input = st.text_input("落球號碼 (5碼)", value="18 25 36 39 17")
    st.info("💡 此版本已修正為「多週期共振」邏輯，結果將與電腦版一致。")

def parse_nums(num_str):
    try:
        clean = num_str.replace(',', ' ').replace('，', ' ')
        return [int(n) for n in clean.split()]
    except: return []

def get_weekday_index(issue):
    if issue >= 115000: return (issue - 115001 + 3) % 6
    else: return (issue - 114311 + 3) % 6

# ==========================================
# 3. 主程式
# ==========================================
if uploaded_file is not None:
    user_nums_drop = parse_nums(user_input)
    if len(user_nums_drop) != 5: st.error("❌ 錯誤：請輸入 5 個號碼！")
    else:
        user_nums_size = sorted(user_nums_drop)
        data_records = []
        try:
            file_ext = uploaded_file.name.split('.')[-1].lower()
            if file_ext == 'txt':
                stringio = uploaded_file.getvalue().decode("utf-8", errors='ignore')
                lines = stringio.splitlines()
                temp_nums = []; current_issue = 0
                for line in lines:
                    t = line.strip()
                    if not t: continue
                    parts = t.split()
                    for p in parts:
                        if p.isdigit():
                            val = int(p)
                            if val > 100:
                                if len(temp_nums) == 5: data_records.append((current_issue, temp_nums))
                                temp_nums = []; current_issue = val
                            else: temp_nums.append(val)
                if len(temp_nums) == 5: data_records.append((current_issue, temp_nums))
            elif file_ext == 'csv':
                df = pd.read_csv(uploaded_file)
                for idx, row in df.iterrows():
                    try:
                        raw = str(row.iloc[-1]).replace('"', '').replace("'", "")
                        nums = [int(n) for n in raw.split(',')]
                        if len(nums) == 5:
                            iss = 0
                            try: iss = int(row.iloc[0])
                            except: pass
                            data_records.append((iss, nums))
                    except: pass
                data_records = data_records[::-1]
        except Exception as e: st.error(f"讀取失敗：{e}")

        if data_records:
            history_drop = [rec[1] for rec in data_records]
            history_size = [sorted(rec[1]) for rec in data_records]
            st.success(f"✅ 成功讀取：{len(history_drop)} 期資料")
            
            tab_strategy, tab_analysis, tab_rank = st.tabs(["🔥 三策略回測", "📊 拖牌分析", "🏆 終極神號"])

            # --- Tab 1: 策略回測 (維持不變) ---
            with tab_strategy:
                st.subheader("★ 三週牌策略回測")
                stats = {"mon": {"weeks":0,"wins":0,"cl":0,"ml":0,"log":[],"pend":None},
                         "thu": {"weeks":0,"wins":0,"cl":0,"ml":0,"log":[],"pend":None},
                         "fri": {"weeks":0,"wins":0,"cl":0,"ml":0,"log":[],"pend":None}}
                for i in range(len(data_records)):
                    curr_iss, curr_nums = data_records[i]
                    if curr_iss == 0: continue
                    w_idx = get_weekday_index(curr_iss)
                    # Mon
                    if w_idx == 0:
                        if stats["mon"]["pend"]:
                            p = stats["mon"]["pend"]; stats["mon"]["weeks"]+=1
                            if p['hit']: stats["mon"]["wins"]+=1; stats["mon"]["cl"]=0; s="✅"
                            else: stats["mon"]["cl"]+=1; stats["mon"]["ml"]=max(stats["mon"]["ml"], stats["mon"]["cl"]); s="❌"
                            stats["mon"]["log"].append(f"週一{p['iss']}|追{p['tar'][0]:02d}|{s}")
                        stats["mon"]["pend"] = {'iss':curr_iss, 'tar':[sorted(curr_nums)[0]+12], 'hit':False}
                    elif stats["mon"]["pend"] and not stats["mon"]["pend"]['hit']:
                        if any(t in curr_nums for t in stats["mon"]["pend"]['tar']): stats["mon"]["pend"]['hit']=True
                    # Thu
                    if w_idx == 3:
                        if stats["thu"]["pend"]:
                            p = stats["thu"]["pend"]; stats["thu"]["weeks"]+=1
                            if p['hit']: stats["thu"]["wins"]+=1; stats["thu"]["cl"]=0; s="✅"
                            else: stats["thu"]["cl"]+=1; stats["thu"]["ml"]=max(stats["thu"]["ml"], stats["thu"]["cl"]); s="❌"
                            stats["thu"]["log"].append(f"週四{p['iss']}|追{p['tar'][0]:02d}|{s}")
                        stats["thu"]["pend"] = {'iss':curr_iss, 'tar':[sorted(curr_nums)[0]+12], 'hit':False}
                    elif stats["thu"]["pend"] and not stats["thu"]["pend"]['hit']:
                        if any(t in curr_nums for t in stats["thu"]["pend"]['tar']): stats["thu"]["pend"]['hit']=True
                    # Fri
                    if w_idx == 4:
                        if stats["fri"]["pend"]:
                            p = stats["fri"]["pend"]; stats["fri"]["weeks"]+=1
                            if p['hit']: stats["fri"]["wins"]+=1; stats["fri"]["cl"]=0; s="✅"
                            else: stats["fri"]["cl"]+=1; stats["fri"]["ml"]=max(stats["fri"]["ml"], stats["fri"]["cl"]); s="❌"
                            stats["fri"]["log"].append(f"週五{p['iss']}|追{p['tar']}|{s}")
                        sn = sorted(curr_nums)
                        stats["fri"]["pend"] = {'iss':curr_iss, 'tar':[sn[1]+7, sn[1]+9], 'hit':False}
                    elif stats["fri"]["pend"] and not stats["fri"]["pend"]['hit']:
                        if any(t in curr_nums for t in stats["fri"]["pend"]['tar']): stats["fri"]["pend"]['hit']=True

                def show_s(t, k, c):
                    s = stats[k]
                    st.markdown(f"**{t}**")
                    c1,c2,c3 = st.columns(3)
                    if s["weeks"]>0:
                        c1.metric("次數", s['weeks']); c2.metric("勝率", f"{(s['wins']/s['weeks'])*100:.1f}%"); c3.metric("最長連倒", s['ml'], f"目前{s['cl']}", delta_color="inverse")
                        if s["pend"]:
                            p=s["pend"]; ts=",".join(map(str,p['tar']))
                            st.caption(f"最新: {p['iss']}期 追 [{ts}] -> {'✅已開' if p['hit'] else '🔥未開'}")
                    else: st.text("無資料")
                    st.divider()
                show_s("🗓️ 策略A (週一)", "mon", "#4CAF50")
                show_s("🗓️ 策略B (週四)", "thu", "#2196F3")
                show_s("🗓️ 策略C (週五)", "fri", "#F44336")

            # --- Tab 2 & 3: 共振邏輯修正 ---
            final_pos_drop = []
            final_pos_size = []
            final_gen_all = []
            windows = [50, 100, 300, 0]

            with tab_analysis:
                st.subheader("🔴 落球序 & 🟢 大小序")
                
                # 落球序 loop
                for idx, target_num in enumerate(user_nums_drop):
                    with st.expander(f"🔴 第{idx+1}支 [{target_num:02d}] 拖牌", expanded=False):
                        for win in windows:
                            if win==0 or win>len(history_drop): subset=history_drop; wl="全 期"
                            else: subset=history_drop[-win:]; wl=f"近{win}期"
                            
                            gen_pool=[]; pos_pool=[]; pos_tails=[]
                            for i in range(len(subset)-1):
                                if target_num in subset[i]: gen_pool.extend(subset[i+1])
                                if subset[i][idx]==target_num:
                                    pos_pool.extend(subset[i+1])
                                    pos_tails.extend([n%10 for n in subset[i+1]])
                            
                            # === 關鍵修正：共振計分邏輯 ===
                            # 每個週期(win)的前三名，都加入最終榜單計算一次
                            if pos_pool:
                                top3 = Counter(pos_pool).most_common(3)
                                for n, c in top3: final_pos_drop.append(n) # 修正點：每週期Top3都加分
                                
                                # 顯示用字串
                                s_str = ",".join([f"{n:02d}({c})" for n,c in top3])
                                t_str = ",".join([f"{t}尾" for t,c in Counter(pos_tails).most_common(2)])
                                st.markdown(f"`{wl}` 指定: **{s_str}** [尾:{t_str}]")
                            
                            if gen_pool:
                                top3 = Counter(gen_pool).most_common(3)
                                for n, c in top3: final_gen_all.append(n) # 修正點：每週期Top3都加分

                st.markdown("---")
                # 大小序 loop
                for idx, target_num in enumerate(user_nums_size):
                    with st.expander(f"🟢 第{idx+1}小 [{target_num:02d}] 拖牌", expanded=False):
                        for win in windows:
                            if win==0 or win>len(history_size): subset=history_size; wl="全 期"
                            else: subset=history_size[-win:]; wl=f"近{win}期"
                            
                            pos_pool=[]
                            for i in range(len(subset)-1):
                                if subset[i][idx]==target_num: pos_pool.extend(subset[i+1])
                            
                            if pos_pool:
                                top3 = Counter(pos_pool).most_common(3)
                                for n, c in top3: final_pos_size.append(n) # 修正點：每週期Top3都加分
                                s_str = ",".join([f"{n:02d}({c})" for n,c in top3])
                                st.markdown(f"`{wl}` 排序: **{s_str}**")

            with tab_rank:
                st.subheader("🏆 三榜共振總結算 (次數=推薦強度)")
                c1,c2,c3 = st.columns(3)
                
                def show_r(col, t, d):
                    col.markdown(f"**{t}**")
                    if d:
                        for r, (n, c) in enumerate(Counter(d).most_common(5), 1):
                            col.text(f"No.{r} : {n:02d} ({c}次)")
                    else: col.text("無資料")

                show_r(c1, "🔴 落球序", final_pos_drop)
                show_r(c2, "🟢 大小序", final_pos_size)
                show_r(c3, "🔵 不分位置", final_gen_all)

                st.markdown("---")
                if final_pos_drop and final_pos_size and final_gen_all:
                    s1 = {n for n,c in Counter(final_pos_drop).most_common(5)}
                    s2 = {n for n,c in Counter(final_pos_size).most_common(5)}
                    s3 = {n for n,c in Counter(final_gen_all).most_common(5)}
                    super_strong = s1 & s2 & s3
                    strong = (s1 & s2) | (s1 & s3) | (s2 & s3)
                    
                    if super_strong:
                        st.success(f"👑 完美神號： {'  '.join([f'[{n:02d}]' for n in sorted(super_strong)])}")
                    else: st.info("無三榜交集號碼")
                    
                    if strong - super_strong:
                        st.warning(f"🔥 重點關注： {'  '.join([f'[{n:02d}]' for n in sorted(strong - super_strong)])}")
