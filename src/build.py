import json, pathlib, shutil
SHOP="https://suzuri.jp/Sue-san"
IMG="https://lens.suzuri.jp/v3/400x400/can-badge/75mm/white/front/{id}/{v}.png.png?h={h}&printed=true"
designs = {
 "kitsune": dict(id=21385942, v="1794813922-4000x4000", h="5efb16b817048d7f8e4e6cb854bf42f5bc3bea20",
   ja="モダン狐", en="Modern Kitsune",
   mja="稲荷の神さまのお使いとされる狐。商売繁盛の願いと結びつけられてきました。",
   men="Messenger of Inari, the deity long associated with prosperity in business."),
 "shishi": dict(id=21384054, v="1794799838-4000x4000", h="2e39aa58db8f1af0a38283c29a2ca3bb8b6469c3",
   ja="モダン獅子", en="Modern Shishi",
   mja="獅子舞の獅子に頭をかんでもらうと、厄が払われると言われています。",
   men="A bite from the shishi lion dancer is said to ward off bad luck."),
 "sensu": dict(id=21333568, v="1794217768-4000x4000", h="c33400e1bab6e668874783aa7823a3990c8f8683",
   ja="モダン扇子", en="Modern Sensu",
   mja="開くと末広がりになる形から、繁栄の縁起物とされています。",
   men="Its shape widens as it opens, so the fan is a symbol of growing prosperity."),
 "kingyo": dict(id=21319983, v="1794049705-2958x3000", h="ffcfba2ce3d2be1b97e40a05671f1a0fd36f9bdc",
   ja="モダン金魚", en="Modern Kingyo",
   mja="「金」の字を持つことから、金運の縁起物とされることもあります。",
   men="With 'gold' in its name, the goldfish is sometimes seen as a charm for wealth."),
 "taka": dict(id=21393955, v="1794888524-4000x4000", h="53e29738f2380cb747763ff932920e58acde9601",
   ja="モダン鷹", en="Modern Taka",
   mja="初夢に見ると縁起がいい「一富士二鷹」の鷹。高く飛ぶ姿から、出世の縁起物ともされます。",
   men="The hawk of 'Ichi-Fuji, Ni-Taka', the luckiest first dreams of the year; its high flight is linked to success."),
 "daruma": dict(id=21317937, v="1794031120-2829x3000", h="b2c39352714f30b535e73b545cbce1a8765e3c29",
   ja="モダンだるま", en="Modern Daruma",
   mja="七転び八起き。願いを込めて片目を入れ、叶ったらもう片方を入れる風習があります。",
   men="Fall seven times, rise eight. One eye is painted when you make a wish, the other when it comes true."),
}
# 入口：1〜3点まで
sections = [
 dict(key="wish", ja="願いで選ぶ", en="Choose by wish", groups=[
   dict(ja="商売繁盛・金運", en="Business & fortune", items=["kitsune","sensu","kingyo"]),
   dict(ja="厄除け", en="Warding off bad luck", items=["shishi"]),
   dict(ja="合格・必勝・出世", en="Success & advancement", items=["daruma","taka"]),
 ]),
 dict(key="gift", ja="贈る相手で選ぶ", en="Choose by occasion", groups=[
   dict(ja="開店・開業のお祝いに", en="Opening a shop or business", items=["kitsune","sensu"]),
   dict(ja="受験生へ", en="For students facing exams", items=["daruma","taka"]),
   dict(ja="お正月・新年に", en="New Year", items=["taka","shishi","daruma"]),
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
