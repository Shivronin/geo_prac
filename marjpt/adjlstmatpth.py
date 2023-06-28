import os
import mariadb
from dotenv import load_dotenv
import mariadb

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

try:
    query = connection.cursor()

    # Создаем базу данных, если она не существует
    query.execute("CREATE DATABASE IF NOT EXISTS dbm")

    # Выбираем созданную базу данных
    query.execute("USE dbm")

    # query.execute("DROP TABLE IF EXISTS adj_lst_mat_pth") #Это тут временно

    # Проверяем, существует ли таблица nst_st
    query.execute("CREATE TABLE IF NOT EXISTS adj_lst_mat_pth (id INT AUTO_INCREMENT PRIMARY KEY,parent_id INT,title VARCHAR(50) NOT NULL,path VARCHAR(100),FOREIGN KEY (parent_id) REFERENCES adj_lst_mat_pth (id) ON DELETE CASCADE);")
    print("Таблица adj_lst_mat_pth успешно создана в базе данных dbm")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}")

def create(connection, title: str, parent_id=None, parent_path=None):
    try:
        query = connection.cursor()

        if parent_id is not None:
            query.execute(f"SELECT path FROM adj_lst_mat_pth WHERE id={parent_id}")
            fetch = query.fetchone()

            if fetch is not None:
                parent_path = fetch[0]

        if parent_path is not None:
            query.execute(f"SELECT id FROM adj_lst_mat_pth WHERE path='{parent_path}'")
            fetch = query.fetchone()
        if parent_path is not None:
            parent_id = fetch[0]

        if parent_path is None and parent_id is None:
            try:
                query.execute(f"INSERT INTO adj_lst_mat_pth (title) VALUES('{title}')")
                connection.commit()
                new_element_id = query.lastrowid
                query.execute(f"UPDATE adj_lst_mat_pth SET parent_id={new_element_id}, path='{new_element_id}' WHERE id={new_element_id}")
                connection.commit()
            except mariadb.Error as err:
                print(err)
                

        elif parent_path is not None and parent_id is not None:
        # create new object with some path
            try:
                query.execute(f"INSERT INTO adj_lst_mat_pth (parent_id, title) VALUES({parent_id}, '{title}')")
                connection.commit()
                new_element_id = query.lastrowid
                query.execute(f"UPDATE adj_lst_mat_pth SET path='{parent_path + '.' + str(new_element_id)}' WHERE id={new_element_id}")
                connection.commit()
            except mariadb.Error as err:
                print(err)

        else:
            pass

        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def get_title(connection, title: str):
    try:
        query = connection.cursor()
        query.execute(f"SELECT * FROM adj_lst_mat_pth WHERE title='{title}'")
        fetch = query.fetchone()
        query.close()
        return fetch
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def get_branch(path: str):
    try:
        query = connection.cursor()
        query.execute(f"SELECT * FROM adj_lst_mat_pth WHERE path LIKE '{path}%'")
        fetch = query.fetchall()
        query.close()
        return fetch
    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def get_children(parent_id: int):
    try:
        children = []

        query = connection.cursor()
        query.execute(f"SELECT * FROM adj_lst_mat_pth WHERE parent_id={parent_id}")

        rows = query.fetchall()

        if len(rows) == 0:
            query.close()
            return children

        for row in rows:
            if row[0] == row[1]:
                continue

            child = list(row)
            child[-1] = None  # Обнуляем поле "path" у потомка

            children.append(child)

            children += get_children(row[0])

        query.execute(f"UPDATE adj_lst_mat_pth SET path=NULL WHERE id={parent_id}")  # Обновляем путь после завершения цикла
        connection.commit()

        query.close()

        return children

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")


query = connection.cursor()

try:
    with open("./data/DataBase.csv") as data:
        for line in data.readlines():
            base_line = line.replace("п»ї", "").strip().split(";")

            title = base_line[2]
            existing_data = get_title(connection, title)

            if existing_data is None:
                if base_line[0] == base_line[1]:
                    create(connection, title)
                else:
                    create(connection, title, base_line[1])

except FileNotFoundError:
    print("Файл не найден.")

except mariadb.Error as e:
    print(f"Ошибка выполнения SQL-запроса: {e}")

except FileNotFoundError:
    print("File not found.")

except mariadb.Error as e:
    print(f"Error executing SQL statement: {e}") 

def delete_element(connection, id_or_path):
    try:
        query = connection.cursor()

        if isinstance(id_or_path, str):
            query.execute(f"DELETE FROM adj_lst_mat_pth WHERE path='{id_or_path}'")
        elif isinstance(id_or_path, int):
            query.execute(f"DELETE FROM adj_lst_mat_pth WHERE id={id_or_path}")
        else:
            raise ValueError("Invalid argument type. Expected str or int.")

        connection.commit()
        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

def update(connection, new_title: str, id=None, path=None):
    try:
        query = connection.cursor()
        if id is not None:
            query.execute(f"UPDATE adj_lst_mat_pth SET title='{new_title}' WHERE id={id}")
        if path is not None:
            query.execute(f"UPDATE adj_lst_mat_pth SET title='{new_title}' WHERE path='{path}'")
            connection.commit()
    
        query.close()

    except mariadb.Error as e:
        print(f"Error executing SQL statement: {e}")

visited = set()

def data_print(id: int, indent=0, visited=None, text_widget=None, connection=connection):
    if visited is None:
        visited = set()
    
    try:
        if id in visited:  # Проверка, был ли узел уже посещен
            return

        visited.add(id)  # Добавление текущего узла в множество посещенных узлов

        query = connection.cursor()
        query.execute(f"SELECT * FROM adj_lst_mat_pth WHERE parent_id={id}")

        parents = query.fetchall()

        if len(parents) == 0:
            query.close()
            return

        for parent in parents:
            if parent[0] == parent[1]:
                continue

            text_widget.insert("end","    " * indent + f"{parent[0]}: {parent[2]}, {parent[-1]}\n")

            # Рекурсивно вызываем data_print для вывода потомков первого родительского узла
            data_print(parent[0], indent + 1, text_widget=text_widget, connection=connection)

        query.close()

    except mariadb.Error as e:
        text_widget.insert("end",f"Error executing SQL statement: {e}")

def database_print(connection, text_widget):
    try:
        query = connection.cursor()
        query.execute("SELECT * FROM adj_lst_mat_pth")
        db = query.fetchall()

        for elem in db:
            if elem[0] == elem[1] and elem[0] not in visited:
                text_widget.insert("end",f"{elem[0]}: {elem[2]}, {elem[-1]}\n")
                data_print(elem[-1], indent=1, text_widget=text_widget, connection=connection) 

        query.close()

    except mariadb.Error as e:
        text_widget.insert("end",f"Error executing SQL statement: {e}")

try:
    connection.commit()
    query.close()
    connection.close()
except mariadb.Error as e:
    print(f"Error closing connection: {e}")
    exit(1)