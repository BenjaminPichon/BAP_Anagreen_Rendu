# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 14:55:43 2018

@author: nicolamartin
"""

from bokeh.models.widgets import DataTable, TableColumn


def table(source, column_list, width=200):
    columns = []
    for col in column_list:
        columns.append(TableColumn(field=col, title=col))

    return DataTable(source=source, columns=columns, width=width, selectable=True)
