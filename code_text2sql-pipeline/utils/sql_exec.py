import os
import sqlite3

root_path = os.path.dirname(os.path.dirname(__file__))
DATABASE_PATH=os.path.join(root_path, 'utils/database-spider/database-dev')


def query_db(db_name,cmd='SELECT',db_path=DATABASE_PATH):
    path_db=os.path.join(os.path.join(db_path,db_name),f"{db_name}.sqlite")
    # 连接到数据库文件
    conn = sqlite3.connect(path_db)
    # conn.text_factory = bytes
    # 创建游标对象
    cursor = conn.cursor()

    try:
        # 执行SQL查询或其他操作
        cursor.execute(cmd)
        results = ['success',cursor.fetchall()]
    except Exception as e:
        results=['fail',[str(e)]]

    conn.close()
    return results


if __name__=='__main__':
    print(query_db('activity_1',"SELECT seX from StudenT Where sex='F'"))