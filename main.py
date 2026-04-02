import sys
import os
import random
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QMessageBox, QFrame,
                             QSpacerItem, QSizePolicy, QProgressBar, QScrollArea, QDialog, QGridLayout, QLineEdit)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt, pyqtSignal

BRANS_AYARLARI = {
    "Futbol": {"renk": "#4CAF50", "ozellikler": ["Penaltı", "Serbest Vuruş", "Karşı Karşıya"]},
    "Basketbol": {"renk": "#FF9800", "ozellikler": ["Üçlük", "İkilik", "Serbest Atış"]},
    "Voleybol": {"renk": "#2196F3", "ozellikler": ["Servis", "Blok", "Smaç"]}
}


class OzelYetenek(ABC):
    @abstractmethod
    def uygula(self, temel_puan, kart, rakip_yetenek, guncel_tur):
        pass


class ClutchPlayerYetenek(OzelYetenek):
    def uygula(self, temel_puan, kart, rakip_yetenek, guncel_tur):
        bonus_etki_orani = 0.5 if rakip_yetenek == "Defender" else 1.0
        bonus = 10 * bonus_etki_orani if guncel_tur >= 9 else 0
        return bonus, 1.0


class LegendYetenek(OzelYetenek):
    def uygula(self, temel_puan, kart, rakip_yetenek, guncel_tur):
        if not kart.legend_kullanildi:
            kart.legend_kullanildi = True
            return 0, 2.0
        return 0, 1.0


class FinisherYetenek(OzelYetenek):
    def uygula(self, temel_puan, kart, rakip_yetenek, guncel_tur):
        bonus_etki_orani = 0.5 if rakip_yetenek == "Defender" else 1.0
        bonus = 8 * bonus_etki_orani if kart.enerji < 40 else 0
        return bonus, 1.0


class PasifYetenek(OzelYetenek):
    def uygula(self, temel_puan, kart, rakip_yetenek, guncel_tur):
        return 0, 1.0


YETENEK_STRATEJILERI = {
    "Clutch Player": ClutchPlayerYetenek(),
    "Legend": LegendYetenek(),
    "Finisher": FinisherYetenek()
}


class KartDetayDialog(QDialog):
    def __init__(self, kart, parent=None):
        super().__init__(parent)
        self.kart = kart
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Sporcu Profili: {self.kart.isim}")
        self.setFixedSize(650, 850)
        self.setStyleSheet("background-color: #0c0e12; color: white; border: 1px solid #333;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        lbl_foto = QLabel()
        lbl_foto.setFixedSize(250, 250)
        dosya_adi = self.kart.isim.lower().replace(" ", "_") + ".jpg"
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), dosya_adi))
        if not pixmap.isNull():
            lbl_foto.setPixmap(pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            lbl_foto.setStyleSheet("border: 4px solid #1a1e26; border-radius: 15px;")
        else:
            lbl_foto.setStyleSheet("background-color: #1a1a1a; border-radius: 15px;")
            lbl_foto.setAlignment(Qt.AlignCenter)
            lbl_foto.setText("RESİM YOK")

        info_v_layout = QVBoxLayout()
        lbl_isim = QLabel(self.kart.isim.upper())
        lbl_isim.setFont(QFont("Arial", 22, QFont.Bold))
        lbl_isim.setStyleSheet(f"color: {BRANS_AYARLARI[self.kart.brans]['renk']}; border: none;")
        lbl_isim.setWordWrap(True)
        lbl_isim.setMaximumWidth(300)

        lbl_takim = QLabel(f"🛡 {self.kart.takim}\n📍 {self.kart.brans.upper()}")
        lbl_takim.setFont(QFont("Arial", 12))
        lbl_takim.setStyleSheet("color: #aaa; border: none;")

        reyting_box = QFrame()
        reyting_box.setStyleSheet(
            f"background-color: {BRANS_AYARLARI[self.kart.brans]['renk']}; border-radius: 10px; border: none;")
        r_layout = QVBoxLayout(reyting_box)
        lbl_r_val = QLabel(f"★ {self.kart.genel_reyting}")
        lbl_r_val.setFont(QFont("Arial", 24, QFont.Bold))
        lbl_r_val.setStyleSheet("color: black; border: none;")
        lbl_r_val.setAlignment(Qt.AlignCenter)
        r_layout.addWidget(lbl_r_val)

        info_v_layout.addWidget(lbl_isim)
        info_v_layout.addWidget(lbl_takim)
        info_v_layout.addStretch()
        info_v_layout.addWidget(QLabel("GENEL REYTING", styleSheet="color: #666; font-weight: bold; border:none;"))
        info_v_layout.addWidget(reyting_box)

        header_layout.addWidget(lbl_foto)
        header_layout.addLayout(info_v_layout)
        main_layout.addWidget(header_widget)

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        for i, (oz_ad, deger) in enumerate(self.kart.get_ozellikler().items()):
            box = QFrame()
            box.setStyleSheet(f"background-color: #1a1e26; border: 2px solid #333; border-radius: 12px;")
            b_lay = QVBoxLayout(box)
            b_lay.setAlignment(Qt.AlignCenter)
            v_lbl = QLabel(str(deger))
            v_lbl.setFont(QFont("Arial", 26, QFont.Bold))
            v_lbl.setStyleSheet("border:none; color: white;")
            k_lbl = QLabel(oz_ad.upper())
            k_lbl.setFont(QFont("Arial", 10, QFont.Bold))
            k_lbl.setStyleSheet("border:none; color: #888;")
            b_lay.addWidget(v_lbl, alignment=Qt.AlignCenter)
            b_lay.addWidget(k_lbl, alignment=Qt.AlignCenter)
            grid_layout.addWidget(box, 0, i)
        main_layout.addWidget(grid_widget)

        stats_layout = QHBoxLayout()

        def istatistik_kutusu(title, value):
            box = QFrame()
            box.setStyleSheet("background-color: #14161d; border-radius: 10px; border: 1px solid #222;")
            l = QVBoxLayout(box)
            l.setAlignment(Qt.AlignCenter)
            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("color: #555; font-size: 10px; font-weight: bold; border:none;")
            v_lbl = QLabel(str(value))
            v_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold; border:none;")
            l.addWidget(t_lbl, alignment=Qt.AlignCenter)
            l.addWidget(v_lbl, alignment=Qt.AlignCenter)
            return box

        stats_layout.addWidget(istatistik_kutusu("SEVİYE", f"S{self.kart.seviye}"))
        stats_layout.addWidget(istatistik_kutusu("DENEYİM", f"{self.kart.deneyim_puani} XP"))
        stats_layout.addWidget(istatistik_kutusu("ENERJİ", f"%{self.kart.enerji}"))
        stats_layout.addWidget(istatistik_kutusu("DAYANIKLILIK", self.kart._dayaniklilik))
        main_layout.addLayout(stats_layout)

        gm_box = QFrame()
        gm_box.setStyleSheet("background-color: #14161d; border-radius: 10px; border: 1px solid #222; padding: 5px;")
        gm_layout = QHBoxLayout(gm_box)
        gm_layout.addWidget(QLabel(f"✅ GALİBİYET: {self.kart.kazanma_sayisi}",
                                   styleSheet="color: #4CAF50; font-weight: bold; border:none;"))
        gm_layout.addStretch()
        gm_layout.addWidget(QLabel(f"❌ MAĞLUBİYET: {self.kart.kaybetme_sayisi}",
                                   styleSheet="color: #f44336; font-weight: bold; border:none;"))
        main_layout.addWidget(gm_box)

        yetenek_box = QFrame()
        yetenek_box.setStyleSheet(
            "background-color: #0f1117; border-left: 5px solid #FFD700; padding: 15px; border-radius: 5px;")
        y_lay = QVBoxLayout(yetenek_box)
        y_title = QLabel(f"✨ ÖZEL YETENEK: {self.kart.ozel_yetenek}")
        y_title.setFont(QFont("Arial", 12, QFont.Bold))
        y_title.setStyleSheet("color: #FFD700; border:none;")
        y_desc = QLabel(self.yetenek_aciklamasi_getir(self.kart.ozel_yetenek))
        y_desc.setWordWrap(True)
        y_desc.setStyleSheet("color: #bbb; border:none;")
        y_lay.addWidget(y_title)
        y_lay.addWidget(y_desc)
        main_layout.addWidget(yetenek_box)

        main_layout.addStretch()
        btn_kapat = QPushButton("PROFİLİ KAPAT")
        btn_kapat.setFixedSize(220, 50)
        btn_kapat.setCursor(Qt.PointingHandCursor)
        btn_kapat.setStyleSheet("background-color: #333; color: white; border-radius: 8px; font-weight: bold;")
        btn_kapat.clicked.connect(self.close)
        main_layout.addWidget(btn_kapat, alignment=Qt.AlignCenter)

    def yetenek_aciklamasi_getir(self, yetenek):
        aciklamalar = {
            "Clutch Player": "Maçın kritik son 3 turunda oyuncuya +10 performans bonusu sağlar.",
            "Captain": "Sahada olduğu sürece aynı branştaki tüm takım arkadaşlarına +5 moral desteği verir.",
            "Legend": "Efsanevi yeteneği ile maçta bir kez seçilen ana özelliğin etkisini ikiye katlar.",
            "Defender": "Savunma uzmanlığı sayesinde rakibin kazandığı özel yetenek bonuslarını yarıya indirir.",
            "Veteran": "Tecrübesi ile maç sırasındaki enerji kaybını %50 oranında azaltır.",
            "Finisher": "Enerjisi %40'ın altına düştüğünde pes etmez ve +8 ek bitiricilik bonusu alır."
        }
        return aciklamalar.get(yetenek, "Özel yetenek bilgisi bulunamadı.")


class KartSecmeStratejisi(ABC):
    @abstractmethod
    def kart_sec(self, uygun_kartlar):
        pass


class KolayStrateji(KartSecmeStratejisi):
    def kart_sec(self, uygun_kartlar):
        return random.choice(uygun_kartlar)


class OrtaStrateji(KartSecmeStratejisi):
    def kart_sec(self, uygun_kartlar):
        en_yuksek_guc = -1
        en_iyi_adaylar = []
        for kart in uygun_kartlar:
            toplam_guc = sum(kart.get_ozellikler().values()) + kart.enerji
            if toplam_guc > en_yuksek_guc:
                en_yuksek_guc = toplam_guc
                en_iyi_adaylar = [kart]
            elif toplam_guc == en_yuksek_guc:
                en_iyi_adaylar.append(kart)
        return random.choice(en_iyi_adaylar)


class Sporcu(ABC):
    def __init__(self, sporcu_id, isim, takim, brans, dayaniklilik, enerji, ozel_yetenek, ozellikler, moral, reyting):
        self.sporcu_id = sporcu_id
        self.isim = isim
        self.takim = takim
        self.brans = brans
        self._dayaniklilik = int(dayaniklilik)
        self._enerji = int(enerji)
        self.max_enerji = int(enerji)
        self.ozel_yetenek = ozel_yetenek.strip()
        self.moral = int(moral)
        self.genel_reyting = int(float(reyting))
        self.ozellikler = {}
        for anahtar, deger in ozellikler.items():
            self.ozellikler[anahtar] = int(deger)
        self.seviye = 1
        self.deneyim_puani = 0
        self.kart_kullanildi_mi = False
        self.kazanma_sayisi = 0
        self.kaybetme_sayisi = 0
        self.legend_kullanildi = False
        self.seviye_atladiktan_sonra_ilk_mac = False

    @property
    def enerji(self):
        return self._enerji

    @enerji.setter
    def enerji(self, deger):
        if deger < 0:
            self._enerji = 0
        elif deger > self.max_enerji:
            self._enerji = self.max_enerji
        else:
            self._enerji = deger

    @abstractmethod
    def enerji_guncelle(self, miktar):
        pass

    @abstractmethod
    def performans_hesapla(self, temel_puan, rakip_yetenek="", guncel_tur=0):
        pass

    def moral_guncelle_bireysel(self, sonuc):
        if sonuc == "kazandi":
            self.moral += 10
        elif sonuc == "kaybetti":
            self.moral -= 5
        self.moral = max(0, min(100, self.moral))

    def deneyim_guncelle(self, sonuc):
        if sonuc == "kazandi":
            self.deneyim_puani = self.deneyim_puani + 2
            self.kazanma_sayisi = self.kazanma_sayisi + 1
        elif sonuc == "berabere":
            self.deneyim_puani = self.deneyim_puani + 1
        else:
            self.kaybetme_sayisi = self.kaybetme_sayisi + 1
        self.seviye_atla_kontrol()

    def seviye_atla_kontrol(self):
        seviye_atladi_mi = False
        if self.seviye == 1:
            if self.kazanma_sayisi >= 2 or self.deneyim_puani >= 4:
                seviye_atladi_mi = True
        elif self.seviye == 2:
            if self.kazanma_sayisi >= 4 or self.deneyim_puani >= 8:
                seviye_atladi_mi = True
        if seviye_atladi_mi:
            self.seviye = self.seviye + 1
            self.seviye_atladiktan_sonra_ilk_mac = True
            self.max_enerji = self.max_enerji + 10
            self.enerji = self.enerji + 10
            self._dayaniklilik = self._dayaniklilik + 5
            for key in self.ozellikler:
                self.ozellikler[key] = self.ozellikler[key] + 5

    def get_ozellikler(self):
        return self.ozellikler


class AktifSporcu(Sporcu):
    def enerji_guncelle(self, miktar):
        if miktar < 0 and self.ozel_yetenek == "Veteran":
            miktar = miktar * 0.5
        self.enerji = self.enerji + miktar

    def performans_hesapla(self, temel_puan, rakip_yetenek="", guncel_tur=0):
        if self.enerji == 0: return 0
        enerji_cezasi = 0
        if self.enerji < 40:
            enerji_cezasi = temel_puan * 0.20
        elif self.enerji <= 70:
            enerji_cezasi = temel_puan * 0.10
        moral_bonusu = 10 if self.moral >= 80 else 5 if self.moral >= 50 else -5
        seviye_bonusu = 5 if self.seviye == 2 else 10 if self.seviye == 3 else 0
        strateji = YETENEK_STRATEJILERI.get(self.ozel_yetenek, PasifYetenek())
        yetenek_bonusu, temel_carpan = strateji.uygula(temel_puan, self, rakip_yetenek, guncel_tur)
        sonuc = (temel_puan * temel_carpan) + moral_bonusu + yetenek_bonusu - enerji_cezasi + seviye_bonusu
        return round(sonuc, 2)


class Oyuncu(ABC):
    def __init__(self, oyuncu_id, isim):
        self.oyuncu_id = oyuncu_id
        self.isim = isim
        self.skor = 0
        self.moral = 60
        self.kart_listesi = []
        self.galibiyet_serisi = 0

    @abstractmethod
    def moral_guncelle(self, sonuc):
        pass


class Kullanici(Oyuncu):
    def moral_guncelle(self, sonuc):
        if sonuc == "kazandi":
            self.galibiyet_serisi = self.galibiyet_serisi + 1
            if self.galibiyet_serisi == 2:
                self.moral = self.moral + 10
            elif self.galibiyet_serisi >= 3:
                self.moral = self.moral + 15
        elif sonuc == "kaybetti":
            self.galibiyet_serisi = 0
            self.moral = self.moral - 5
        self.moral = max(0, min(100, self.moral))


class Bilgisayar(Oyuncu):
    def __init__(self, oyuncu_id, isim):
        super().__init__(oyuncu_id, isim)
        self.strateji = OrtaStrateji()

    def strateji_belirle(self, strateji_objesi):
        self.strateji = strateji_objesi

    def ai_hamlesi(self, brans):
        uygun_kartlar = [kart for kart in self.kart_listesi if
                         kart.brans == brans and not kart.kart_kullanildi_mi and kart.enerji > 0]
        if len(uygun_kartlar) == 0: return None
        return self.strateji.kart_sec(uygun_kartlar)

    def moral_guncelle(self, sonuc):
        if sonuc == "kazandi":
            self.galibiyet_serisi = self.galibiyet_serisi + 1
            if self.galibiyet_serisi == 2:
                self.moral = self.moral + 10
            elif self.galibiyet_serisi >= 3:
                self.moral = self.moral + 15
        elif sonuc == "kaybetti":
            self.galibiyet_serisi = 0
            self.moral = self.moral - 10
        self.moral = max(0, min(100, self.moral))


class VeriOkuyucu:
    @staticmethod
    def dosya_oku(dosya_yolu):
        kart_listesi = []
        if not os.path.exists(dosya_yolu):
            raise FileNotFoundError(f"'{dosya_yolu}' dosyası bulunamadı!")
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            satir_sayisi = 0
            for satir in dosya:
                satir_sayisi += 1
                satir = satir.strip()
                if not satir or satir.startswith("Branş"): continue
                veriler = satir.split(",")
                temiz_veriler = [v.strip() for v in veriler]
                if len(temiz_veriler) != 12:
                    raise ValueError(f"Hata: {satir_sayisi}. satırda 12 sütun bekleniyor!")
                try:
                    brans, s_id, isim, takim, dayan, enerji, yetenek, oz1, oz2, oz3, moral, reyting = temiz_veriler
                    brans_isim = brans.capitalize()
                    if brans_isim in BRANS_AYARLARI:
                        anahtarlar = BRANS_AYARLARI[brans_isim]["ozellikler"]
                        ozellikler_dict = {anahtarlar[0]: oz1, anahtarlar[1]: oz2, anahtarlar[2]: oz3}
                        yeni_kart = AktifSporcu(int(s_id), isim, takim, brans_isim, int(dayan), int(enerji), yetenek,
                                                ozellikler_dict, int(moral), reyting)
                        kart_listesi.append(yeni_kart)
                except ValueError:
                    raise ValueError(f"Hata: {satir_sayisi}. satırda sayısal beklenen verilerde hata var!")
        return kart_listesi


class OyunYonetici:
    def __init__(self, oyuncu, bilgisayar):
        self.oyuncu = oyuncu
        self.bilgisayar = bilgisayar
        self.tur_sirasi = list(BRANS_AYARLARI.keys())
        self.guncel_tur = 0
        self.guncel_ozellik = ""

    def kartlari_dagit(self, tum_kartlar):
        for b in self.tur_sirasi:
            brans_kartlari = [k for k in tum_kartlar if k.brans == b]
            if len(brans_kartlari) < 8: return False
            random.shuffle(brans_kartlari)
            for i in range(4): self.oyuncu.kart_listesi.append(brans_kartlari[i])
            for i in range(4, 8): self.bilgisayar.kart_listesi.append(brans_kartlari[i])
        return True

    def tur_kazanani_belirle(self, k_kart, b_kart, ana_ozellik, guncel_tur):
        o_puan = k_kart.performans_hesapla(k_kart.get_ozellikler()[ana_ozellik], b_kart.ozel_yetenek, guncel_tur)
        b_puan = b_kart.performans_hesapla(b_kart.get_ozellikler()[ana_ozellik], k_kart.ozel_yetenek, guncel_tur)
        if o_puan > b_puan: return "kullanici", o_puan, b_puan
        if b_puan > o_puan: return "bilgisayar", o_puan, b_puan
        yedek_ozellik_listesi = BRANS_AYARLARI[k_kart.brans]["ozellikler"]
        for oz in yedek_ozellik_listesi:
            if oz == ana_ozellik: continue
            o_yedek = k_kart.get_ozellikler()[oz]
            b_yedek = b_kart.get_ozellikler()[oz]
            if o_yedek > b_yedek: return "kullanici", o_puan, b_puan
            if b_yedek > o_yedek: return "bilgisayar", o_puan, b_puan
        o_yet_puan, _ = YETENEK_STRATEJILERI.get(k_kart.ozel_yetenek, PasifYetenek()).uygula(0, k_kart,
                                                                                             b_kart.ozel_yetenek,
                                                                                             guncel_tur)
        b_yet_puan, _ = YETENEK_STRATEJILERI.get(b_kart.ozel_yetenek, PasifYetenek()).uygula(0, b_kart,
                                                                                             k_kart.ozel_yetenek,
                                                                                             guncel_tur)
        if o_yet_puan > b_yet_puan: return "kullanici", o_puan, b_puan
        if b_yet_puan > o_yet_puan: return "bilgisayar", o_puan, b_puan
        if k_kart._dayaniklilik > b_kart._dayaniklilik: return "kullanici", o_puan, b_puan
        if b_kart._dayaniklilik > k_kart._dayaniklilik: return "bilgisayar", o_puan, b_puan
        if k_kart.enerji > b_kart.enerji: return "kullanici", o_puan, b_puan
        if b_kart.enerji > k_kart.enerji: return "bilgisayar", o_puan, b_puan
        if k_kart.seviye > b_kart.seviye: return "kullanici", o_puan, b_puan
        if b_kart.seviye > k_kart.seviye: return "bilgisayar", o_puan, b_puan
        return "berabere", o_puan, b_puan

    def tur_sonucu_uygula(self, kazanan, kaybeden, k_kart, y_kart):
        tur_puani = 10
        if k_kart.ozel_yetenek == "Clutch Player" and self.guncel_tur >= 9: tur_puani = 15
        if kazanan.galibiyet_serisi + 1 == 3:
            tur_puani += 10
        elif kazanan.galibiyet_serisi + 1 >= 5:
            tur_puani += 20
        if k_kart.enerji < 30: tur_puani += 5
        if k_kart.seviye_atladiktan_sonra_ilk_mac:
            tur_puani += 5
            k_kart.seviye_atladiktan_sonra_ilk_mac = False
        if k_kart.ozel_yetenek == "Clutch Player" and self.guncel_tur >= 9: tur_puani += 5
        kazanan.skor += tur_puani
        kazanan.moral_guncelle("kazandi");
        kaybeden.moral_guncelle("kaybetti")
        k_kart.moral_guncelle_bireysel("kazandi");
        y_kart.moral_guncelle_bireysel("kaybetti")
        k_kart.deneyim_guncelle("kazandi");
        y_kart.deneyim_guncelle("kaybetti")
        k_kart.enerji_guncelle(-5);
        y_kart.enerji_guncelle(-10)


class KartGorunumu(QFrame):
    tiklandi = pyqtSignal(object)

    def __init__(self, kart, aktif_mi):
        super().__init__()
        self.kart = kart
        self.aktif_mi = aktif_mi
        self.tema_renk = BRANS_AYARLARI.get(kart.brans, {}).get("renk", "#FFFFFF")
        self.initUI()

    def initUI(self):
        self.setFixedSize(180, 380)
        arkaplan = "#1e222b" if self.aktif_mi else "#2a2a2a"
        cerceve_renk = self.tema_renk if self.aktif_mi else "#555555"
        self.setStyleSheet(
            f"KartGorunumu {{ background-color: {arkaplan}; border-radius: 12px; border: 3px solid {cerceve_renk}; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        btn_detay = QPushButton("ⓘ", self)
        btn_detay.setFixedSize(24, 24)
        btn_detay.move(145, 10)
        btn_detay.setCursor(Qt.PointingHandCursor)
        btn_detay.setStyleSheet(
            f"QPushButton {{ background-color: {self.tema_renk}; color: black; border-radius: 12px; font-weight: bold; border: none; }}")
        btn_detay.clicked.connect(self.detay_ekrani_ac)
        ust_bilgi_layout = QHBoxLayout()
        lbl_seviye = QLabel(f"S{self.kart.seviye}")
        lbl_seviye.setStyleSheet(f"color: {self.tema_renk}; font-weight: bold; font-size: 12px; border:none;")
        lbl_genel_reyting = QLabel(f"★{self.kart.genel_reyting}")
        lbl_genel_reyting.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 12px; border:none;")
        ust_bilgi_layout.addWidget(lbl_seviye);
        ust_bilgi_layout.addStretch();
        ust_bilgi_layout.addWidget(lbl_genel_reyting);
        ust_bilgi_layout.addStretch()
        layout.addLayout(ust_bilgi_layout)
        lbl_resim = QLabel()
        lbl_resim.setFixedSize(154, 90)
        dosya_adi = self.kart.isim.lower().replace(" ", "_") + ".jpg"
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), dosya_adi))
        if not pixmap.isNull():
            lbl_resim.setPixmap(pixmap.scaled(154, 90, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            lbl_resim.setStyleSheet("background-color: #111; border-radius: 5px;")
        layout.addWidget(lbl_resim, alignment=Qt.AlignCenter)
        lbl_isim = QLabel(f"{self.kart.isim.upper()}")
        lbl_isim.setFont(QFont("Arial", 10, QFont.Bold));
        lbl_isim.setAlignment(Qt.AlignCenter);
        lbl_isim.setWordWrap(True)
        lbl_isim.setStyleSheet(f"color: {'white' if self.aktif_mi else '#888'}; border: none;")
        layout.addWidget(lbl_isim)
        yazi_renk = "white" if self.aktif_mi else "#888"
        layout.addWidget(QLabel(f"ENERJİ: %{int(self.kart.enerji)}",
                                styleSheet=f"color: {yazi_renk}; font-size: 9px; font-weight: bold; border: none;"))
        bar_enerji = QProgressBar();
        bar_enerji.setValue(int(self.kart.enerji));
        bar_enerji.setFixedHeight(6);
        bar_enerji.setTextVisible(False)
        bar_enerji.setStyleSheet(
            f"QProgressBar {{ background-color: #333; border: none; border-radius: 3px; }} QProgressBar::chunk {{ background-color: {self.tema_renk if self.aktif_mi else '#666'}; border-radius: 3px; }}")
        layout.addWidget(bar_enerji)
        layout.addWidget(QLabel(f"MORAL: {self.kart.moral}",
                                styleSheet=f"color: {yazi_renk}; font-size: 9px; font-weight: bold; border: none;"))
        bar_moral = QProgressBar();
        bar_moral.setValue(self.kart.moral);
        bar_moral.setFixedHeight(6);
        bar_moral.setTextVisible(False)
        moral_bar_renk = "#4CAF50" if self.kart.moral >= 80 else "#FF9800" if self.kart.moral >= 50 else "#f44336"
        bar_moral.setStyleSheet(
            f"QProgressBar {{ background-color: #333; border: none; border-radius: 3px; }} QProgressBar::chunk {{ background-color: {moral_bar_renk if self.aktif_mi else '#666'}; border-radius: 3px; }}")
        layout.addWidget(bar_moral)
        ozellik_konteyner = QFrame();
        ozellik_konteyner.setStyleSheet("border: none; background: transparent;")
        ozellik_layout = QVBoxLayout(ozellik_konteyner);
        ozellik_layout.setContentsMargins(2, 5, 2, 5);
        ozellik_layout.setSpacing(3)
        yazi_stili = f"color: {yazi_renk if self.aktif_mi else '#888'}; font-size: 10px; border: none; font-weight: bold;"
        for oz_ad, deger in self.kart.get_ozellikler().items():
            lbl = QLabel(f"➤ {oz_ad.upper()}: {deger}");
            lbl.setStyleSheet(yazi_stili);
            ozellik_layout.addWidget(lbl)
        lbl_dayan = QLabel(f"🛡 DAYANIKLILIK: {self.kart._dayaniklilik}");
        lbl_dayan.setStyleSheet(yazi_stili);
        ozellik_layout.addWidget(lbl_dayan)
        layout.addWidget(ozellik_konteyner)
        lbl_yetenek = QLabel(self.kart.ozel_yetenek.upper());
        lbl_yetenek.setFont(QFont("Arial", 9, QFont.Bold));
        lbl_yetenek.setAlignment(Qt.AlignCenter)
        lbl_yetenek.setStyleSheet(
            f"background-color: {self.tema_renk if self.aktif_mi else '#444'}; color: {'black' if self.aktif_mi else '#888'}; border-radius: 5px; padding: 4px;")
        layout.addWidget(lbl_yetenek)

    def detay_ekrani_ac(self):
        KartDetayDialog(self.kart, self).exec_()

    def mousePressEvent(self, event):
        if self.aktif_mi: self.tiklandi.emit(self.kart)


class AnaPencere(QMainWindow):
    def __init__(self, oyun_yonetici):
        super().__init__()
        self.oyun = oyun_yonetici
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sporcu Kartları Ligi");
        self.setGeometry(50, 50, 1500, 950)

        # ANA OYUN EKRANI ARKA PLANINI AYARLA
        self.arka_plan_ayarla("arka_plan.png")

        merkez_widget = QWidget();
        self.setCentralWidget(merkez_widget);
        self.ana_layout = QVBoxLayout(merkez_widget);
        bilgi_layout = QHBoxLayout()
        self.lbl_skor = QLabel();
        self.lbl_skor.setFont(QFont("Arial", 20, QFont.Bold))
        self.btn_ai_goster = QPushButton("AI KARTLARINI GÖSTER");
        self.btn_ai_goster.setCheckable(True);
        self.btn_ai_goster.setFixedWidth(220)
        self.btn_ai_goster.setStyleSheet(
            "QPushButton { background-color: #333; padding: 12px; border: 1px solid #555; border-radius: 6px; font-weight: bold; } QPushButton:checked { background-color: #b33; }")
        self.btn_ai_goster.clicked.connect(self.arayuzu_guncelle)
        self.lbl_tur = QLabel();
        self.lbl_tur.setFont(QFont("Arial", 20, QFont.Bold))
        bilgi_layout.addWidget(self.lbl_skor);
        bilgi_layout.addStretch();
        bilgi_layout.addWidget(self.btn_ai_goster);
        bilgi_layout.addStretch();
        bilgi_layout.addWidget(self.lbl_tur);
        self.ana_layout.addLayout(bilgi_layout)
        self.lbl_ozellik_bilgi = QLabel();
        self.lbl_ozellik_bilgi.setFont(QFont("Arial", 16, QFont.Bold));
        self.lbl_ozellik_bilgi.setAlignment(Qt.AlignCenter);
        self.lbl_ozellik_bilgi.setStyleSheet(
            "color: #FFD700; background-color: rgba(26,26,26,200); padding: 10px; border-radius: 5px;")
        self.ana_layout.addWidget(self.lbl_ozellik_bilgi)
        self.ai_scroll = QScrollArea();
        self.ai_scroll.setWidgetResizable(True);
        self.ai_scroll.setFixedHeight(400);
        self.ai_scroll.setVisible(False);
        self.ai_scroll.setStyleSheet("border: 1px dashed #444; background-color: transparent;")
        self.ai_container = QWidget();
        self.ai_container.setStyleSheet("background-color:transparent;");
        self.ai_layout = QHBoxLayout(self.ai_container);
        self.ai_scroll.setWidget(self.ai_container);
        self.ana_layout.addWidget(QLabel("RAKİP KARTLARI (BİLGİSAYAR):"));
        self.ana_layout.addWidget(self.ai_scroll)
        icerik_widget = QWidget();
        icerik_widget.setStyleSheet("background-color: transparent;");
        self.kart_layout = QHBoxLayout(icerik_widget);
        self.kart_layout.setAlignment(Qt.AlignLeft)
        scroll_area = QScrollArea();
        scroll_area.setWidgetResizable(True);
        scroll_area.setStyleSheet("border: none; background-color: transparent;");
        scroll_area.setWidget(icerik_widget);
        self.ana_layout.addWidget(QLabel("SENİN KARTLARIN:"));
        self.ana_layout.addWidget(scroll_area)
        self.yeni_ozellik_sec();
        self.arayuzu_guncelle()

    def arka_plan_ayarla(self, image_path):
        if os.path.exists(image_path):
            self.setAutoFillBackground(True)
            palette = self.palette()
            pixmap = QPixmap(image_path).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)
        else:
            self.setStyleSheet("background-color: #0c0e12; color: white;")

    def resizeEvent(self, event):
        # Pencere boyutu değiştikçe arka planı tekrar ölçekle
        self.arka_plan_ayarla("arka_plan.png")
        super().resizeEvent(event)

    def yeni_ozellik_sec(self):
        indeks = self.oyun.guncel_tur % 3;
        siradaki_brans = self.oyun.tur_sirasi[indeks]
        self.oyun.guncel_ozellik = random.choice(BRANS_AYARLARI[siradaki_brans]["ozellikler"])

    def arayuzu_guncelle(self):
        if self.oyun.guncel_tur >= 12: self.oyun_bitti_ekrani(); return
        self.lbl_skor.setText(
            f"🏆 {self.oyun.oyuncu.isim.upper()}: {self.oyun.oyuncu.skor} | AI: {self.oyun.bilgisayar.skor}")
        indeks = self.oyun.guncel_tur % 3;
        siradaki_brans = self.oyun.tur_sirasi[indeks];
        renk = BRANS_AYARLARI.get(siradaki_brans, {}).get("renk", "#FFF")
        self.lbl_tur.setText(f"SIRADAKİ BRANŞ: <span style='color:{renk};'>{siradaki_brans.upper()}</span>")
        self.lbl_ozellik_bilgi.setText(f"⚡ BU TUR KARŞILAŞTIRILACAK ÖZELLİK: {self.oyun.guncel_ozellik.upper()}")
        for i in reversed(range(self.ai_layout.count())): self.ai_layout.itemAt(i).widget().setParent(None)
        if self.btn_ai_goster.isChecked():
            self.ai_scroll.setVisible(True);
            self.btn_ai_goster.setText("AI KARTLARINI GİZLE")
            for kart in self.oyun.bilgisayar.kart_listesi:
                if not kart.kart_kullanildi_mi: self.ai_layout.addWidget(KartGorunumu(kart, False))
        else:
            self.ai_scroll.setVisible(False); self.btn_ai_goster.setText("AI KARTLARINI GÖSTER")
        for i in reversed(range(self.kart_layout.count())):
            wi = self.kart_layout.itemAt(i)
            if wi and wi.widget(): wi.widget().setParent(None)
        for kart in self.oyun.oyuncu.kart_listesi:
            if not kart.kart_kullanildi_mi:
                widget = KartGorunumu(kart, kart.brans == siradaki_brans);
                widget.tiklandi.connect(self.kart_secildi);
                self.kart_layout.addWidget(widget)

    def kart_secildi(self, secilen_kart):
        ozellik = self.oyun.guncel_ozellik;
        brans = self.oyun.tur_sirasi[self.oyun.guncel_tur % 3];
        ai_karti = self.oyun.bilgisayar.ai_hamlesi(brans)
        if ai_karti is None:
            QMessageBox.warning(self, "Uyarı", "AI enerjisi kalmadı, hükmen kazandın!");
            self.oyun.oyuncu.skor += 8;
            self.oyun.guncel_tur += 1;
            self.yeni_ozellik_sec();
            self.arayuzu_guncelle();
            return
        karar, o_guc, b_guc = self.oyun.tur_kazanani_belirle(secilen_kart, ai_karti, ozellik, self.oyun.guncel_tur)
        if secilen_kart.ozel_yetenek == "Captain":
            for target in self.oyun.oyuncu.kart_listesi:
                if target.brans == secilen_kart.brans and target != secilen_kart: target.moral = min(100,
                                                                                                     target.moral + 5)
        if ai_karti.ozel_yetenek == "Captain":
            for target in self.oyun.bilgisayar.kart_listesi:
                if target.brans == ai_karti.brans and target != ai_karti: target.moral = min(100, target.moral + 5)
        if karar == "kullanici":
            self.oyun.tur_sonucu_uygula(self.oyun.oyuncu, self.oyun.bilgisayar, secilen_kart,
                                        ai_karti); sonuc = "KAZANDIN! 🎉"
        elif karar == "bilgisayar":
            self.oyun.tur_sonucu_uygula(self.oyun.bilgisayar, self.oyun.oyuncu, ai_karti,
                                        secilen_kart); sonuc = "KAYBETTİN! 😢"
        else:
            secilen_kart.enerji_guncelle(-3); ai_karti.enerji_guncelle(-3); sonuc = "BERABERE! (Tüm değerler eşit) 🤝"
        if secilen_kart.enerji <= 0: secilen_kart.kart_kullanildi_mi = True
        if ai_karti.enerji <= 0: ai_karti.kart_kullanildi_mi = True
        self.oyun.guncel_tur += 1
        QMessageBox.information(self, "Tur Sonucu",
                                f"🎯 ÖZELLİK: {ozellik.upper()}\n\n{self.oyun.oyuncu.isim.upper()}: {secilen_kart.isim} (Puan: {o_guc})\nAI: {ai_karti.isim} (Puan: {b_guc})\n\nKARAR: {sonuc}")
        self.yeni_ozellik_sec();
        self.arayuzu_guncelle()

    def oyun_bitti_ekrani(self):
        o, b = self.oyun.oyuncu.skor, self.oyun.bilgisayar.skor;
        durum = f"🏆 {self.oyun.oyuncu.isim.upper()} ŞAMPİYON!" if o > b else "💀 AI KAZANDI!" if b > o else "🤝 BERABERE!"
        QMessageBox.information(self, "Sezon Bitti!",
                                f"{self.oyun.oyuncu.isim.upper()}: {o}\nAI Puanı: {b}\n\n{durum}");
        self.close()


class GirisEkrani(QMainWindow):
    def __init__(self, oyun_penceresi, bilgisayar_objesi, kullanici_objesi):
        super().__init__();
        self.oyun_penceresi = oyun_penceresi;
        self.bilgisayar = bilgisayar_objesi;
        self.kullanici = kullanici_objesi
        self.setWindowTitle("Sporcu Kart Oyunu");
        self.setGeometry(100, 100, 1000, 750)

        self.arka_plan_ayarla("arka_plan.png")

        merkez = QWidget(self);
        self.setCentralWidget(merkez);
        layout = QVBoxLayout(merkez);
        layout.addStretch()
        layout.addWidget(QLabel(
            "<center><h1 style='color:white; font-size:48px;'>SPORCU</h1><h1 style='color:#4CAF50; font-size:40px;'>KART <span style='color:#FF9800;'>OYUNU</span></h1></center>"))
        input_container = QFrame();
        input_container.setStyleSheet(
            "background-color: rgba(26, 30, 38, 200); border-radius: 15px; border: 1px solid #333;")
        input_layout = QVBoxLayout(input_container);
        input_layout.setContentsMargins(30, 30, 30, 30)
        input_layout.addWidget(
            QLabel("<center><h3 style='color:white;'>OYUNCU ADI</h3></center>", styleSheet="border:none;"))
        self.name_input = QLineEdit();
        self.name_input.setPlaceholderText("İsminizi yazın...");
        self.name_input.setFixedSize(300, 40)
        self.name_input.setStyleSheet(
            "background-color: #0c0e12; color: white; border: 1px solid #555; padding: 5px; font-size: 14px;")
        input_layout.addWidget(self.name_input, alignment=Qt.AlignCenter);
        input_layout.addSpacing(20)
        input_layout.addWidget(
            QLabel("<center><h3 style='color:white;'>ZORLUK SEVİYESİ</h3></center>", styleSheet="border:none;"))
        btn_layout = QHBoxLayout()
        self.btn_kolay = QPushButton("KOLAY");
        self.btn_kolay.setFixedSize(140, 60);
        self.btn_kolay.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 10px; border:none;");
        self.btn_kolay.clicked.connect(lambda: self.oyuna_basla(KolayStrateji()))
        self.btn_orta = QPushButton("ORTA");
        self.btn_orta.setFixedSize(140, 60);
        self.btn_orta.setStyleSheet("background-color: #FF9800; color: white; border-radius: 10px; border:none;");
        self.btn_orta.clicked.connect(lambda: self.oyuna_basla(OrtaStrateji()))
        btn_layout.addWidget(self.btn_kolay);
        btn_layout.addWidget(self.btn_orta);
        input_layout.addLayout(btn_layout)
        layout.addWidget(input_container, alignment=Qt.AlignCenter);
        layout.addStretch()

    def arka_plan_ayarla(self, image_path):
        if os.path.exists(image_path):
            self.setAutoFillBackground(True)
            palette = self.palette()
            pixmap = QPixmap(image_path).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)
        else:
            self.setStyleSheet("background-color: #0c0e12;")

    def oyuna_basla(self, strateji):
        isim = self.name_input.text().strip()
        if not isim: QMessageBox.warning(self, "Hata", "Lütfen bir oyuncu adı giriniz!"); return
        self.kullanici.isim = isim;
        self.bilgisayar.strateji_belirle(strateji);
        self.oyun_penceresi.arayuzu_guncelle();
        self.hide();
        self.oyun_penceresi.show()

    def resizeEvent(self, event):
        self.arka_plan_ayarla("arka_plan.png")
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        tum_kartlar = VeriOkuyucu.dosya_oku("sporcular.txt")
        if len(tum_kartlar) >= 24:
            o_obj = Kullanici(1, "");
            b_obj = Bilgisayar(2, "AI");
            oyun = OyunYonetici(o_obj, b_obj)
            if oyun.kartlari_dagit(tum_kartlar):
                pencere = AnaPencere(oyun);
                giris = GirisEkrani(pencere, b_obj, o_obj);
                giris.show();
                sys.exit(app.exec_())
        else:
            QMessageBox.critical(None, "Hata",
                                 "sporcular.txt dosyasında her branştan en az 8, toplam 24 kart olmalıdır.")
    except Exception as e:
        QMessageBox.critical(None, "Dosya Hatası", str(e))