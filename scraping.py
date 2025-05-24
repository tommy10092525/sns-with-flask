from datetime import datetime
from bs4 import BeautifulSoup
import requests
from app import Class, db
from app import app
from urllib import parse


def get_class_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    department = soup.select("tr")[0].select("span.jp")[1].text.strip()
    year = soup.select("tr")[2].select("td")[1].text.strip()
    code = soup.select("tr")[3].select("td")[1].text.strip()
    # htmlから科目名だけ位置を特定して無理やり取り出す
    name = str(soup.select("h1")[0])
    name = name[name.find("</div>")+8:name.find("／")]
    teacher = soup.select("h2")[0].text.strip()
    teacher = teacher[:teacher.find("（")]
    season = soup.select("tr")[6].select("td")[1].text.strip()
    time = soup.select("tr")[7].select("td")[1].text.strip()
    time = time[:time.find("/")]
    place = soup.select("tr")[10].select("td")[1].text.strip()
    unit = soup.select("tr")[12].select("td")[1].text.strip()
    restriction = soup.select("tr")[13].select("td")[1].text.strip()
    grading_criteria = soup.select("div.subjectContents>span>span.jp>p")[
        11].text.strip()
    grading_criteria = grading_criteria[len(
        r"【成績評価の方法と基準 / Grading criteria】\r\n")-2:]

    _class = Class(department=department, year=year, code=code, name=name, season=season, time=time, place=place,
                   url=url, teacher=teacher, unit=unit, restriction=restriction, grading_criteria=grading_criteria)
    print(_class.to_dict())
    # db.session.add(_class)
    # db.session.commit()

def get_class_list(department,page):
    url=r"https://syllabus.hosei.ac.jp/web/web_search_show.php?search=show&nendo=2025&gakubu="+parse.quote(department)+"&page="+str(page)
    print(url)
    response=requests.get(url)
    soup=BeautifulSoup(response.text,"html.parser")
    rows=soup.select("table>tr.jp")
    class_list=[]
    for row in rows:
        try:
            url="https://syllabus.hosei.ac.jp/web/"+row.attrs["data-href"]
        except:
            url="urlなし"
        class_list.append(url)
    return class_list

DEPARTMENTS = [
    "法学部",
    "文学部",
    "経済学部",
    "社会学部",
    "経営学部",
    "国際文化学部",
    "人間環境学部",
    "現代福祉学部",
    "情報科学部",
    "キャリアデザイン学部",
    "理工学部",
    "生命科学部",
    "グローバル教養学部",
    "スポーツ健康学部"]

print(get_class_list(DEPARTMENTS[-1],1))
# with app.app_context():
#     db.create_all()
#     db.session.commit()

#     url = r"https://syllabus.hosei.ac.jp/web/web_search_show.php?search=show&nendo=2025&gakubu=%E7%B5%8C%E6%B8%88%E5%AD%A6%E9%83%A8"

#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     rows = soup.select("tr.jp")
#     for row in rows:
#         url = "https://syllabus.hosei.ac.jp/web/"+row.attrs["data-href"]
#         get_class_info(url)
