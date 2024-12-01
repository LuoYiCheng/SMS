import sqlite3
import pandas as pd
import streamlit as st


# 初始化資料庫
def init_db():
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT UNIQUE NOT NULL,
                brand TEXT,
                motorcycle_model TEXT,
                name TEXT,
                contact TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS service_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT,
                date TEXT,
                consumption TEXT,
                notes TEXT,
                oil_mileage INTEGER,
                amount INTEGER,  -- 新增金額欄位
                FOREIGN KEY (license_plate) REFERENCES customers (license_plate)
            )
            """
        )
        conn.commit()


# 查詢顧客
def get_customer(license_plate):
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT license_plate, brand, motorcycle_model, name, contact
            FROM customers WHERE license_plate = ?
        """,
            (license_plate,),
        )
        return cursor.fetchone()


# 新增顧客
def add_customer(license_plate, brand, motorcycle_model, name, contact):
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO customers (license_plate, brand, motorcycle_model, name, contact)
                VALUES (?, ?, ?, ?, ?)
                """,
                (license_plate, brand, motorcycle_model, name, contact),
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"車牌號碼 {license_plate} 已經存在。") from e


# 新增消費紀錄
def add_service_record(license_plate, date, consumption, amount, notes, oil_mileage):
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO service_records (license_plate, date, consumption, amount, notes, oil_mileage)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (license_plate, date, consumption, amount, notes, oil_mileage),
        )
        conn.commit()


# 查詢消費歷史，並返回排序的 DataFrame
def get_service_records(license_plate):
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, license_plate, date, consumption, amount, notes, oil_mileage
            FROM service_records
            WHERE license_plate = ?
            ORDER BY date DESC
        """,
            (license_plate,),
        )
        # 轉換查詢結果為 DataFrame
        records = cursor.fetchall()
        columns = [
            "ID",
            "車牌號碼",
            "日期",
            "消費內容",
            "本次消費金額",
            "備註",
            "機油里程",
        ]
        return pd.DataFrame(records, columns=columns)


# 查詢所有顧客資料
def get_all_customers():
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT license_plate, brand, motorcycle_model, name, contact 
            FROM customers
            """
        )
        records = cursor.fetchall()
        columns = ["車牌號碼", "廠牌", "車款", "姓名", "聯絡方式"]
        return pd.DataFrame(records, columns=columns)


# 更新顧客資料
def update_or_add_customer(license_plate, brand, motorcycle_model, name, contact):
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()

        # 檢查顧客是否已存在
        cursor.execute(
            "SELECT * FROM customers WHERE license_plate = ?",
            (license_plate,),
        )
        existing_customer = cursor.fetchone()

        if existing_customer:
            # 顧客已存在，執行更新
            cursor.execute(
                """
                UPDATE customers
                SET brand = ?, motorcycle_model = ?, name = ?, contact = ?
                WHERE license_plate = ?
                """,
                (brand, motorcycle_model, name, contact, license_plate),
            )
        else:
            # 顧客不存在，執行新增
            cursor.execute(
                """
                INSERT INTO customers (license_plate, brand, motorcycle_model, name, contact)
                VALUES (?, ?, ?, ?, ?)
                """,
                (license_plate, brand, motorcycle_model, name, contact),
            )

        conn.commit()


def update_or_add_service_record(
    record_id, license_plate, date, consumption, amount, notes, oil_mileage
):
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()

        # 檢查消費紀錄是否已存在，根據 id 或者 (車牌號碼, 日期) 判斷
        cursor.execute(
            "SELECT * FROM service_records WHERE id = ? OR (license_plate = ? AND date = ? AND consumption = ?)",
            (record_id, license_plate, date, consumption),
        )
        existing_record = cursor.fetchone()

        if existing_record:
            # 紀錄已存在，執行更新
            cursor.execute(
                """
                UPDATE service_records
                SET license_plate = ?, date = ?, consumption = ?, amount = ?, notes = ?, oil_mileage = ?
                WHERE id = ?
                """,
                (
                    license_plate,
                    date,
                    consumption,
                    amount,
                    notes,
                    oil_mileage,
                    record_id,
                ),
            )
        else:
            # 紀錄不存在，執行新增
            cursor.execute(
                """
                INSERT INTO service_records (license_plate, date, consumption, amount, notes, oil_mileage)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (license_plate, date, consumption, amount, notes, oil_mileage),
            )

        conn.commit()


# 匯出所有消費記錄
def export_service_records():
    with sqlite3.connect("data/motorcycle_shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, license_plate, date, consumption, amount, notes, oil_mileage
            FROM service_records
            ORDER BY date DESC
            """
        )
        records = cursor.fetchall()
        columns = ["ID", "車牌號碼", "日期", "消費內容", "金額", "備註", "機油里程"]
        return pd.DataFrame(records, columns=columns)
