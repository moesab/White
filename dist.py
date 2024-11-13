import streamlit as st

def distribute_resources(total_resources, a_team_size, b_team_size, a_weight, b_weight):
    total_weight = a_team_size * a_weight + b_team_size * b_weight
    a_team_resources = round(total_resources * (a_team_size * a_weight / total_weight))
    b_team_resources = total_resources - a_team_resources  # 残りを留守番組に

    # 一人当たりの資源数を整数にする
    a_individual_share = a_team_resources // a_team_size
    b_individual_share = b_team_resources // b_team_size

    # 端数が出る場合、移転組に優先的に配分
    a_team_resources = a_individual_share * a_team_size
    b_team_resources = b_individual_share * b_team_size
    remaining_resources = total_resources - (a_team_resources + b_team_resources)

    # 残った資源を移転組に優先的に配分
    if remaining_resources > 0:
        a_team_resources += remaining_resources
        a_individual_share += remaining_resources // a_team_size  # 一人当たりの数も更新

    return a_team_resources, b_team_resources, a_individual_share, b_individual_share

st.title("📊 資源分配ツール")

st.markdown("このツールでは、移転組と留守番組に資源を効率的に分配します。人数やウェイト（重み）を入力して、資源分配を計算できます。")

# Step 1: 資源数の入力
st.header("ステップ 1: 総資源数の入力")
total_resources = st.slider("総資源数を選択してください", min_value=1, max_value=1000, value=100)

# Step 2: チーム設定
st.header("ステップ 2: 留守番組の人数とウェイト設定")
a_team_size = st.number_input("移転組の人数を入力してください", min_value=1, value=5)
b_team_size = st.number_input("留守番組の人数を入力してください", min_value=1, value=3)
a_weight = st.slider("移転組のウェイト（重み）を設定してください", min_value=0.1, max_value=3.0, value=1.2)
b_weight = st.slider("留守番組のウェイト（重み）を設定してください", min_value=0.1, max_value=3.0, value=1.0)

# Step 3: 計算ボタン
if st.button("分配を計算する"):
    a_resources, b_resources, a_individual_share, b_individual_share = distribute_resources(total_resources, a_team_size, b_team_size, a_weight, b_weight)
    st.success("分配結果")
    st.write(f"✨ 移転組に割り当てられる資源: **{a_resources}**（一人当たり割当: {a_individual_share}）")
    st.write(f"✨ 留守番組に割り当てられる資源: **{b_resources}**（一人当たり割当: {b_individual_share}）")
