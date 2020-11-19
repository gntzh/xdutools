import re


URLS = {
    "kb": "http://ehall.xidian.edu.cn/jwapp/sys/wdkb/modules/xskcb/xsllsykb.do",
}
APP_NAME = "我的课表"


class Lesson:
    week = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日"}

    def __init__(self):
        pass

    def get_lessons(self, session):
        res = session.post(URLS["kb"], data={"XNXQDM": "2019-2020-2"})
        return [self.process_lesson(i) for i in res.json()["datas"]["xsllsykb"]["rows"]]

    def process_lesson(self, data):
        return {
            "课程": data["KCM"],
            "教师": (data["SKJS"] or "未指定").replace(",", " "),
            "周几": data["SKXQ"],
            "开始节数": data["KSJC"],
            "结束节数": data["JSJC"],
            "教室": data["JASMC"],
            "周数": self.process_week(data["ZCMC"]),
        }

    def process_week(self, week):
        rst = []
        for w in week.split(","):
            m = re.match(r"(\d+)-(\d+)周\([单双]\)$", w)
            if m:
                rst.extend(i for i in range(int(m.group(1)), int(m.group(2)) + 1, 2))
                continue
            m = re.match(r"(\d+)-(\d+)周$", w)
            if m:
                rst.extend(i for i in range(int(m.group(1)), int(m.group(2)) + 1))
            m = re.match(r"(\d+)周$", w)
            if m:
                rst.append(int(m.group(1)))
                continue
        return rst

    def save_lessons(self, lessons, format):
        getattr(self, "save_lessons_as_" + format)(lessons)

    def save_lessons_as_csv(self, lessons):
        with open("./schedule.csv", "w", encoding="utf-8") as fo:
            fo.write("课程,教师,周几,节数,教室,周数" + "\n")
            fo.writelines(
                ",".join(
                    (
                        i["课程"],
                        i["教师"],
                        self.week[i["周几"]],
                        "%d-%d" % (i["开始节数"], i["结束节数"]),
                        i["教室"] or "无",
                        " ".join(map(str, i["周数"])),
                    )
                )
                + "\n"
                for i in lessons
            )

    def save_lessons_as_simple(self, lessons):
        with open("./schedule-simple.txt", "w", encoding="utf-8") as fo:
            fo.writelines(
                "，".join(
                    (
                        i["课程"],
                        i["教师"],
                        self.week[i["周几"]],
                        "%d-%d" % (i["开始节数"], i["结束节数"]),
                        i["教室"] or "无",
                        " ".join(map(str, i["周数"])),
                    )
                )
                + "\n"
                for i in lessons
            )

    def save_lessons_as_wakeup(self, lessons):
        """保存为适合WakeUp课程表导入的格式(csv)
        课程名称,星期,开始节数,结束节数,老师,地点,周数
        """
        with open("./schedule-wakeup.csv", "w", encoding="utf-8") as fo:
            fo.write("课程名称,星期,开始节数,结束节数,老师,地点,周数" + "\n")
            fo.writelines(
                ",".join(
                    (
                        i["课程"],
                        str(i["周几"]),
                        str(i["开始节数"]),
                        str(i["结束节数"]),
                        i["教师"],
                        i["教室"] or "无",
                        "、".join(map(str, i["周数"])),
                    )
                )
                + "\n"
                for i in lessons
            )
