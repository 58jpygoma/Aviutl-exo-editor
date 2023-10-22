import flet as ft
import os
import csv
import configparser
import re


import exo_edit

def main(page: ft.Page):
    csv_path = None
    config = None
    

    def pick_file_result(e: ft.FilePickerResultEvent):
        file_path = e.files[0].path
        file_extension = os.path.splitext(file_path)[1]

        #section_navオブジェクトとcontentのリストを作る
        if file_extension == ".exo":
            #初期化
            section_nav_data.clear()
            section_content_data_list.clear()
            section_content_data.clear()

            nonlocal config
            config = configparser.ConfigParser(interpolation = None)
            # 大文字を区別する
            config.optionxform = str
            config.read(file_path)

            #print(config)

            count=0 #section[0.0][0.1]...のカウンタ
            objects = [] #オブジェクトごとにsectionをまとめたリスト
            for n,section in enumerate(config.sections()):

                if n == 0:
                    #data_ini.append([sec_info])
                    object_sections =[]
                elif int(float(section)) == count:
                    object_sections.append(dict(config[section]))
                elif int(float(section)) != count:
                    objects.append(object_sections)
                    object_sections =[]
                    object_sections.append(dict(config[section]))
                    count += 1
                if n == len(config.sections()) - 1:
                    objects.append(object_sections)
                    #print(objects)

                
            #section_nav_dataの作成
            for n,object_dict_list in enumerate(objects):
                object_dict = {}
                for d in reversed(object_dict_list):
                    object_dict.update(d)
                
                name = object_dict['_name']
                layer = object_dict['layer']
                while len(layer) < 4:
                    layer = " " + layer
                section_nav_data.append(
                    ft.ListTile(title=ft.Text(f"{layer} : {name}"),
                                on_click =lambda _,n=n: change_section(n), 
                                dense=True,
                                selected=True if nav_folus_now == n else False),
                    )
            #print(section_nav_data)
            section_nav.update()



            #section_content_dataの作成
            for l,object_dict_list in enumerate(objects):
                color = 0
                a = []
                for m,object_dict in enumerate(object_dict_list):
                    b = []    
                    for n,(key, value) in enumerate(object_dict.items()):
                        if len(value) == 4096 and key == "text":
                            value = exo_edit.byt_to_str(value)
                            add_string_option = True
                        else:
                            add_string_option = False
                        b.append(
                            ft.DataRow(
                                cells =[
                                    ft.DataCell(ft.Text(key)),
                                    ft.DataCell(ft.Text(value)),
                                    ft.DataCell(ft.TextField(
                                        keyboard_type= "NUMBER",
                                        on_focus=lambda _,l=l,m=m,n=n:csv_input_focus(l,m,n,2)
                                    )),
                                    ft.DataCell(
                                        content=(ft.Dropdown(
                                            options=[
                                                ft.dropdown.Option("数字"),
                                                ft.dropdown.Option("文字"),
                                                ft.dropdown.Option(" ")  
                                            ],
                                            border="NONE",
                                            on_focus=lambda _,l=l,m=m,n=n:csv_input_focus(l,m,n,3)
                                        ))
                                    ),
                                    ft.DataCell(
                                        ft.TextField(
                                            keyboard_type= "NUMBER",
                                            on_focus=lambda _,l=l,m=m,n=n:csv_input_focus(l,m,n,4)
                                        ),
                                    ),
                                ],
                                color = ft.colors.SURFACE if color == 0 else ft.colors.GREY_200

                            )
                        )
                    a.append(b)
                    color = (color+1)%2
                section_content_data_list.append(a)
                #print(section_content_data_list)
        

        if file_extension == ".csv":
            nonlocal csv_path
            csv_path = file_path
            with open(file_path, 'rb') as file:
                data = file.read(4)
                if data[:3] == b'\xEF\xBB\xBF':  # UTF-8のBOMを検出
                    csv_encoding = 'utf-8-sig'
                else:
                    csv_encoding = 'utf-8'
            with open(file=file_path,mode="r", newline='',encoding=csv_encoding) as f:
                reader = csv.reader(f)
                data = list(reader)
            data_columns = [ft.DataColumn(ft.Text("列番号")),ft.DataColumn(ft.Text("列名")),ft.DataColumn(ft.Text("1行目")),ft.DataColumn(ft.Text("2行目"))]
            data_rows=[]
            #print(data)
            for n,column in enumerate(data[0]):
                data_row = ft.DataRow()
                data_row.cells.extend([ft.DataCell(ft.Text(n+1)),ft.DataCell(ft.Text(column)),ft.DataCell(ft.Text(data[1][n])),ft.DataCell(ft.Text(data[2][n]))])
                data_rows.append(data_row)


            # for column in data[0]:
            #     data_columns.append(ft.DataColumn(ft.Text(column)))
            # for row in data[1:]:
            #     data_row = ft.DataRow()
            #     for value in row:
            #         data_row.cells.append(ft.DataCell(ft.Text(value)),)
            #     data_rows.append(data_row)

            csv_table.columns = data_columns
            csv_table.rows = data_rows
            csv_table.update()

    def pick_file_write_result(e: ft.FilePickerResultEvent):
        file_path = e.path
        if not file_path.endswith(".exo"):
            file_path += ".exo"
        print(config)
        merged_config = exo_edit.merge_config(config,section_content_data_list,csv_path)

        with open(file_path, 'w') as configfile:
            # 設定をファイルに書き込む
            merged_config.write(configfile, space_around_delimiters=False)

    #一括入力
    def close_filler(e):
        page.dialog = filler
        filler.open = False
        page.update()
    ft_fill_terms =[ft.DataRow([ft.DataCell(ft.TextField(width=90)),ft.DataCell(ft.TextField(width=90))],),
                    ft.DataRow([ft.DataCell(ft.TextField(width=90)),ft.DataCell(ft.TextField(width=90))],),
                    ft.DataRow([ft.DataCell(ft.TextField(width=90)),ft.DataCell(ft.TextField(width=90))],),
                    ]
    ft_fill_terms_m = [ft.DataRow([ft.DataCell(ft.TextField()),ft.DataCell(ft.TextField()),ft.DataCell(ft.TextField())],),
                       ft.DataRow([ft.DataCell(ft.TextField()),ft.DataCell(ft.TextField()),ft.DataCell(ft.TextField())],),
                       ft.DataRow([ft.DataCell(ft.TextField()),ft.DataCell(ft.TextField()),ft.DataCell(ft.TextField())],),
                       ]
    ft_fill_key = ft.TextField(hint_text="挿入する項目")
    ft_fill_value = ft.TextField(hint_text="挿入する文字")
    ft_fill_csv_column = ft.TextField(hint_text=".csvの列番号 {layer}でレイヤー番号を指定できる（{layer}-4）")
    ft_fill_insert_type = ft.Dropdown(options=[ft.dropdown.Option("数字"),ft.dropdown.Option("文字"),ft.dropdown.Option(" ")],hint_text="入力タイプ")

    def fill_terms(e):
        fill_list =[]
        
        for ft_row in ft_fill_terms:# 各ft_row
            fill_name = ft_row.cells[0].content.value
            fill_term = ft_row.cells[1].content.value
            if fill_name != "":
                fill_list.append([fill_name,fill_term])
        for ft_row in ft_fill_terms_m:# 各ft_row
            fill_name = ft_row.cells[0].content.value
            fill_term_min = ft_row.cells[1].content.value
            fill_term_max = ft_row.cells[2].content.value
            if fill_name != "":
                fill_list.append([fill_name,fill_term_min,fill_term_max])
        for _, section_content_data in enumerate(section_content_data_list):#オブジェクト　1: テキストとか
            fill_flag = 0

            for n,section in enumerate(section_content_data):# 0.0 0.1 とか
                
                for ft_row in section:# 各ft_row
                    
                    for n,ft_data_cell in enumerate(ft_row.cells):#それぞれの要素_text x とか
                        content = ft_data_cell.content
                        #print(content.value)
                        if n == 0:#項目名
                            element_name = content.value
                            for term in fill_list:
                                #項目名のみ埋まっている場合
                                if term[0] == element_name and term[1] == "":
                                    fill_flag += 1
                            if element_name == ft_fill_key.value:
                                fill_content_word = ft_row.cells[4].content
                                fill_content_option = ft_row.cells[3].content
                                fill_content_csv = ft_row.cells[2].content
                            if element_name == "layer":
                                layer = ft_row.cells[1].content.value
                        elif n == 1:#初期値
                            first_value = content.value
                            for term in fill_list:
                                #項目名のみ埋まっている場合
                                if term[0] == element_name and term[1] != "" :
                                    if len(term)==2 and term[1] == first_value:
                                        fill_flag += 1
                                    if len(term)==3:
                                        try:
                                            min = float(term[1])
                                            max = float(term[2])
                                            if float(first_value)>= min and float(first_value)<=max:
                                                fill_flag += 1
                                        except:
                                            pass
            if fill_flag == len(fill_list):
                csv_result=ft_fill_csv_column.value.replace("{layer}",layer)
                if re.match(r'^[\d\s()+\-*/.]*', csv_result):
                    csv_result = eval(csv_result)
                fill_content_word.value = ft_fill_value.value
                fill_content_option.value = ft_fill_insert_type.value
                fill_content_csv.value = csv_result
    filler = ft.AlertDialog(
        modal= False,
        title=ft.Text("一括入力"), 
        content=ft.Column(
            [
                ft_fill_key,
                ft_fill_value,
                ft_fill_csv_column,
                ft_fill_insert_type,
                
                ft.DataTable(
                    expand=1,
                    column_spacing=5,
                    columns=[
                        ft.DataColumn(ft.Text("項目名",width=90)),
                        ft.DataColumn(ft.Text("値",width=90)),
                    ],
                    rows = ft_fill_terms
                ),

                ft.DataTable(
                    expand=1,
                    column_spacing=5,
                    columns=[
                        ft.DataColumn(ft.Text("項目名",width=90)),
                        ft.DataColumn(ft.Text("最小値",width=90)),
                        ft.DataColumn(ft.Text("最大値",width=90)),
                    ],
                    rows = ft_fill_terms_m
                ),
                ft.Text("例えば項目名layer、最小値3、最大値4、項目名_name、値図形、挿入する項目X、値{cell}にすると、初期値が3から4のレイヤーかつ図形のオブジェクトのXに{cell}という値が入る"),
                ft.Text("例えば挿入する項目X、挿入する語句4にすると、すべてのXが4になる"),
            ]
        ),
        actions=[
            ft.TextButton("一括入力", on_click=fill_terms),
            ft.TextButton("閉じる", on_click=close_filler),
        ],
    )
    def open_filler(e):
        page.dialog = filler
        filler.open = True
        page.update()
    

    #表示を変えるイベント群
    nav_folus_now = 0
    def change_section(n):
        nonlocal nav_folus_now
        nav_folus_now = n
        temp = section_content_data_list[nav_folus_now]
        section_content.rows = [item for sublist in temp for item in sublist]
        for i, section in enumerate(section_nav_data):
            if i ==n:
                section.selected = True
            else:
                section.selected = False

        page.update()
    
    
    field_focus_now=[]
    def csv_input_focus(l,m,n,column):
        nonlocal field_focus_now
        field_focus_now = [l,m,n,column]


    
 
    


    #それぞれのオブジェクトを生成
    #csv
    csv_table = ft.DataTable(expand= 1)
    csv_table_box = ft.ListView(expand=1)
    csv_table_box.controls.append(csv_table)
    #open button
    filepicker = ft.FilePicker(on_result=pick_file_result)
    read_button = ft.ElevatedButton(
                    "インポート",
                    icon=ft.icons.FILE_OPEN,
                    on_click=lambda _: filepicker.pick_files(allow_multiple=False,allowed_extensions =["exo","csv"])
                )
    #write button
    filepicker_write = ft.FilePicker(on_result=pick_file_write_result)
    write_button = ft.ElevatedButton(
                    "エクスポート",
                    icon=ft.icons.FILE_DOWNLOAD,
                    on_click=lambda _: filepicker_write.save_file(allowed_extensions=["exo"])
                )
    #fill
    filler_button = ft.ElevatedButton(
                    "一括挿入",
                    icon=ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP,
                    on_click=open_filler,
                )
    #sections
    section_nav_data = []
    section_nav = ft.ListView(
                width=200,
                controls=section_nav_data,        
            )
    section_content_data_list = []
    section_content_data = []
    section_content = ft.DataTable(
        expand=1,
        column_spacing=5,
        columns=[
            ft.DataColumn(ft.Text("項目名",width=120),tooltip="項目名=値"),
            ft.DataColumn(ft.Text("初期値",width=90)),
            ft.DataColumn(ft.Text(".csvの列番号",width=90),tooltip=".csvの何列目と置き換えるか"),
            ft.DataColumn(ft.Text("挿入",width=80),tooltip="入力する種類の選択"),
            ft.DataColumn(ft.Text("挿入",width=200),tooltip="{cell},{first}はそれぞれcsvのセルの値と初期値に置換されます。"),
        ],
        rows = [item for sublist in section_content_data for item in sublist]
    )
    section_content_box = ft.ListView(expand=1)
    section_content_box.controls.append(section_content)
    
    page.overlay.append(filepicker)
    page.overlay.append(filepicker_write)

    #キーボードショートカット

    def on_keyboard(e:ft.KeyboardEvent):
        if e.key == "Enter" and e.shift:
            change_section(nav_folus_now+1)
            section_content_data_list[nav_folus_now][field_focus_now[1]][field_focus_now[2]].cells[field_focus_now[3]].content.focus()
        elif e.key == "Enter":
            print(field_focus_now)
            if field_focus_now[2]+1 >= len(section_content_data_list[field_focus_now[0]][field_focus_now[1]]):
                section_content_data_list[field_focus_now[0]][field_focus_now[1]+1][0].cells[field_focus_now[3]].content.focus()
            else:
                section_content_data_list[field_focus_now[0]][field_focus_now[1]][field_focus_now[2]+1].cells[field_focus_now[3]].content.focus()
    page.on_keyboard_event = on_keyboard

    page.add(
        ft.Row([read_button,write_button,filler_button]),
        ft.Row([
            section_nav,
            ft.VerticalDivider(width=1),
            section_content_box,
            csv_table_box,
            ],
            expand=True,) 
    )

ft.app(target=main)