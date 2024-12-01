import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
from utils.DB import (
    init_db,
    get_customer,
    add_customer,
    add_service_record,
    get_service_records,
)

# ==================== 檢查登入 =======================
# 檢查登入狀態
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("為確保資訊安全，請先至 login 頁面登入！")

else:
    # 初始化數據庫
    init_db()

    # 初始化 session_state
    if "records" not in st.session_state:
        st.session_state.records = None
    if "customer" not in st.session_state:
        st.session_state.customer = None

    # Streamlit 應用
    st.title("🔍 查詢或新增顧客車輛")

    # 查詢顧客
    license_plate = st.text_input("請輸入車牌號碼")

    if license_plate:
        # 如果 `customer` 不存在，從數據庫查詢
        if (
            st.session_state.customer is None
            or st.session_state.customer[0] != license_plate
        ):
            st.session_state.customer = get_customer(license_plate)
            if st.session_state.customer:
                # 如果找到顧客，更新歷史記錄
                st.session_state.records = get_service_records(license_plate)
            else:
                # 如果沒找到顧客，清空歷史記錄
                st.session_state.records = None

        # 顯示顧客資料
        if st.session_state.customer:
            customer = st.session_state.customer
            st.success(
                f"找到顧客：{customer[3]} 聯絡方式: {customer[4]} 車款: {customer[2]}"
            )

            # 顯示歷史消費記錄
            if (
                st.session_state.records is not None
                and not st.session_state.records.empty
            ):
                st.subheader("歷史消費記錄：")
                records_df = pd.DataFrame(
                    st.session_state.records,
                    columns=[
                        "ID",
                        "車牌號碼",
                        "日期",
                        "消費內容",
                        "本次消費金額",
                        "備註",
                        "機油里程",
                    ],
                )
                st.table(records_df)
            else:
                st.info("尚無消費記錄。")

            # 新增消費紀錄按鈕
            if st.button("新增消費紀錄"):
                st.session_state["show_form"] = True

            # 顯示表單
            if st.session_state.get("show_form"):
                with st.form("add_service_record", clear_on_submit=True):
                    consumption = st.text_area("消費內容")
                    amount = st.number_input("本次消費金額", min_value=0, step=100)
                    notes = st.text_area("備註")
                    oil_mileage = st.number_input("機油里程", min_value=0)
                    submitted = st.form_submit_button("提交")

                    if submitted:
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        add_service_record(
                            license_plate,
                            current_date,
                            consumption,
                            amount,
                            notes,
                            oil_mileage,
                        )
                        st.success("已成功新增消費紀錄！")

                        # 即時更新 session_state.records
                        new_record = pd.DataFrame(
                            {
                                "ID": ["None"],  # 假設 ID 是自動生成的，可以先設為 None
                                "車牌號碼": [license_plate],
                                "日期": [current_date],
                                "消費內容": [consumption],
                                "本次消費金額": [amount],
                                "備註": [notes],
                                "機油里程": [oil_mileage],
                            }
                        )
                        # 將新紀錄添加到最上面
                        st.session_state.records = pd.concat(
                            [new_record, st.session_state.records], ignore_index=True
                        )

                        # 取消顯示表單
                        st.session_state["show_form"] = False

                        # 強制重新載入頁面，顯示更新後的表格
                        st.rerun()

        else:
            # 新增顧客
            st.warning("未找到紀錄，請新增顧客資訊。")
            name = st.text_input("姓名")
            contact = st.text_input("聯絡方式")
            brand = st.selectbox(
                label="廠牌",
                options=[
                    "KYMCO",
                    "SYM",
                    "YAMAHA",
                    "AEONMOTER",
                    "PGO",
                    "SUZUKI",
                    "VESPA",
                    "HARTFORD",
                    "GOGORO",
                ],
            )
            motorcycle_model = st.text_input("車款")
            if st.button("新增顧客"):
                try:
                    add_customer(license_plate, brand, motorcycle_model, name, contact)
                    st.success("已成功新增顧客！ 點擊下方按鍵新增消費紀錄")
                    # 更新 session_state.customer
                    st.session_state.customer = (
                        license_plate,
                        brand,
                        motorcycle_model,
                        name,
                        contact,
                    )
                    st.session_state.records = pd.DataFrame(
                        columns=[
                            "ID",
                            "車牌號碼",
                            "日期",
                            "消費內容",
                            "本次消費金額" "備註",
                            "機油里程",
                        ],
                    )
                except ValueError as e:
                    st.error(str(e))

                # 顯示新增消費紀錄
                if st.button("新增消費紀錄"):
                    st.session_state["show_form"] = True
