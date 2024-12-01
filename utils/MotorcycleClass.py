class MotorcycleRecord:
    def __init__(self, license_plate, owner_name, contact):
        self.license_plate = license_plate  # 車牌號碼
        self.owner_name = owner_name  # 車主姓名
        self.contact = contact  # 聯絡方式
        self.history = []  # 歷史消費記錄，儲存多筆消費資料
        self.total_oil_mileage = 0  # 累積機油里程

    def add_service_record(self, date, consumption, notes, oil_mileage):
        """
        新增一筆服務記錄
        """
        record = {
            "date": date,
            "consumption": consumption,
            "notes": notes,
            "oil_mileage": oil_mileage,
        }
        self.history.append(record)
        self.total_oil_mileage += oil_mileage  # 更新累積機油里程

    def get_history(self):
        """
        返回完整的歷史記錄
        """
        return self.history

    def get_total_oil_mileage(self):
        """
        返回累積機油里程
        """
        return self.total_oil_mileage

    def to_dict(self):
        """
        將記錄轉換為字典格式，用於儲存到資料框
        """
        return {
            "車牌號碼": self.license_plate,
            "姓名": self.owner_name,
            "聯絡方式": self.contact,
            "消費歷史": self.history,
            "累積機油里程": self.total_oil_mileage,
        }
