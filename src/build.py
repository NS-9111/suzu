import json, pathlib, shutil
SHOP="https://suzuri.jp/Sue-san"
IMG="https://lens.suzuri.jp/v3/400x400/can-badge/75mm/white/front/{id}/{v}.png.png?h={h}&printed=true"
designs = {
 "kitsune": dict(id=21385942, v="1794813922-4000x4000", h="5efb16b817048d7f8e4e6cb854bf42f5bc3bea20",
   ja="稲荷狐", en="Inari Kitsune",
   mja="稲荷の神さまのお使いとされる狐。商売繁盛の願いと結びつけられてきました。",
   men="Messenger of Inari, the deity long associated with prosperity in business."),
 "shishi": dict(id=21384054, v="1794799838-4000x4000", h="2e39aa58db8f1af0a38283c29a2ca3bb8b6469c3",
   ja="獅子舞", en="Shishimai",
   mja="獅子舞の獅子に頭をかんでもらうと、厄が払われると言われています。",
   men="A bite from the shishi lion dancer is said to ward off bad luck."),
 "sensu": dict(id=21333568, v="1794217768-4000x4000", h="c33400e1bab6e668874783aa7823a3990c8f8683",
   ja="末広扇", en="Suehiro Sensu",
   mja="開くと末広がりになる形から、繁栄の縁起物とされています。",
   men="Its shape widens as it opens, so the fan is a symbol of growing prosperity."),
 "kingyo": dict(id=21319983, v="1794049705-2958x3000", h="ffcfba2ce3d2be1b97e40a05671f1a0fd36f9bdc",
   ja="青海波金魚", en="Seigaiha Kingyo",
   mja="金運に通じる縁起物とも言われています。",
   men="Goldfish are said to bring good fortune."),
 "taka": dict(id=21393955, v="1794888524-4000x4000", h="53e29738f2380cb747763ff932920e58acde9601",
   ja="初夢鷹", en="Hatsuyume Taka",
   mja="初夢に見ると縁起がいいとされる「一富士二鷹三茄子」の鷹。",
   men="In Japan, a hawk is one of the luckiest sights in the first dream of the year."),
 "daruma": dict(id=21317937, v="1794031120-2829x3000", h="b2c39352714f30b535e73b545cbce1a8765e3c29",
   ja="願掛けだるま", en="Gankake Daruma",
   mja="七転び八起き。願いを込めて片目を入れ、叶ったらもう片方を入れる風習があります。",
   men="Fall seven times, rise eight. One eye is painted when you make a wish, the other when it comes true."),
 "tengu": dict(id=21411948, v="1795069891-4000x4000", h="110b7b5441c7af9f014b27194bf4b16d1b12498f",
   ja="もみじ天狗", en="Momiji Tengu",
   mja="山の守り神として祀られる土地もある天狗。魔除けの縁起物とも言われます。",
   men="Tengu, mountain spirits in Japanese folklore, are sometimes seen as charms against evil."),
 "kame": dict(id=21412556, v="1795074816-4000x4000", h="fe7b0b1f2a430ecc4d5e04be5733604329918998",
   ja="万年亀", en="Mannen Kame",
   mja="「鶴は千年、亀は万年」と言われる、長寿の縁起物です。",
   men='"Cranes live a thousand years, turtles ten thousand" — a classic symbol of long life.'),
 "usagi": dict(id=21412580, v="1795075160-4000x4000", h="2ea78f39e6b47911c57358157013dc7c7e3ae77f",
   ja="からくり兎", en="Karakuri Usagi",
   mja="『古事記』の因幡の白兎は、大国主神と八上姫の縁を結んだとされ、縁結びの縁起物とされます。跳ねる姿から「飛躍」の象徴とも言われます。",
   men="In Japanese myth, the White Hare of Inaba brought two deities together, so rabbits are seen as charms for good relationships — and their leaps as a sign of progress."),
}
# 入口：1〜3点まで
sections = [
 dict(key="wish", ja="願いで選ぶ", en="Choose by wish", groups=[
   dict(ja="商売繁盛・金運", en="Business & fortune", items=["kitsune","sensu","kingyo"]),
   dict(ja="厄除け", en="Warding off bad luck", items=["shishi","tengu"]),
   dict(ja="合格・必勝・出世", en="Success & advancement", items=["daruma","taka","usagi"]),
   dict(ja="健康・長寿", en="Health & longevity", items=["kame"]),
   dict(ja="縁結び", en="Good relationships", items=["usagi"]),
 ]),
 dict(key="gift", ja="贈る相手で選ぶ", en="Choose by occasion", groups=[
   dict(ja="開店・開業のお祝いに", en="Opening a shop or business", items=["kitsune","sensu"]),
   dict(ja="受験生へ", en="For students facing exams", items=["daruma","taka"]),
   dict(ja="お正月・新年に", en="New Year", items=["taka","shishi","daruma"]),
   dict(ja="長寿のお祝いに", en="For longevity celebrations", items=["kame"]),
 ]),
 dict(key="season", ja="季節で選ぶ", en="Choose by season", groups=[
   dict(ja="冬・お正月", en="Winter & New Year", items=["taka","shishi","daruma"]),
 ]),
]
for k,d in designs.items():
    d["img"]=IMG.format(**d); d["url"]=f"{SHOP}/designs/{d['id']}"
data=dict(shop=SHOP, designs=designs, sections=sections)
tpl=pathlib.Path(__file__).with_name("template.html").read_text()
html=tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False))
out=pathlib.Path(__file__).resolve().parent.parent
(out/"index.html").write_text(html)
for r in ["t","p","pe","y","tt"]:
    (out/r).mkdir(exist_ok=True); (out/r/"index.html").write_text(html)
print("ok")
