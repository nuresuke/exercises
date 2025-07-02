from django.db import models


# Create your models here.
class Pokemon(models.Model):
    zukan_no = models.IntegerField(db_column="図鑑番号", primary_key=True)
    name = models.CharField(max_length=20, db_column="ポケモン名")
    type = models.CharField(max_length=10, db_column="タイプ")
    color = models.CharField(max_length=20, db_column="色")
    weight = models.FloatField(db_column="重さ")
    height = models.FloatField(db_column="大きさ")
    evolution = models.IntegerField(db_column="進化段階")
    can_fly = models.BooleanField(db_column="飛行可能か")
    habitat = models.CharField(max_length=50, db_column="生息地")
    is_legendary = models.BooleanField(db_column="伝説のポケモン")
    feature = models.CharField(max_length=50, db_column="外見的特徴")
    is_fossil = models.BooleanField(db_column="化石ポケモン")
    has_special_skill = models.CharField(max_length=20, db_column="代表的な技")  # 型に注意
    has_sash = models.BooleanField(db_column="サトシの所持の有無")
    characteristic = models.CharField(max_length=10, db_column="特性")
    initial = models.CharField(max_length=1, db_column="頭文字")
    class Meta:
        db_table = "pokemons"
        app_label = 'Akinator'
    
    def to_dict(self):
        return {
            "zukan_no": self.zukan_no,
            "name": self.name,
            "type": self.type,
            "color": self.color,
            "weight": self.weight,
            "height": self.height,
            "evolution": self.evolution,
            "can_fly": self.can_fly,
            "habitat": self.habitat,
            "is_legendary": self.is_legendary,
            "feature": self.feature,
            "is_fossil": self.is_fossil,
            "has_special_skill": self.has_special_skill,
            "has_sash": self.has_sash,
            "characteristic": self.characteristic,
            "initial": self.initial,
        }
