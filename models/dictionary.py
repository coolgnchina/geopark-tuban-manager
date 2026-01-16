from . import db


class Dictionary(db.Model):
    __tablename__ = "dictionaries"

    id = db.Column(db.Integer, primary_key=True)
    dict_type = db.Column(db.String(50), nullable=False, comment="字典类型", index=True)
    dict_code = db.Column(db.String(50), nullable=False, comment="字典编码", index=True)
    dict_value = db.Column(db.String(100), nullable=False, comment="字典值")
    sort_order = db.Column(db.Integer, default=0, comment="排序")

    def __repr__(self):
        return f"<Dictionary {self.dict_type}:{self.dict_value}>"
