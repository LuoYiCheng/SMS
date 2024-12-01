import streamlit as st
import pandas as pd
from utils.DB import (
    get_all_customers,
    update_or_add_customer,
    export_service_records,
    get_service_records,
    update_or_add_service_record,
)
from io import BytesIO
import sqlite3

if not st.session_state.logged_in:
    st.warning("為確保資訊安全，請先至 login 頁面登入！")

elif st.session_state.role != "admin":
    st.warning("無管理權限，請先至 login 頁面以管理者帳號登入！")

else:
    st.title("🧑‍💼 顧客管理系統")

    # 初始化 session_state
    if "customer_data" not in st.session_state:
        st.session_state.customer_data = get_all_customers()

    if "service_records" not in st.session_state:
        st.session_state.service_records = pd.DataFrame()

    # 主要功能選擇
    menu = st.radio("選擇操作", ("顧客資料管理", "消費記錄管理"))

    if menu == "顧客資料管理":
        # ================= 顧客資料管理 =================
        st.subheader("顧客與車輛資料管理")

        # 顯示所有顧客資料
        customer_data = st.session_state.customer_data

        # 顧客篩選選項
        license_plate_filter = st.text_input("輸入車牌號碼查詢")
        name_filter = st.text_input("輸入顧客姓名查詢")

        if license_plate_filter:
            customer_data = customer_data[
                customer_data["車牌號碼"].str.contains(license_plate_filter, case=False)
            ]

        if name_filter:
            customer_data = customer_data[
                customer_data["姓名"].str.contains(name_filter, case=False)
            ]

        # 顯示顧客資料
        edited_data = st.data_editor(
            customer_data, num_rows="dynamic", key="customer_editor"
        )

        # 保存修改
        if st.button("保存修改"):
            # 檢查哪些資料被刪除
            deleted_data = customer_data.loc[
                ~customer_data["車牌號碼"].isin(edited_data["車牌號碼"])
            ]
            # 刪除已被移除的顧客資料
            with sqlite3.connect("data/motorcycle_shop.db") as conn:
                cursor = conn.cursor()
                for _, row in deleted_data.iterrows():
                    cursor.execute(
                        "DELETE FROM customers WHERE license_plate = ?",
                        (row["車牌號碼"],),
                    )
                conn.commit()
            # 新增/修改顧客資料
            for index, row in edited_data.iterrows():
                try:
                    update_or_add_customer(
                        license_plate=row["車牌號碼"],
                        brand=row["廠牌"],
                        motorcycle_model=row["車款"],
                        name=row["姓名"],
                        contact=row["聯絡方式"],
                    )
                    fix_error = False
                except:
                    fix_error = True
            if not fix_error:
                st.session_state.customer_data = get_all_customers()
                st.success("已成功修改/新增顧客資料")
            else:
                st.error("保存失敗！請注意是否多新增到一行空白列，")

        # 匯出顧客資料
        customer_buffer = BytesIO()
        st.session_state.customer_data.to_excel(
            customer_buffer, index=False, engine="openpyxl"
        )
        customer_buffer.seek(0)

        st.download_button(
            label="匯出顧客資料為 Excel",
            data=customer_buffer,
            file_name="customers.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    elif menu == "消費記錄管理":
        # ================= 消費記錄管理 =================
        st.subheader("消費記錄管理")

        # 讓管理者選擇顧客
        license_plate = st.selectbox(
            "選擇顧客車牌", get_all_customers()["車牌號碼"].unique()
        )

        # 顯示該顧客的消費紀錄
        service_records = get_service_records(license_plate)
        st.session_state.service_records = service_records
        edited_service_records = st.data_editor(
            service_records, num_rows="dynamic", key="service_record_editor"
        )

        # 保存消費紀錄
        if st.button("保存消費紀錄修改"):
            # 檢查哪些資料被刪除
            deleted_data = service_records.loc[
                ~service_records["ID"].isin(edited_service_records["ID"])
            ]

            # 刪除已被移除的顧客資料
            with sqlite3.connect("data/motorcycle_shop.db") as conn:
                cursor = conn.cursor()
                for _, row in deleted_data.iterrows():
                    cursor.execute(
                        "DELETE FROM service_records WHERE ID = ?", (row["ID"],)
                    )
                conn.commit()

            # 新增/修改消費紀錄
            for index, row in edited_service_records.iterrows():
                update_or_add_service_record(
                    record_id=row["ID"],
                    license_plate=row["車牌號碼"],
                    date=row["日期"],
                    consumption=row["消費內容"],
                    amount=row["本次消費金額"],
                    notes=row["備註"],
                    oil_mileage=row["機油里程"],
                )
            st.success("消費紀錄已更新！")

        # 匯出消費記錄
        st.session_state.service_records = get_service_records(license_plate)
        service_records_buffer = BytesIO()
        st.session_state.service_records.to_excel(
            service_records_buffer, index=False, engine="openpyxl"
        )
        service_records_buffer.seek(0)

        st.download_button(
            label="匯出消費記錄為 Excel",
            data=service_records_buffer,
            file_name="service_records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
