
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

    # query.execute("DROP TABLE IF EXISTS nst_st") #Это тут временно

    # Проверяем, существует ли таблица nst_st
    query.execute("CREATE TABLE IF NOT EXISTS nst_st (id INT AUTO_INCREMENT PRIMARY KEY, left_key INT NOT NULL, right_key INT NOT NULL, title VARCHAR(255) NOT NULL, tree_id INT NOT NULL)")
    print("Таблица nst_st успешно создана в базе данных dbm")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")


def levels_id(all_nodes: list) -> list:
    try:
        query = connection.cursor()
        levels = []
        for node in all_nodes:
            query.execute("SELECT COUNT(*) FROM nst_st WHERE left_key <= %s AND right_key >= %s AND tree_id = %s", (node[1], node[2], node[4]))
            level = query.fetchone()
            levels.append((level[0], node[0], node[3], node[1], node[2]))
        query.close()
        return levels
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")


class NodeNotExistsException(Exception):
    def __init__(self, node_id):
        self.node_id = node_id
        self.message = f"Узел с идентификатором {node_id} не существует"
        super().__init__(self.message)

def print_tree():
    try:
        query = connection.cursor()
        query.execute("SELECT id, left_key, right_key, title, tree_id FROM nst_st ORDER BY tree_id, left_key")
        all_nodes = query.fetchall()
        levels = levels_id(all_nodes)

        for level in levels:
            tabs = "    " * level[0]
            print(f"{tabs}{str(level[1])} {level[2]} (left: {level[3]}, right: {level[4]})")

        query.close()
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def mtree_id() -> int:
    try:
        max_tree_id = 0
        query = connection.cursor()
        query.execute("SELECT tree_id FROM nst_st ORDER BY tree_id DESC")
        mtree = query.fetchone()
        if mtree:
            max_tree_id = mtree[0]
        return max_tree_id + 1
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def read(node: str) -> list:
    try:
        query = connection.cursor()
        query.execute("SELECT id FROM nst_st WHERE title = %s", (node,))
        result = query.fetchall()
        query.close()
        return result

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def read_childs(title: str, parent_id: int) -> list:
    try:
        query = connection.cursor()
        query.execute("SELECT left_key, right_key FROM nst_st where id = %s", (parent_id,))
        this = query.fetchone()
        if not this:
            raise NodeNotExistsException(title)
        query.execute("SELECT id FROM nst_st WHERE left_key >= %s AND right_key <= %s AND title = %s GROUP BY id ORDER BY id", (this[0], this[1], title))
        all_childs = query.fetchall()
        if len(all_childs) == 0:
            raise NodeNotExistsException(title)
        query.close()
        return all_childs

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")
        
def create(node: str, parent_id: int) -> int:
    try:
        query = connection.cursor()
        query.execute("SELECT right_key, tree_id FROM nst_st WHERE id = %s", (parent_id,))
        prev = query.fetchone()
        if not prev:
            prev = (1, mtree_id())
        else:
            prev = prev

        query.execute("UPDATE nst_st SET left_key = left_key + 2 WHERE left_key > %s AND tree_id = %s", (prev[0], prev[1]))
        query.execute("UPDATE nst_st SET right_key = right_key + 2 WHERE right_key >= %s AND tree_id = %s", (prev[0], prev[1]))
        query.execute("INSERT INTO nst_st (left_key, right_key, title, tree_id) VALUES (%s, %s, %s, %s)", (prev[0], prev[0] + 1, node, prev[1]))

        connection.commit()
        query.execute("SELECT id FROM nst_st ORDER BY id DESC")
        id = query.fetchone()
        query.close()
        return id[0]

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")
        
try:
    with open("./data/DataBase.csv") as data:
        for line in data.readlines():
            base_line = line.strip().split(";")
            node_title = base_line[2]
            existing_nodes = read(node_title)
            
            if not existing_nodes:
                try:
                    read_childs(base_line[2], base_line[1])
                except:
                    create(base_line[2], base_line[1])
            
except FileNotFoundError:
    print("File not found.")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")
    
def delete(node_id: int) -> None:
    try:
        query = connection.cursor()

        # Получаем информацию о узле, который нужно удалить
        query.execute("SELECT left_key, right_key, tree_id FROM nst_st WHERE id = %s", (node_id,))
        node = query.fetchone()
        if not node:
            raise NodeNotExistsException(node_id)

        # Вычисляем ширину удаляемого поддерева
        width = node[1] - node[0] + 1

        # Удаляем узлы поддерева
        query.execute("DELETE FROM nst_st WHERE left_key BETWEEN %s AND %s AND tree_id = %s", (node[0], node[1], node[2]))

        # Обновляем левые ключи узлов, находящихся справа от удаляемого поддерева
        query.execute("UPDATE nst_st SET left_key = left_key - %s WHERE left_key > %s AND tree_id = %s", (width, node[1], node[2]))

        # Обновляем правые ключи узлов, находящихся справа от удаляемого поддерева
        query.execute("UPDATE nst_st SET right_key = right_key - %s WHERE right_key > %s AND tree_id = %s", (width, node[1], node[2]))

        connection.commit()
        query.close()

        print(f"Узел с идентификатором {node_id} успешно удален")

    except mariadb.Error as e:
        print(f"Ошибка выполнения SQL-запроса: {e}")
        exit(1)
        
def add_node(title: str, parent_id: int) -> None:
    try:
        query = connection.cursor()

        # Получаем информацию о родительском узле
        query.execute("SELECT left_key, right_key, tree_id FROM nst_st WHERE id = %s", (parent_id,))
        parent_node = query.fetchone()
        if not parent_node:
            raise NodeNotExistsException(parent_id)

        # Получаем информацию о правом ключе последнего дочернего узла родительского узла
        query.execute("SELECT MAX(right_key) FROM nst_st WHERE left_key > %s AND right_key < %s AND tree_id = %s", (parent_node[0], parent_node[1], parent_node[2]))
        last_child_right_key = query.fetchone()[0]
        if not last_child_right_key:
            last_child_right_key = parent_node[0]  # Если нет дочерних узлов, используем левый ключ родительского узла

        # Обновляем левые и правые ключи у существующих узлов
        query.execute("UPDATE nst_st SET left_key = CASE WHEN left_key > %s THEN left_key + 1 ELSE left_key END, right_key = CASE WHEN right_key >= %s THEN right_key + 1 ELSE right_key END WHERE tree_id = %s", (last_child_right_key, last_child_right_key, parent_node[2]))

        # Вставляем новый узел с корректными левыми и правыми ключами
        new_node_id = create(title, parent_id)
        new_node_right_key = last_child_right_key + 2
        query.execute("UPDATE nst_st SET right_key = %s WHERE id = %s", (new_node_right_key, new_node_id))
        last_child_right_key = new_node_right_key

        connection.commit()
        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

        
def update_node(node_id: int, new_title: str) -> None:
    try:
        query = connection.cursor()

        # Получаем информацию об обновляемом узле
        query.execute("SELECT title FROM nst_st WHERE id = %s", (node_id,))
        node = query.fetchone()
        if not node:
            raise NodeNotExistsException(node_id)

        # Обновляем название узла
        query.execute("UPDATE nst_st SET title = %s WHERE id = %s", (new_title, node_id))

        connection.commit()
        query.close()

        print(f"Название узла с идентификатором {node_id} успешно обновлено")

    except mariadb.Error as e:
        print(f"Ошибка выполнения SQL-запроса: {e}")
        exit(1)

print_tree()

try:
    connection.commit()
    query.close()
    connection.close()
except mariadb.Error as e:
    print(f"Error closing connection: {e}")