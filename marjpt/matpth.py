
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

    # query.execute("DROP TABLE IF EXISTS mat_pth") #Это тут временно

    # Проверяем, существует ли таблица nst_st
    query.execute("CREATE TABLE IF NOT EXISTS mat_pth (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL, path VARCHAR(100))")
    print("Таблица mat_pth успешно создана в базе данных dbm")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")


def get_id(id: int):
    try:
        query = connection.cursor()
        query.execute(f"SELECT * FROM mat_pth WHERE id={id}")
        fetch = query.fetchone()
        query.close()
        return fetch
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def get_title(connection, title: str):
    try:
        query = connection.cursor()
        query.execute(f"SELECT * FROM mat_pth WHERE title='{title}'")
        fetch = query.fetchone()
        query.close()
        return fetch
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def get_path(connection, path: str):
    try:
        query = connection.cursor()
        query.execute(f"SELECT * FROM mat_pth WHERE path='{path}'")
        fetch = query.fetchone()
        query.close()
        return fetch
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def get_branch(path: str):
    try:
        query = connection.cursor()
        query.execute(f"SELECT * FROM mat_pth WHERE path LIKE '{path}%'")
        fetch = query.fetchall()
        query.close()
        return fetch
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")


def add_node(connection, title: str, parent_path: str = None):

    query = connection.cursor()

    # Проверка на существующую запись с таким же названием
    existing_node = get_title(connection, title)
    if existing_node:
        query.close()
        return

    if parent_path is None:
        try:
            # Создание нового пути для нового объекта
            query.execute(f"INSERT INTO mat_pth (title) VALUES('{title}')")
            new_element_id = query.lastrowid
            query.execute(f"UPDATE mat_pth SET path='{new_element_id}' WHERE id={new_element_id}")
            connection.commit()
        except mariadb.Error as err:
            print(err)
    else:
        parent = get_path(connection, parent_path)
        if parent:
            try:
                # Создание нового объекта с определенным путем
                query.execute(f"INSERT INTO mat_pth (title) VALUES('{title}')")
                new_element_id = query.lastrowid
                query.execute(f"UPDATE mat_pth SET path='{parent_path + '.' + str(new_element_id)}' WHERE id={new_element_id}")
                connection.commit()
            except mariadb.Error as err:
                print(err)
        else:
            print("Родитель не найден:", parent_path)

    query.close()

query = connection.cursor()

visited_nodes = set()

try:
    with open("./data/DataBase.csv") as data:
        for line in data.readlines():
            base_line = line.replace("п»ї", "").strip().split(";")

            if base_line[0] == base_line[1]:
                # Проверяем, существует ли уже запись с таким же путем
                existing_node = get_path(connection, base_line[2])
                if not existing_node:
                    add_node(connection, base_line[2])
            else:
                parent = get_id(base_line[1])
                # Проверяем, существует ли уже запись с таким же путем
                existing_node = get_path(connection, base_line[2])
                if not existing_node:
                    add_node(connection, base_line[2], parent[-1])

    query.close()

except FileNotFoundError:
    print("File not found.")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")


def data_print(path: str, indent=0, printed=None, text_widget=None, connection=connection):
    if printed is None:
        printed = set()

    try:
        query = connection.cursor()
        query.execute(f"SELECT * FROM mat_pth WHERE path LIKE '{path}%' ORDER BY path")

        parents = query.fetchall()[:]

        if len(parents) == 0:
            query.close()
            return

        for parent in parents:
            if parent[0] == parent[1]:
                continue

            if parent[0] not in printed:
                visited = 'Visited' if parent[0] in visited_nodes else ''
                text_widget.insert("end","    " * indent + f"{parent[0]}: {parent[1]}, {parent[-1]} {visited}\n")
                printed.add(parent[0])
                data_print(parent[-1], indent + 1, printed, text_widget=text_widget, connection=connection)

        query.close()

    except mariadb.Error as e:
        text_widget.insert("end", f"Error executing SQL statement: {e}")


def database_print(connection, text_widget):
    try:
        query = connection.cursor()
        query.execute("SELECT * FROM mat_pth")
        db = query.fetchall()

        for elem in db:
            if str(elem[0]) == elem[-1]:
                visited_nodes = set()
                data_print(elem[-1], indent=1, printed=visited_nodes, text_widget=text_widget, connection=connection)

        query.close()

    except mariadb.Error as e:
        text_widget.insert("end", f"Error executing SQL statement: {e}")

query = connection.cursor()

def update(connection, title: str, new_title: str):
    try:
        query = connection.cursor()
        query.execute(f"UPDATE mat_pth SET title = '{new_title}' WHERE title = '{title}'")
        connection.commit()

        query.close()   

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")


def delete(connection, path: str) -> None:
    try:
        query = connection.cursor()

        query.execute(f"DELETE FROM mat_pth WHERE path LIKE '{path}%'")
        connection.commit()

        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")


try:
    connection.commit()
    query.close()
    connection.close()
except mariadb.Error as e:
    print(f"Error closing connection: {e}")
    exit(1)