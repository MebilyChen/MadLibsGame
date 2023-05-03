# MadLibs小程序@2022
# MadLibs.py
# pyinstaller -F main.py

import os
import sys
import re
import pymysql
import random
import string
import cryptography

# 默认连接参数
host = "10.181.89.186"
port = 3306
user = 'root'
password = '690619'
database = 'db'
charset = 'utf8mb4'

userwordcount = 0
similar = [' ', ' ']
face = ["(*=▽=*)", "(*I▽I*)", "(oωo)", "(=w=)", "(0w0)", "(0v0)"]


def save():
    filename = input("请输入文件名(无后缀):")
    filename = filename + ".txt"
    print("正在连接到数据库...")
    try:
        cursor.execute("SELECT VERSION()")
        # 获取单条数据
        one = cursor.fetchone()
        print("DB version is: %s" % one)
    except Exception as e:
        print("无法连接数据库：")
        print(e)
    sql = '''SELECT * FROM ML_LIST'''
    try:
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        # 清空文件
        f = open(filename, "w")
        f.close()
        for row in results:
            ml_id = row[0]
            title = row[1]
            txt = row[2]
            # 将换行改成\n
            txt2 = ''
            for a in txt:
                if a == '\n':
                    txt2 = txt2 + "\\n"
                else:
                    txt2 = txt2 + a
            print("正在导出第", ml_id, "条...")
            with open(filename, "a") as f:
                f.write("#%d" % ml_id)
                f.write("\n")
                f.write("《%s》" % title)
                f.write("\n")
                f.write(txt2)
                f.write("\n")
    except Exception as e:
        print("导出失败：")
        print(e)
    print("导出成功！请查看同目录下的%s文件。" % filename)


def loadone(f, flag):
    flag = 0
    l1 = f.readline()
    l1 = l1.strip('\n')
    if l1 != "":
        flag = flag + 1
    l2 = f.readline()
    l2 = l2.strip('\n')
    if l2 != "":
        flag = flag + 1
    l3 = f.readline()
    l3 = l3.strip('\n')
    if l3 != "":
        flag = flag + 1
    return l1, l2, l3, flag


def load():
    filename = input("请输入文件名(无后缀):")
    if not os.path.exists("%s.txt" % filename):
        print("文件不存在，请确认是否在同一目录。")
        load()
    try:
        filename = filename + ".txt"
        print("正在连接到数据库...")
        flag2 = 3
        with open(filename, 'r', encoding='gbk') as f:
            while flag2 == 3:
                l1, l2, l3, flag2 = loadone(f, flag2)
                l2 = l2.replace("《", "")
                l2 = l2.replace("》", "")
                if l1 == "" or l2 == "" or l3 == "":
                    break
                try:
                    print("正在录入第", l1, "条记录...")
                    cursor.execute("INSERT INTO ML_LIST(TITLE, CONTENT) VALUES ('%s', '%s')" % (l2, l3))
                    db.commit()
                    flag = 1
                except Exception as e:
                    flag = 0
                    db.rollback()
                    print("错误:\n", e)
                if flag == 1:
                    print("录入成功！")
                else:
                    print("上传失败,操作已回滚。")
        if flag2 != 0:
            print("数据条数不匹配，缺少%d行数据，请检查%s的条目完整性" % (3 - flag2, filename))
            db.rollback()
        main()
    except Exception as e:
        print("错误:\n", e)
        print("请检查文本编码格式是否为ANSI")


def inisimi():
    global similar
    similar = [' ', ' ']


# 查询列表
def ml_list():
    try:
        # 查询
        sql = '''SELECT * FROM ML_LIST'''
        try:
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            for row in results:
                ml_id = row[0]
                title = row[1]
                txt = row[2]
                wordcount = txt.count('【')
                print("=========")
                print("[%d]《%s》 填空数:%d" % (ml_id, title, wordcount))
            print("=========")
        except Exception as e:
            print("查询失败：")
            print(e)

    except Exception as e:
        print("无法连接数据库：")
        print(e)

    # 关闭数据库
    # db.close()
    more()


# 查询列表详细
def more():
    index = int(input("请输入对应序号查询某条记录的详细内容，输入[0]返回主界面："))
    while index is not None:
        if index > 0:
            try:
                cursor.execute("SELECT * FROM ML_LIST WHERE ID = '%d'" % index)
                # 获取单条数据
                one = cursor.fetchone()
                ml_id = one[0]
                title = one[1]
                txt = one[2]
                wordcount = txt.count('【')
                print("=========")
                print("[%d]《%s》 填空数:%d" % (ml_id, title, wordcount))
                print(txt)
                print("=========")
            except Exception as e:
                print("查询失败：")
                print(e)
            index = int(input("请输入对应序号查询某条记录的详细内容，输入[0]返回主界面："))
        else:
            # 关闭数据库
            # db.close()
            main()


# 增加条目
def add():
    print("正在连接到数据库...")
    try:
        cursor.execute("SELECT VERSION()")
        # 获取单条数据
        one = cursor.fetchone()
        print("DB version is: %s" % one)
    except Exception as e:
        print("无法连接数据库：")
        print(e)

    print("快速自制填字单的方法：截取一段文艺作品梗概 / 情节描述。将其中的部分词替换，但保留完整的整体框架")
    print("录入：按格式录入Mad Lib，使用[列表]查看Mad Lib列表，查看录入格式输入[格式]")
    a = input("请输入[录入]，[列表]或[格式]，输入[返回]返回主界面：")
    while a is not None:
        if a == "录入":
            title = input("请输入标题（可省略）：")
            text = input("请输入内容：")
            a = input("确定上传?(y/n)：")
            while a is not None:
                if a == "y":
                    print("录入中...")

                    # 如果表User存在则删除
                    # cursor.execute("DROP TABLE IF EXISTS USER")

                    # 创建表List
                    # cursor.execute("CREATE TABLE ML_LIST(ID INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT'主键',
                    # TITLE VARCHAR(255) DEFAULT NULL COMMENT'标题',
                    # CONTENT TEXT DEFAULT NULL COMMENT'内容')) ENGINE = INNODB CHARSET = UTF8MB4")
                    # ！！！TEXT数据类型在Python中没有对应？会报错。！！！--已解决，使用%s % (title)的方式，见下。

                    # 插入
                    try:
                        cursor.execute("INSERT INTO ML_LIST(TITLE, CONTENT) VALUES ('%s', '%s')" % (title, text))
                        db.commit()
                        flag = 1
                    except Exception as e:
                        flag = 0
                        db.rollback()
                        print("错误:\n", e)
                    if flag == 1:
                        print("录入成功！")
                        print("标题：", title)
                        print(text)
                        add()
                    else:
                        print("上传失败,操作已回滚。")
                else:
                    title = input("请重新输入标题（可省略）,输入[返回]返回上一级：")
                    if title == '返回':
                        add()
                    text = input("请重新输入内容：")
                    a = input("确定上传?(y/n)：")
        if a == "格式":
            print(
                "格式参考：\n 这是一段格式参考文档，【你的姓名#1】可以参考这段文字进行Mad Lib的【一个动词】。\n【#1】需要了解，当【任意词汇】需要重复出现的时候，需要在其后加上井字符和序号，就像【任意词汇#2】，这样【#1】的【你的玩家】就无需再次输入【#2】了。\n如【#1】需要换行，请输入\\n。")
        if a == "返回":
            main()
        if a == "列表":
            ml_list()
        else:
            a = input("请输入[录入]，[列表]或[格式]，输入[返回]返回主界面：")


# 读取条目
def play():
    print("正在连接到数据库...")
    try:
        cursor.execute("SELECT VERSION()")
        # 获取单条数据
        one = cursor.fetchone()
        print("DB version is: %s" % one)
    except Exception as e:
        print("无法连接数据库：")
        print(e)

    a = input("游玩：使用[选择]在列表中选择一个Mad Lib，或输入[随机]开始游戏，输入[返回]返回主界面：")
    while a is not None:
        if a == "选择":
            choose()
        if a == "随机":
            random_ml()
        if a == "返回":
            main()
        else:
            a = input("游玩：使用[选择]在列表中选择一个Mad Lib，或输入[随机]开始游戏，输入[返回]返回主界面：")


def choose():
    txt = "text"
    sql = '''SELECT * FROM ML_LIST'''
    try:
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            ml_id = row[0]
            title = row[1]
            txt = row[2]
            wordcount = txt.count('【')
            print("=========")
            print("[%d]《%s》 填空数:%d" % (ml_id, title, wordcount))
        print("=========")
    except Exception as e:
        print("查询失败：")
        print(e)
    a = int(input("输入序号进行选择，输入[0]返回主界面："))
    if a > 0:
        index = a
        readgame(index)
    else:
        main()


def random_ml():
    sql = '''SELECT count(*) FROM ML_LIST'''
    try:
        cursor.execute(sql)
        # 获取列表所有记录的数量
        count = cursor.fetchone()
        randomi = count[0]
        # ！！！返回的不是int，是元组！！！--已解决，使用cursor[0]获取
        randomi = random.randint(1, randomi)
        cursor.execute("SELECT * FROM ML_LIST WHERE ID = '%d'" % randomi)
        results = cursor.fetchone()
        check = results[2]
        while check is None:
            randomi = random.randint(1, randomi)
            cursor.execute("SELECT * FROM ML_LIST WHERE ID = '%d'" % randomi)
            results = cursor.fetchone()
            check = results[2]
        readgame(randomi)
    except Exception as e:
        print("查询失败：")
        print(e)


def readgame(index):
    global userwordcount
    randomi = random.randint(0, 5)
    if randomi >= 1:
        inisimi()
    notitle = 0
    print("正在读取游戏", index, "号...")
    cursor.execute("SELECT * FROM ML_LIST WHERE ID = '%d'" % index)
    results = cursor.fetchone()
    title = results[1]
    txt = results[2]
    wordcount = txt.count('【') - txt.count('#') + 3
    print("待填空数:", wordcount)
    a = input("是否显示标题？（y/n）:")
    if a == 'y':
        print("《%s》" % title)
        notitle = 1
    answer = ''
    answertmp = ''
    question = ''
    # 字符串逐行扫描
    nPos = 0
    waittime = 0
    for wordi in txt:
        if wordi == "【":
            # 在大于等于nPos的位置寻找字符wordi
            nPos = txt.index(wordi, nPos)
            mPos = nPos
            wordi = txt[nPos + 1]
            userwordcount = userwordcount + 1
            while wordi != "】":
                if wordi != "】":
                    wordi = txt[nPos]
                    question = question + wordi
                nPos = nPos + 1
            # 函数可以多输入/多输出
            # wordcounttmp, answertmp = readword(userwordcount, question)
            answertmp = readword(question)
            question = ""
            waittime = nPos - mPos
            if is_chinese(wordi):
                answertmp = answertmp + ''
            else:
                answertmp = answertmp + ' '
            answer = answer + answertmp
            continue
        else:
            if waittime > 1:
                waittime = waittime - 1
                continue
            answer = answer + wordi
    print("=========")
    if notitle == 1:
        print("《%s》" % title)
    print(answer)
    print("=========")
    play()


def readword(word):
    global userwordcount
    global similar
    word = word
    if '#' in word:
        wordspli = word.split('#')
        simindex = int(wordspli[1].rstrip('】'))
        similar.append(' ')
        if similar[simindex] == ' ':
            a = input("请输入【%s】：" % wordspli[0].lstrip('【'))
            similar.insert(simindex, a)
        else:
            userwordcount = userwordcount - 1
            return similar[simindex]
    else:
        a = input("请输入%s：" % word)
    # ！！！判空并没有用！！！
    if a is not None:
        return a
    else:
        while a is None:
            a = input("输入不能为空，请输入%s：" % word)
        return a


def is_chinese(word):
    ch = ord(word)
    # ch <= 127 and ch >= 0简化：
    if 0 <= ch <= 127:
        return False
    else:
        return True


def login():
    global user
    global password
    global db
    global cursor
    user = input("输入用户名(默认root):")
    password = input("输入密码:")
    flag = input("是否启动自动重连(10次):(y/n)")
# 重连机制
    if flag != "n":
        retry_count = 10
        init_connect_count = 0
        connect_res = True
        while connect_res and init_connect_count < retry_count:
            try:
                db = pymysql.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    charset=charset
                )
                cursor = db.cursor()
                # 连接上退出循环，连接不上继续重连
                connect_res = False
            except pymysql.Error as e:
                print("数据库连接失败，尝试重连...，错误信息：{0}".format(e))
                init_connect_count += 1
                login()
    else:
        try:
            print("数据库连接中...")
            db = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset=charset
            )
            cursor = db.cursor()
        except Exception as e:
            print("数据库连接失败，请重新输入参数！")
            print(e)
            login()


# 主程序
def main():
    print("Welcome, %s!" % user)
    if userwordcount > 0:
        print("%s你本次游玩已输入%d词" % (face[random.randint(0, 5)], userwordcount))
    print("录入：录入单条Mad Lib")
    print("游玩：游玩Mad Lib")
    print("导出：导出数据库中的Mad Libs为文件")
    print("读取：读取Mad Libs文件并添加到数据库")

    a = input("请输入[列表]，[录入]，[游玩]或其他命令开始使用本程序，输入[退出]退出程序：")
    while a is not None:
        if a == "列表":
            ml_list()
        if a == "录入":
            add()
        if a == "游玩":
            play()
        if a == "导出":
            save()
        if a == "读取":
            load()
        if a == "退出":
            exit()
        else:
            a = input("请输入[列表]，[录入]，[游玩]或其他命令开始使用本程序，输入[退出]退出程序：")


cur = input("是否需要设置连接参数(y/n)：")
if cur == 'y':
    user = input("输入用户名:")
    password = input("输入密码:")
try:
    print("数据库连接中...")
    db = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset=charset
    )
    cursor = db.cursor()
except Exception as e:
    print("数据库连接失败，请重新输入参数！")
    print(e)
    login()
main()
