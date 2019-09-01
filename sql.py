# -*- coding: utf-8 -*-
import sqlite3
import sys

MY_DATABASE = r"/media/la/Movies/python_sqlite.db"


# def connect_to_database(database_file):
# database = database_file
# global cursor, connect_to_database
# connect_to_database = sqlite3.connect(database)
# connect_to_database.text_factory = str
# cursor = connect_to_database.cursor()


# def close_connection():
# cursor.close()
# connect_to_database.close()


def select(table, column, required_condition_column, required_condition_value):
    # if the condition is not only regular condition , get out. (anti injection).
    for i in required_condition_value:
        for j in range(str(i).__len__()):
            if str(i)[
                j] not in "1234567890 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ אבגדהוזחטיכלמנסעפצקרשת_":
                print("injection!!!", i)
                return

    for i in required_condition_column:
        for j in range(str(i).__len__()):
            if str(i)[
                j] not in "1234567890 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ אבגדהוזחטיכלמנסעפצקרשת_":
                print("injection!!!", i)
                return

    database = MY_DATABASE
    connect_to_database = sqlite3.connect(database)
    connect_to_database.text_factory = str
    cursor = connect_to_database.cursor()

    print("SELECT {} FROM {} WHERE {} = '{}'".format(column, str(table), required_condition_column,
                                                     required_condition_value))
    result = cursor.execute("SELECT {} FROM {} WHERE {} = '{}'".format(column, str(table), required_condition_column,
                                                                       required_condition_value)).fetchall()

    # converting "list of tuples" to "list of strings".
    result = [[str(item) for item in results] for results in result]
    cursor.close()
    connect_to_database.close()
    return result


# insert to database.
def insert(table, columns, data):
    # using tuples because:
    # in the "insert" you can't use the column and the data with "+" char,
    # it makes problems because the special chars like space. so you should use "?" and "execute(),parameters)"
    # you cant use the same str for the parameters, because it will be like only one data for one column.
    # and because using tuple for the data, also using tuple for the columns.
    if type(columns) is not tuple or type(data) is not tuple:
        print("please use 'tuple' for the values and the column names.")
        return

    elif len(columns) != len(data):
        print("use the same number of elements fir the values and the columns")
        return

    database = MY_DATABASE
    connect_to_database = sqlite3.connect(database)
    connect_to_database.text_factory = str
    cursor = connect_to_database.cursor()

    # values_counter will save the chars "?, ?, ?"... as the number of the values in "data".
    # starting with "?" because:
    # a. always there are minimum one thing in "data".
    # b. the for right down will add ", ?" every time. but the first should be without ", "
    # so the "for" will start from the second element.
    values_counter = "?"

    # saving the columns names, just in str, to use "execute("insert... (" + columns_str + "...""
    # columns_str will save the names from columns in str in this way:
    # "column1, column2, column3, "...
    # starting with the first column name because:
    # a. always there are minimum one thing in "columns".
    # b. the for right down will add ", next_column_name" every time. but the first should be without ", "
    # so the "for" will start from the second element.
    columns_str = columns[0]

    # saving the chars "?, ?, ?"...  as the number of the values in "data".
    # starting with xrange(1, ...) because the first already define up there, without the ", "
    for i in range(1, len(columns)):
        values_counter += ", ?"

    # will save the names from columns in str in this way:
    # "column1, column2, column3, "...
    # starting with xrange(1, ...) because the first already define up there, without the ", "
    for i in range(1, len(columns)):
        columns_str += ", " + columns[i]
    print("INSERT INTO " + table + " (" + columns_str + ") VALUES (" + values_counter + ")", data)
    cursor.execute("INSERT INTO " + table + " (" + columns_str + ") VALUES (" + values_counter + ")", data)
    connect_to_database.commit()  # very important- saving the changes
    cursor.close()
    connect_to_database.close()


# insert to database.
def update(table, columns, data, condition):
    # using tuples because:
    # in the "update" you can't use the column and the data with "+" char,
    # it makes problems because the special chars like space. so you should use "?" and "execute(),parameters)"
    # you cant use the same str for the parameters, because it will be like only one data for one column.
    # and because using tuple for the data, also using tuple for the columns.
    if type(columns) is not tuple or type(data) is not tuple:
        print("please use 'tuple' for the values and the column names.")
        return

    elif len(columns) != len(data):
        print("use the same number of elements fir the values and the columns")
        return

    database = MY_DATABASE
    connect_to_database = sqlite3.connect(database)
    connect_to_database.text_factory = str
    cursor = connect_to_database.cursor()

    # saving the columns names, just in str, to use "execute("insert... (" + columns_str + "...""
    # columns_str will save the names from columns in str in this way:
    # "column1, column2, column3, "...
    # starting with the first column name because:
    # a. always there are minimum one thing in "columns".
    # b. the for right down will add ", next_column_name" every time. but the first should be without ", "
    # so the "for" will start from the second element.
    columns_and_data = columns[0] + "= '" + str(data[0]) + "'"

    # will save the names from columns in str in this way:
    # "column1, column2, column3, "...
    # starting with xrange(1, ...) because the first already define up there, without the ", "
    # cant put the ", " in the end of the loop, because the last element will end with ", ".
    for i in range(1, len(columns)):
        columns_and_data += ", " + str(columns[i]) + "= '" + str(data[i]) + "'"
    cursor.execute("UPDATE " + table + " SET " + columns_and_data + " WHERE " + condition)
    connect_to_database.commit()  # very important- saving the changes
    cursor.close()
    connect_to_database.close()


def new_database():
    connect_to_file = sqlite3.connect(MY_DATABASE)
    print((sqlite3.version))
    connect_to_file.close()


def create_table():
    database = MY_DATABASE
    connect_to_database = sqlite3.connect(database)
    connect_to_database.text_factory = str
    cursor = connect_to_database.cursor()

    cursor.execute("""CREATE TABLE Users ( 
    id VARCHAR(15), 
    gender CHAR(1), 
    x_cor VARCHAR(10),
    y_cor VARCHAR(10),
    phone VARCHAR(10),
    name VARCHAR,
    age VARCHAR(3),
    last_seen VARCHAR(14),
    birthday VARCHAR(8),
    type char(8))""")
    cursor.close()
    connect_to_database.close()
