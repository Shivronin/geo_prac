import os
from dotenv import load_dotenv

load_dotenv()

import mariadb

import asyncio
import aiomysql

from typing import List, Tuple

try:
    connection = mariadb.connect(
        host=os.getenv('MARIADB_HOST', '127.0.0.1'),
        user=os.getenv('MARIADB_USER', 'root'),
        password=os.getenv('MARIADB_PASSWORD', 'dbm'),
        port=int(os.getenv('MARIADB_PORT', '3306'))
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    exit(1)

try:
    query = connection.cursor()

    # Создаем базу данных, если она не существует
    query.execute("CREATE DATABASE IF NOT EXISTS dbm")

    # Выбираем созданную базу данных
    query.execute("USE dbm")
    
    # query.execute("DROP TABLE IF EXISTS geo_table")  # Это тут временно

    # Проверяем, существует ли таблица geo_table
    query.execute("CREATE TABLE IF NOT EXISTS geo_table (id INT AUTO_INCREMENT PRIMARY KEY, parent_id INT, title VARCHAR(255) NOT NULL, FOREIGN KEY (parent_id) REFERENCES geo_table (id) ON DELETE CASCADE)")
    print("Таблица geo_table успешно создана в базе данных dbm")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")

class NodeNotExistsException(Exception):
    def __init__(self, title: str):
        self.message = "Node with id = {0} is not exists".format(title)
        super().__init__(self.message)

def read(title: str) -> List[Tuple[int, int, str]]:
    try:
        query = connection.cursor()
        query.execute(
            "SELECT id, parent_id, title FROM geo_table WHERE title = %s", (title,)
        )
        all = query.fetchall()
        if not all:
            raise NodeNotExistsException(title)
        query.close()
        return all

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")
        
def read_childs(title: str, parent_id: int) -> Tuple[int, int, str]:
    try:
        query = connection.cursor()
        query.execute(
            "SELECT * FROM geo_table WHERE title = %s AND parent_id = %s", (title, parent_id)
        )
        this = query.fetchone()
        if not this:
            raise NodeNotExistsException(title)
        query.close()
        return this

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def create(title: str, parent_id: int) -> int:
    try:
        query = connection.cursor()
        query.execute(
            "SELECT id FROM geo_table WHERE id = %s", (parent_id,)
        )
        que_res = query.fetchall()
        query.execute(
            "SELECT id FROM geo_table ORDER BY id DESC LIMIT 1"
        )
        max_id_node = query.fetchone()
        if not max_id_node:
            max_id_node = [0]
        if len(que_res) == 0:
            que_res = [max_id_node[0] + 1]
        else:
            que_res = que_res[0]
        query.execute(
            "INSERT INTO geo_table (id, parent_id, title) VALUES (%s, %s, %s)",
            (max_id_node[0] + 1, que_res[0], title),
        )
        connection.commit()
        query.execute("SELECT id FROM geo_table ORDER BY id DESC")
        id = query.fetchone()
        query.close()
        return id[0]

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def add_node(connection, parent_id: int, title: str) -> int:
    try:
        query = connection.cursor()
        query.execute("SELECT id FROM geo_table ORDER BY id DESC LIMIT 1")
        max_id = query.fetchone()
        query.execute("INSERT INTO geo_table (id, parent_id, title) VALUES (%s, %s, %s)", (max_id[0] + 1, parent_id, title))
        connection.commit()
        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def update(connection, id: int, title: str) -> int:
    try:
        query = connection.cursor()
        query.execute("UPDATE geo_table SET title = %s WHERE id = %s", (title, id))
        connection.commit()
        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")


def delete(connection, id: int):
    try:
        query = connection.cursor()
        query.execute("DELETE FROM geo_table WHERE id = %s", (id,))
        connection.commit()
        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

query = connection.cursor()

try:
#     with open("./../../data/geo.csv", encoding="utf-8-sig") as file:
#         for line in file.readlines():
#             line_data = line.strip().split(";")
#             parent_id: int = -1
#             for data in line_data:
#                 try:
#                     if parent_id != -1:
#                         info = read_childs(data, parent_id)[0]
#                     else:
#                         info = read(data)[0][0]
#                     parent_id = info
#                 except NodeNotExistsException:
#                     parent_id = create(data, parent_id)
                    
    with open("./data/DataBase.csv") as data:
        for line in data.readlines():
            base_line = line.strip().split(";")
            parent_id = base_line[1]
            title = base_line[2]
            # Проверяем, существует ли запись с таким же parent_id и title
            query.execute("SELECT id FROM geo_table WHERE parent_id = %s AND title = %s", (parent_id, title))
            existing_record = query.fetchone()
            if not existing_record:
                query.execute("INSERT INTO geo_table (parent_id, title) VALUES (%s, %s)", (parent_id, title))
                connection.commit()

except FileNotFoundError:
    print("File not found.")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")

query.close()

def data_print(id: int, indent=0, visited=None, text_widget=None) -> List[Tuple[int, int, str]]:
    if visited is None:
        visited = set()

    try:
        query = connection.cursor()
        query.execute(
            "SELECT id, parent_id, title FROM geo_table WHERE parent_id = %s", (id,)
        )
        parents = query.fetchall()

        for parent in parents:
            if parent[0] == parent[1]:
                continue

            text_widget.insert("end", "    " * indent + f"{parent[0]}: {parent[2]}\n")
            data_print(parent[0], indent + 1, text_widget=text_widget)

        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def database_print(connection, text_widget):
    try:
        query = connection.cursor()
        query.execute("SELECT * FROM geo_table")
        db = query.fetchall()

        for elem in db:
            if elem[0] == elem[1]:
                text_widget.insert("end", f"{elem[0]}: {elem[2]}\n")
                data_print(elem[0], indent=1, text_widget=text_widget)

        query.close()

    except mariadb.Error as e:
        text_widget.insert("end",f"Error executing SQL statement: {e}")


try:
    connection.commit()

except mariadb.Error as e:
    print(f"Error closing connection to MariaDB: {e}")