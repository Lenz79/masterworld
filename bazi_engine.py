import json
from lunar_python import Solar, Lunar
from supabase import create_client, Client

# 1. Supabase 配置
URL: str = "https://qistykwqmwtacknrhifq.supabase.co"
KEY: str = "sb_publishable_gL3EJrq87UcGb-RFMgF1hg_4x-H3rif" # 请填入您的真实 key

supabase: Client = create_client(URL, KEY)

# 天干五行对应表
GAN_ELEMENTS = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}
ZHI_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

def calculate_real_bazi(name: str, gender: str, year: int, month: int, day: int, hour: int):
    solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
    lunar = solar.getLunar()
    eight_char = lunar.getEightChar()

    is_male = 1 if gender == "男" else 0
    eight_char.setSect(1)
    
    bazi_chart = {
        "year_pillar": {
            "gan": eight_char.getYearGan(),
            "zhi": eight_char.getYearZhi(),
            "shishen": eight_char.getYearShiShenGan(),
            "cangan": list(eight_char.getYearHideGan())
        },
        "month_pillar": {
            "gan": eight_char.getMonthGan(),
            "zhi": eight_char.getMonthZhi(),
            "shishen": eight_char.getMonthShiShenGan(),
            "cangan": list(eight_char.getMonthHideGan())
        },
        "day_pillar": {
            "gan": eight_char.getDayGan(),
            "zhi": eight_char.getDayZhi(),
            "shishen": "日主",
            "cangan": list(eight_char.getDayHideGan())
        },
        "hour_pillar": {
            "gan": eight_char.getTimeGan(),
            "zhi": eight_char.getTimeZhi(),
            "shishen": eight_char.getTimeShiShenGan(),
            "cangan": list(eight_char.getTimeHideGan())
        }
    }

    elements_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    all_gans = [eight_char.getYearGan(), eight_char.getMonthGan(), eight_char.getDayGan(), eight_char.getTimeGan()]
    all_zhis = [eight_char.getYearZhi(), eight_char.getMonthZhi(), eight_char.getDayZhi(), eight_char.getTimeZhi()]
    
    for g in all_gans:
        elements_count[GAN_ELEMENTS.get(g, "土")] += 1.5
    for z in all_zhis:
        elements_count[ZHI_ELEMENTS.get(z, "土")] += 1.0

    total_score = sum(elements_count.values())
    five_elements = {k: round((v / total_score) * 100) for k, v in elements_count.items()}

    yun = eight_char.getYun(is_male)
    da_yun_list = yun.getDaYun()
    
    dayun_schedule = []
    for dy in da_yun_list[:6]:
        if dy.getIndex() == 0:
            continue
        dayun_schedule.append({
            "age": dy.getStartAge() if hasattr(dy, 'getStartAge') else dy.getAge(),
            "start_year": dy.getStartYear(),
            "gan_zhi": dy.getGanZhi()
        })

    day_gan = eight_char.getDayGan()
    year_gz = f"{eight_char.getYearGan()}{eight_char.getYearZhi()}"
    month_gz = f"{eight_char.getMonthGan()}{eight_char.getMonthZhi()}"
    day_gz = f"{eight_char.getDayGan()}{eight_char.getDayZhi()}"
    hour_gz = f"{eight_char.getTimeGan()}{eight_char.getTimeZhi()}"

    start_year = yun.getStartYear()

    ai_report = (
        f"【大师级真实八字分析报告 - {name}】\n"
        f"命主公历生于 {year}年{month}月{day}日 {hour}时。\n"
        f"八字四柱为：{year_gz}年  {month_gz}月  {day_gz}日  {hour_gz}时。\n"
        f"日主为【{day_gan}】，生于{eight_char.getMonthZhi()}月。\n"
        f"起运年份：大约 {start_year} 年起交大运。\n"
        f"局中五行分布：金{five_elements['金']}%、木{five_elements['木']}%、水{five_elements['水']}%、火{five_elements['火']}%、土{five_elements['土']}%。"
    )

    return bazi_chart, five_elements, dayun_schedule, ai_report

def run_test():
    name = "小叶"
    gender = "男"
    year, month, day, hour = 1979, 3, 20, 10

    print(f"🔮 正在使用真实天文历法计算 {name} ({year}-{month}-{day} {hour}:00) 的真实八字...")
    chart, elements, dayun, report = calculate_real_bazi(name, gender, year, month, day, hour)

    record = {
        "user_name": name,
        "gender": gender,
        "birth_year": year,
        "birth_month": month,
        "birth_day": day,
        "birth_hour": hour,
        "bazi_chart": chart,
        "five_elements": elements,
        "dayun_list": dayun,
        "ai_report": report
    }

    response = supabase.table("bazi_records").insert(record).execute()
    if response.data:
        print("✅ 计算成功！真实的己未年八字数据已成功写入 Supabase 云端！")

if __name__ == "__main__":
    run_test()