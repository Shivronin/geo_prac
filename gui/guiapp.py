import sys
import os
from tkinter import Scrollbar, Text, Tk, Label, Entry, Button

# Установите путь к проекту
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

from marjpt.adjlst import connection, add_node, update, delete, database_print
import marjpt.adjlst

class GUI:
    def __init__(self):
        self.window = Tk()
        self.window.title("Practice application")

        # Создаем метку и поле ввода для добавления узла
        self.label_add = Label(self.window, text="Add Node:")
        self.label_add.grid(row=0, column=0, padx=10, pady=10)
        self.entry_add_pid = Entry(self.window)
        self.entry_add_pid.grid(row=0, column=1, padx=10, pady=10)
        self.entry_add_title = Entry(self.window)
        self.entry_add_title.grid(row=0, column=2, padx=10, pady=10)
        self.button_add = Button(self.window, text="Add", command=self.add_node)
        self.button_add.grid(row=0, column=3, padx=10, pady=10)

        # Создаем метку и поле ввода для обновления узла
        self.label_update = Label(self.window, text="Update Node:")
        self.label_update.grid(row=1, column=0, padx=10, pady=10)
        self.entry_update_id = Entry(self.window)
        self.entry_update_id.grid(row=1, column=1, padx=10, pady=10)
        self.entry_update_title = Entry(self.window)
        self.entry_update_title.grid(row=1, column=1, padx=10, pady=10)
        self.button_update = Button(self.window, text="Update", command=self.update_node)
        self.button_update.grid(row=1, column=2, padx=10, pady=10)

        # Создаем метку и поле ввода для удаления узла
        self.label_delete = Label(self.window, text="Delete Node:")
        self.label_delete.grid(row=2, column=0, padx=10, pady=10)
        self.entry_delete = Entry(self.window)
        self.entry_delete.grid(row=2, column=1, padx=10, pady=10)
        self.button_delete = Button(self.window, text="Delete", command=self.delete_node)
        self.button_delete.grid(row=2, column=2, padx=10, pady=10)

        # Кнопка для вывода базы данных
        self.button_print = Button(self.window, text="Print Database", command=self.print_database)
        self.button_print.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.button_print = Button(self.window, text="Print Database", command=self.print_database)
        self.button_print.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Создаем текстовый виджет и полосу прокрутки для вывода таблицы
        self.text_output = Text(self.window, height=50, width=50)
        self.text_output.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.scrollbar = Scrollbar(self.window)
        self.scrollbar.grid(row=4, column=3, sticky="NS")

        self.text_output.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_output.yview)

        self.window.mainloop()

    def add_node(self):
        parent_id = self.entry_add_pid.get()
        title = self.entry_add_title.get()
        add_node(connection, parent_id, title)

    def update_node(self):
        id = self.entry_update_id.get()
        title = self.entry_update_title.get()
        update(connection, id, title)

    def delete_node(self):
        id = self.entry_delete.get()
        delete(connection, id)

    def print_database(self):
        self.text_output.delete("1.0", "end")
        sys.stdout = self.text_output
        marjpt.adjlst.database_print(connection, self.text_output)
        sys.stdout = sys.__stdout__

if __name__ == "__main__":
    GUI()