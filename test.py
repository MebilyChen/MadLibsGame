import pymysql


def main():
    print("正在连接到数据库...")
    db = pymysql.connect(
        host="localhost",
        port=3306,
        user='root',
        password='690619',
        database='db',
        charset='utf8mb4'
    )
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF ")
    sql = "show database"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            title = row[0]
            txt = row[1]
            ml_id = row[2]
            print("===")
            print("[%s]Title:%s" % (title, ml_id))
            print(txt)
            print("===")
    except Exception as e:
        print("查询失败。")
        print(e)

main()