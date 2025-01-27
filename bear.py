import streamlit as st
import math

# 初期化：セッション状態を使って残り兵士数、部隊情報、優先順位を保持
if "remaining_shield" not in st.session_state:
    st.session_state.remaining_shield = None
    st.session_state.remaining_spear = None
    st.session_state.remaining_archer = None
    st.session_state.units = []
    st.session_state.priorities = None

# 部隊編成関数
def allocate_one_unit(remaining_shield, remaining_spear, remaining_archer, capacity, ratios, initial_ratios):
    shield_ratio, spear_ratio, archer_ratio = ratios

    # 必要な兵士数を計算
    required_shield = int(capacity * (shield_ratio / 100))
    required_spear = int(capacity * (spear_ratio / 100))
    required_archer = int(capacity * (archer_ratio / 100))

    # 初期割り当て
    assigned_shield = min(remaining_shield, required_shield)
    assigned_spear = min(remaining_spear, required_spear)
    assigned_archer = min(remaining_archer, required_archer)

    # 初期割り当ての合計を計算
    total_assigned = assigned_shield + assigned_spear + assigned_archer

    # 不足分の計算
    deficit = capacity - total_assigned

    # 補完ロジック
    adjustments = {"Shield": 0, "Spear": 0, "Archer": 0}
    if deficit > 0:
        # 優先順位に基づいて補完
        for priority in ["Shield", "Spear", "Archer"]:
            if deficit <= 0:
                break
            if priority == "Shield" and remaining_shield > assigned_shield:
                add_shield = min(deficit, remaining_shield - assigned_shield)
                assigned_shield += add_shield
                adjustments["Shield"] += add_shield
                deficit -= add_shield
            elif priority == "Spear" and remaining_spear > assigned_spear:
                add_spear = min(deficit, remaining_spear - assigned_spear)
                assigned_spear += add_spear
                adjustments["Spear"] += add_spear
                deficit -= add_spear
            elif priority == "Archer" and remaining_archer > assigned_archer:
                add_archer = min(deficit, remaining_archer - assigned_archer)
                assigned_archer += add_archer
                adjustments["Archer"] += add_archer
                deficit -= add_archer

    # 割り当てた兵士数を更新
    unit = {
        "Shield": assigned_shield,
        "Spear": assigned_spear,
        "Archer": assigned_archer,
        "Shield%": round((assigned_shield / capacity) * 100),
        "Spear%": round((assigned_spear / capacity) * 100),
        "Archer%": round((assigned_archer / capacity) * 100),
        "Adjustments": adjustments,
    }
    remaining_shield -= assigned_shield
    remaining_spear -= assigned_spear
    remaining_archer -= assigned_archer

    return unit, remaining_shield, remaining_spear, remaining_archer

# Streamlit UI
st.title("部隊ごとの編成アプリ")

# 優先順位の選択（最初に一度だけ）
if st.session_state.priorities is None:
    with st.form("priority_form"):
        st.write("不足分を補う際の優先順位を設定してください")
        priority_1 = st.selectbox("第1優先兵種", ["Shield", "Spear", "Archer"], index=2)
        priority_2 = st.selectbox("第2優先兵種", ["Shield", "Spear", "Archer"], index=1)
        priority_3 = st.selectbox("第3優先兵種", ["Shield", "Spear", "Archer"], index=0)
        submit_priorities = st.form_submit_button("優先順位を確定")
    if submit_priorities:
        st.session_state.priorities = [priority_1, priority_2, priority_3]

# 初期兵士数の入力
if st.session_state.remaining_shield is None and st.session_state.priorities is not None:
    with st.form("initial_form"):
        st.write("最初の兵士数を入力してください")
        shield = st.number_input("盾兵の数", min_value=0, step=1, value=415630)
        spear = st.number_input("槍兵の数", min_value=0, step=1, value=324233)
        archer = st.number_input("弓兵の数", min_value=0, step=1, value=369777)
        submit_initial = st.form_submit_button("開始")
    if submit_initial:
        st.session_state.remaining_shield = shield
        st.session_state.remaining_spear = spear
        st.session_state.remaining_archer = archer

# 部隊編成の入力
if st.session_state.remaining_shield is not None:
    with st.form("input_form"):
        st.write("現在の部隊を編成する割合を入力してください")
        shield_ratio = st.number_input("盾兵の割合 (%)", min_value=0, max_value=100, step=1, value=10)
        spear_ratio = st.number_input("槍兵の割合 (%)", min_value=0, max_value=100, step=1, value=10)
        archer_ratio = st.number_input("弓兵の割合 (%)", min_value=0, max_value=100, step=1, value=80)
        capacity = st.number_input("出征容量 (1部隊あたりの最大兵士数)", min_value=1, step=1, value=144310)

        submit = st.form_submit_button("部隊を編成")

    if submit:
        # 部隊を編成
        unit, remaining_shield, remaining_spear, remaining_archer = allocate_one_unit(
            st.session_state.remaining_shield,
            st.session_state.remaining_spear,
            st.session_state.remaining_archer,
            capacity,
            (shield_ratio, spear_ratio, archer_ratio),
            {"Shield": shield_ratio, "Spear": spear_ratio, "Archer": archer_ratio},
        )

        st.session_state.units.append(unit)
        st.session_state.remaining_shield = remaining_shield
        st.session_state.remaining_spear = remaining_spear
        st.session_state.remaining_archer = remaining_archer

    # 部隊削除機能
    if st.session_state.units:
        with st.form("delete_form"):
            st.write("削除する部隊番号を入力してください")
            delete_index = st.number_input(
                "削除する部隊番号", min_value=1, max_value=len(st.session_state.units), step=1, value=1
            )
            delete_submit = st.form_submit_button("部隊を削除")
            if delete_submit:
                deleted_unit = st.session_state.units.pop(delete_index - 1)
                st.session_state.remaining_shield += deleted_unit["Shield"]
                st.session_state.remaining_spear += deleted_unit["Spear"]
                st.session_state.remaining_archer += deleted_unit["Archer"]
                st.success(f"部隊 {delete_index} を削除しました。")

    # 結果表示
    st.write(f"現在の総部隊数: {len(st.session_state.units)}")
    for i, unit in enumerate(st.session_state.units, start=1):
        st.write(f"部隊 {i}:")
        st.write(f"  盾兵: {unit['Shield']} ({unit['Shield%']}%)")
        st.write(f"  槍兵: {unit['Spear']} ({unit['Spear%']}%)")
        st.write(f"  弓兵: {unit['Archer']} ({unit['Archer%']}%)")
        st.write(f"  最終補完: 盾兵 {unit['Adjustments']['Shield']}人, 槍兵 {unit['Adjustments']['Spear']}人, 弓兵 {unit['Adjustments']['Archer']}人")

    # 残り兵士数と次回の指定可能な最大割合を表示
    st.write("### 残り兵士数と次回の指定可能な最大割合")
    remaining_capacity_shield = math.ceil((st.session_state.remaining_shield / capacity) * 100)
    remaining_capacity_spear = math.ceil((st.session_state.remaining_spear / capacity) * 100)
    remaining_capacity_archer = math.ceil((st.session_state.remaining_archer / capacity) * 100)

    st.write(f"盾兵: {st.session_state.remaining_shield}（次回最大割合: {remaining_capacity_shield}%）")
    st.write(f"槍兵: {st.session_state.remaining_spear}（次回最大割合: {remaining_capacity_spear}%）")
    st.write(f"弓兵: {st.session_state.remaining_archer}（次回最大割合: {remaining_capacity_archer}%）")
