#!/usr/bin/env python

import os
import sys

def setup_database():
    # 先清理任何 alembic 相关的文件
    if os.path.exists('alembic'):
        import shutil
        shutil.rmtree('alembic')

    if os.path.exists('alembic.ini'):
        os.remove('alembic.ini')

    # 如果存在旧的数据库文件，则删除
    if os.path.exists('sql_app.db'):
        os.remove('sql_app.db')

    # 导入数据库模块并创建表
    try:
        print("正在创建数据库和表结构...")
        from app.database import create_db_and_tables
        create_db_and_tables()
        print("数据库和表结构创建成功!")
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        return False

    return True

if __name__ == "__main__":
    if setup_database():
        print("\n设置完成! 现在可以运行应用:")
        print("python main.py")
    else:
        print("\n设置失败，请检查错误信息")
        sys.exit(1)
