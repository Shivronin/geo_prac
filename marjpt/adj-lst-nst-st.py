import os
import mariadb
from dotenv import load_dotenv

# Загрузка данных из файла .env
load_dotenv()

try:
    connection = mariadb.connect(
        host=os.getenv('MARIADB_HOST', 'localhost'),
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

#     query.execute("DROP TABLE IF EXISTS adj_lst_nst_st") #Это тут временно

    # Проверяем, существует ли таблица geo_table
    query.execute("CREATE TABLE IF NOT EXISTS `adj_lst_nst_st` (id INT AUTO_INCREMENT PRIMARY KEY, parent_id INT, title VARCHAR(50) NOT NULL, left_key INT NOT NULL, right_key INT NOT NULL, FOREIGN KEY (parent_id) REFERENCES `adj_lst_nst_st`(id) ON DELETE CASCADE)")
    print("Таблица adj_lst_nst_st успешно создана в базе данных dbm")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")

def mtree_id() -> int:
    try:
        max_parent_id = 0
        query = connection.cursor()
        query.execute("SELECT parent_id FROM adj_lst_nst_st ORDER BY parent_id DESC")
        mtree = query.fetchone()
        if mtree:
            max_parent_id = mtree[0]
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")
    return max_parent_id + 1

class NodeNotExistsException(Exception):
    def __init__(self, title: str):
        self.message = "Node with id = {0} is not exists".format(title)
        super().__init__(self.message)

def create(title: str, parent_id: int) -> int:
    try:
        query = connection.cursor()
        query.execute("SELECT id, right_key FROM adj_lst_nst_st ORDER BY id DESC LIMIT 1")
        max_id_node = query.fetchone()
        query.execute("SELECT right_key FROM adj_lst_nst_st ORDER BY right_key DESC LIMIT 1")
        max_id_rnode = query.fetchone()
        query.execute("SELECT right_key FROM adj_lst_nst_st AS go WHERE go.id = {0}".format(parent_id))
        parent_id_node = query.fetchone()

        if max_id_node:
            max_id = max_id_node[0]
            max_lid = max_id_rnode[0] +1
            max_rid = max_id_rnode[0] +2
        else:
            max_id = 0
            max_lid = 1
            max_rid = 2
        if not parent_id_node:
            parent_id_node = [max_rid]
            parent_id = max_id +1
        else:
            max_lid = parent_id_node[0]
            max_rid = parent_id_node[0] + 1

        query.execute("UPDATE adj_lst_nst_st SET left_key = left_key + 2 WHERE left_key > %s", (parent_id_node[0],))
        query.execute("UPDATE adj_lst_nst_st SET right_key = right_key + 2 WHERE right_key >= %s", (parent_id_node[0],))
        query.execute("INSERT INTO adj_lst_nst_st (id, title, left_key, right_key, parent_id) VALUES (%s, %s, %s, %s, %s)", (max_id + 1, title, max_lid, max_rid, parent_id))
        connection.commit()
        query.close()
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")
    return max_id +1

def levels_id(all_nodes: list) -> list:
    try:
        query = connection.cursor()
        levels = []
        for node in all_nodes:
            query.execute("SELECT COUNT(*) FROM adj_lst_nst_st WHERE left_key <= %s AND right_key >= %s", (node[3], node[4]))
            level = query.fetchone()
            levels.append((level[0], node[0], node[2], node[3], node[4]))
        query.close()
        return levels
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def read(id=None, title=None) -> list:
    try:
        query = connection.cursor()
        
        if id is not None:
            query.execute("SELECT left_key, right_key FROM `adj_lst_nst_st` WHERE id = %s", (id,))
        elif title is not None:
            query.execute("SELECT left_key, right_key FROM `adj_lst_nst_st` WHERE title = %s", (title,))
        else:
            raise ValueError("Must provide either id or title")

        this = query.fetchone()
        if not this:
            if id is not None:
                raise NodeNotExistsException(id)
            elif title is not None:
                raise NodeNotExistsException(title)

        query.execute("SELECT id, parent_id, title, left_key, right_key FROM `adj_lst_nst_st` WHERE left_key >= %s AND right_key <= %s GROUP BY id ORDER BY id", (this[0], this[1]))
        all = query.fetchall()
        query.close()
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")
    return all


def read_childs(title: str, parent_id: int) -> list:
    try:
        query = connection.cursor()
        query.execute("SELECT left_key, right_key FROM adj_lst_nst_st where title = %s AND parent_id = %s", (title, parent_id,))
        this = query.fetchone()
        if not this:
            raise NodeNotExistsException(title)
        query.execute("SELECT id, title, parent_id FROM adj_lst_nst_st WHERE left_key >= {0} AND right_key <= {1} GROUP BY id ORDER BY id".format(this[0], this[1]))
        all_childs = query.fetchall()
        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")
    return all_childs

def data_print():
    try:
        query = connection.cursor()
        query.execute("SELECT id, parent_id, title, left_key, right_key FROM adj_lst_nst_st ORDER BY left_key")
        all_nodes = query.fetchall()
        levels = levels_id(all_nodes)

        for level in levels:
                tabs = "    " * level[0]
                print(f"{tabs}{str(level[1])} {level[2]} (left: {level[3]}, right: {level[4]})")

        query.close()
        
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def database_print(levels: list):
    try:
        for level in levels:
            print(str(level[1]) + " " + str(level[2]) + " (" + str(level[3]) + ", " + str(level[4]) + ")")
    
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")


try:
    with open("./data/DataBase.csv") as data:
        for line in data.readlines():
            base_line = line.strip().split(";")
            title = base_line[2]
            parent_id = int(base_line[1])

            # Проверяем, существует ли уже запись с таким же title и parent_id
            query.execute("SELECT id FROM adj_lst_nst_st WHERE title = %s AND parent_id = %s", (title, parent_id))
            existing_data = query.fetchone()

            if existing_data:
                # Если запись уже существует, пропускаем операцию вставки
                continue

            # Выполняем операцию вставки только для новых данных
            create(title, parent_id)

except FileNotFoundError:
    print("File not found.")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")

def delete(id: int) -> None:
    try:
        query = connection.cursor()
        query.execute("SELECT left_key, right_key FROM adj_lst_nst_st AS go WHERE go.id = %s", (id,))
        delete = query.fetchone()
        if not delete:
            raise NodeNotExistsException(id)
        tree_width = delete[1] - delete[0] + 1
        query.execute("UPDATE adj_lst_nst_st SET right_key = right_key - %s WHERE right_key > %s", (tree_width, delete[1],))
        query.execute("UPDATE adj_lst_nst_st SET left_key = left_key - %s WHERE left_key > %s", (tree_width, delete[1],))
        query.execute("DELETE FROM adj_lst_nst_st WHERE id = %s", (id,))
        connection.commit()
        query.close()
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def update(title: str, id: int) -> None:
    try:
        query = connection.cursor()
        query.execute("UPDATE adj_lst_nst_st SET title = '{0}' WHERE id = {1}".format(title, id))
        connection.commit()
        query.close() 
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

data_print()

try:
    connection.commit()
    query.close()
    connection.close()
except mariadb.Error as e:
    print(f"Error closing connection: {e}")