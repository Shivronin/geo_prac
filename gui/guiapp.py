import sys
import os
from tkinter import Scrollbar, Text, Tk, Label, Entry, Button, Frame

# Установите путь к проекту
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

from marjpt.adjlst import connection
import marjpt.adjlst
import marjpt.nstst
import marjpt.adjlstnstst
import marjpt.matpth
import marjpt.adjlstmatpth

class GUI:
    def __init__(self):
        self.window = Tk()
        self.window.title("Practice Application")

        self.current_form = None  # Ссылка на текущую форму

        # Кнопки для изменения содержимого формы
        self.button_adj_lst = Button(self.window, text="Adjacency List", command=self.show_adj_lst_form)
        self.button_nest_set = Button(self.window, text="Nested Set", command=self.show_nest_set_form)
        self.button_adj_lst_nst_st = Button(self.window, text="Adjacency List + Nested Set", command=self.show_adj_lst_nst_st_form)
        self.button_mat_pth = Button(self.window, text="Materialized Path", command=self.show_mat_pth_form)
        self.button_adj_lst_mat_pth = Button(self.window, text="Adjacency List + Materialized Path", command=self.show_adj_lst_mat_pth_form)
        # Создаем метку и поле ввода для добавления узла
        self.label_add = Label(self.window, text="Add Node:")
        self.entry_add_pid = Entry(self.window)
        self.entry_add_title = Entry(self.window)
        self.button_add = Button(self.window, text="Add", command=self.add_node)

        # Создаем метку и поле ввода для обновления узла
        self.label_update = Label(self.window, text="Update Node:")
        self.entry_update_id = Entry(self.window)
        self.entry_update_title = Entry(self.window)
        self.button_update = Button(self.window, text="Update", command=self.update_node)

        # Создаем метку и поле ввода для удаления узла
        self.label_delete = Label(self.window, text="Delete Node:")
        self.entry_delete = Entry(self.window)
        self.button_delete = Button(self.window, text="Delete", command=self.delete_node)

        # Кнопка для вывода базы данных
        self.button_print = Button(self.window, text="Print Database", command=self.print_database)

        # Создаем текстовый виджет и полосу прокрутки для вывода таблицы
        self.text_output = Text(self.window, height=30, width=90)
        self.scrollbar = Scrollbar(self.window)

        self.label_add.grid(row=1, column=0, padx=10, pady=10)
        self.entry_add_pid.grid(row=1, column=1, padx=10, pady=10)
        self.entry_add_title.grid(row=1, column=2, padx=10, pady=10)
        self.button_add.grid(row=1, column=3, padx=10, pady=10)
        
        self.label_update.grid(row=3, column=0, padx=10, pady=10)
        self.entry_update_id.grid(row=3, column=1, padx=10, pady=10)
        self.entry_update_title.grid(row=3, column=2, padx=10, pady=10)
        self.button_update.grid(row=3, column=3, padx=10, pady=10)

        self.label_delete.grid(row=5, column=0, padx=10, pady=10)
        self.entry_delete.grid(row=5, column=1, padx=10, pady=10)
        self.button_delete.grid(row=5, column=2, padx=10, pady=10)

        self.button_print.grid(row=6, column=1, columnspan=2, padx=10, pady=10)

        self.text_output.grid(row=7, column=0, columnspan=5, padx=10, pady=10)
        self.scrollbar.grid(row=7, column=5, sticky="NS")

        self.text_output.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_output.yview)

        self.button_adj_lst.grid(row=0, column=4, padx=10, pady=10)
        self.button_nest_set.grid(row=1, column=4, padx=10, pady=10)
        self.button_adj_lst_nst_st.grid(row=2, column=4, padx=10, pady=10)
        self.button_mat_pth.grid(row=3, column=4, padx=10, pady=10)
        self.button_adj_lst_mat_pth.grid(row=4, column=4, padx=10, pady=10)

        self.window.mainloop()

    def show_adj_lst_form(self):
        self.clear_form()

        self.current_form = Frame(self.window)

        self.metod = 1

        self.window.title("Adjacency List")

        self.label_add_inf1 = Label(self.window, text="parent_id")
        self.label_add_inf2 = Label(self.window, text="title")
        self.label_update_inf1 = Label(self.window, text="id")
        self.label_update_inf2 = Label(self.window, text="new_title")
        self.label_delete_inf1 = Label(self.window, text="id")

        self.button_add.grid(row=1, column=3, padx=10, pady=10)
        self.button_update.grid(row=3, column=3, padx=10, pady=10)
        self.button_delete.grid(row=5, column=2, padx=10, pady=10)
        self.label_add_inf1.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
        self.label_add_inf2.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
        self.label_update_inf1.grid(row=2, column=1, rowspan=2, padx=10, pady=10)
        self.label_update_inf2.grid(row=2, column=2, rowspan=2, padx=10, pady=10)
        self.label_delete_inf1.grid(row=4, column=1, rowspan=2, padx=10, pady=10)

        self.current_form.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

    def show_nest_set_form(self):
        self.clear_form()

        self.current_form = Frame(self.window)

        self.window.title("nest-set")

        self.metod = 2

        self.label_add_inf1 = Label(self.window, text="title")
        self.label_add_inf2 = Label(self.window, text="parent_id")
        self.label_update_inf1 = Label(self.window, text="id")
        self.label_update_inf2 = Label(self.window, text="new_title")
        self.label_delete_inf1 = Label(self.window, text="id")

        self.label_add_inf1.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
        self.label_add_inf2.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
        self.label_update_inf1.grid(row=2, column=1, rowspan=2, padx=10, pady=10)
        self.label_update_inf2.grid(row=2, column=2, rowspan=2, padx=10, pady=10)
        self.label_delete_inf1.grid(row=4, column=1, rowspan=2, padx=10, pady=10)

        self.current_form.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

    def show_adj_lst_nst_st_form(self):
        self.clear_form()

        # Создаем форму Nest-Set
        self.current_form = Frame(self.window)

        self.window.title("Adjacency List + Nested Set")

        self.metod = 3

        self.label_add_inf1 = Label(self.window, text="title")
        self.label_add_inf2 = Label(self.window, text="parent_id")
        self.label_update_inf1 = Label(self.window, text="new_title")
        self.label_update_inf2 = Label(self.window, text="id")
        self.label_delete_inf1 = Label(self.window, text="id")

        self.label_add_inf1.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
        self.label_add_inf2.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
        self.label_update_inf1.grid(row=2, column=1, rowspan=2, padx=10, pady=10)
        self.label_update_inf2.grid(row=2, column=2, rowspan=2, padx=10, pady=10)
        self.label_delete_inf1.grid(row=4, column=1, rowspan=2, padx=10, pady=10)

        self.current_form.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

    def show_mat_pth_form(self):
        self.clear_form()

        # Создаем форму Nest-Set
        self.current_form = Frame(self.window)

        self.window.title("Materialized Path")

        self.metod = 4

        self.label_add_inf1 = Label(self.window, text="title")
        self.label_add_inf2 = Label(self.window, text="parent_title")
        self.label_update_inf1 = Label(self.window, text="title")
        self.label_update_inf2 = Label(self.window, text="new_title")
        self.label_delete_inf1 = Label(self.window, text="title")

        self.label_add_inf1.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
        self.label_add_inf2.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
        self.label_update_inf1.grid(row=2, column=1, rowspan=2, padx=10, pady=10)
        self.label_update_inf2.grid(row=2, column=2, rowspan=2, padx=10, pady=10)
        self.label_delete_inf1.grid(row=4, column=1, rowspan=2, padx=10, pady=10)

        self.current_form.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

    def show_adj_lst_mat_pth_form(self):
        self.clear_form()

        # Создаем форму Nest-Set
        self.current_form = Frame(self.window)

        self.window.title("Adjacency List + Materialized Path")

        self.metod = 5

        self.label_add_inf1 = Label(self.window, text="title")
        self.label_add_inf2 = Label(self.window, text="parent_title")
        self.label_update_inf1 = Label(self.window, text="new_title")
        self.label_update_inf2 = Label(self.window, text="title")
        self.label_delete_inf1 = Label(self.window, text="title")

        self.label_add_inf1.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
        self.label_add_inf2.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
        self.label_update_inf1.grid(row=2, column=1, rowspan=2, padx=10, pady=10)
        self.label_update_inf2.grid(row=2, column=2, rowspan=2, padx=10, pady=10)
        self.label_delete_inf1.grid(row=4, column=1, rowspan=2, padx=10, pady=10)

        self.current_form.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

    def add_node(self):
        if self.metod == 1:
            parent_id = self.entry_add_pid.get()
            title = self.entry_add_title.get()
            marjpt.adjlst.add_node(connection, parent_id, title)
        if self.metod == 2:
            title = self.entry_add_pid.get()
            parent_id = self.entry_add_title.get()
            marjpt.nstst.add_node(connection, title, parent_id)
        if self.metod == 3:
            title = self.entry_add_pid.get()
            parent_id = self.entry_add_title.get()
            marjpt.adjlstnstst.create(connection, title, parent_id)
        if self.metod == 4:
            title = self.entry_add_pid.get()
            parent_id = self.entry_add_title.get()
            parent_id_get = marjpt.matpth.get_title(connection, parent_id)[2]
            marjpt.matpth.add_node(connection, title, parent_id_get)
        if self.metod == 5:
            title = self.entry_add_pid.get()
            parent_id = self.entry_add_title.get()
            parent_id_get = marjpt.adjlstmatpth.get_title(connection, parent_id)[0]
            marjpt.adjlstmatpth.create(connection, title, parent_id_get)

    def update_node(self):
        if self.metod == 1:
            id = self.entry_update_id.get()
            title = self.entry_update_title.get()
            marjpt.adjlst.update(connection, id, title)
        if self.metod == 2:
            id = self.entry_update_id.get()
            title = self.entry_update_title.get()
            marjpt.nstst.update_node(connection, id, title)
        if self.metod == 3:
            title = self.entry_update_id.get()
            id = self.entry_update_title.get()
            marjpt.adjlstnstst.update(connection, title, id)
        if self.metod == 4:
            title = self.entry_update_id.get()
            new_title = self.entry_update_title.get()
            marjpt.matpth.update(connection, title, new_title)
        if self.metod == 5:
            new_title = self.entry_update_id.get()
            title = self.entry_update_title.get()
            title_get_title = marjpt.adjlstmatpth.get_title(connection, title)[0]
            marjpt.adjlstmatpth.update(connection, new_title, title_get_title)

    def delete_node(self):
        if self.metod == 1:
            id = self.entry_delete.get()
            marjpt.adjlst.delete(connection, id)
        if self.metod == 2:
            id = self.entry_delete.get()
            marjpt.nstst.delete(connection, id)
        if self.metod == 3:
            id = self.entry_delete.get()
            marjpt.adjlstnstst.delete(connection, id)
        if self.metod == 4:
            title = self.entry_delete.get()
            title_get_title = marjpt.matpth.get_title(connection, title)[2]
            marjpt.matpth.delete(connection, title_get_title)
        if self.metod == 5:
            title = self.entry_delete.get()
            title_get_title = marjpt.adjlstmatpth.get_title(connection, title)[3]
            marjpt.adjlstmatpth.delete_element(connection, title_get_title)

    def print_database(self):
        if self.metod == 1:
            self.text_output.delete("1.0", "end")
            sys.stdout = self.text_output
            marjpt.adjlst.database_print(connection, self.text_output)
            sys.stdout = sys.__stdout__
        if self.metod == 2:
            self.text_output.delete("1.0", "end")
            sys.stdout = self.text_output
            marjpt.nstst.print_tree(connection, self.text_output)
            sys.stdout = sys.__stdout__
        if self.metod == 3:
            self.text_output.delete("1.0", "end")
            sys.stdout = self.text_output
            marjpt.adjlstnstst.data_print(connection, self.text_output)
            sys.stdout = sys.__stdout__
        if self.metod == 4:
            self.text_output.delete("1.0", "end")
            sys.stdout = self.text_output
            marjpt.matpth.database_print(connection, self.text_output)
            sys.stdout = sys.__stdout__
        if self.metod == 5:
            self.text_output.delete("1.0", "end")
            sys.stdout = self.text_output
            marjpt.adjlstmatpth.database_print(connection, self.text_output)
            sys.stdout = sys.__stdout__

    def clear_form(self):
        if self.current_form:
            self.current_form.destroy()  # Удаляем текущую форму
            self.label_add_inf1.destroy()
            self.label_add_inf2.destroy()
            self.label_update_inf1.destroy()
            self.label_update_inf2.destroy()
            self.label_delete_inf1.destroy()
            self.text_output.delete("1.0", "end")


if __name__ == "__main__":
    GUI()
