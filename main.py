import flet as ft
import os
import csv
import configparser


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
            config = configparser.ConfigParser()
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
                                dense=True),
                    )
            #print(section_nav_data)
            section_nav.update()



            #section_content_dataの作成
            for l,object_dict_list in enumerate(objects):
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
                                ]
                            )
                        )
                        if add_string_option:
                            b[-1].cells[3].content.options.append(ft.dropdown.Option("文字"))
                    a.append(b)   
                section_content_data_list.append(a)
                #print(section_content_data_list)
        

        if file_extension == ".csv":
            nonlocal csv_path
            csv_path = file_path
            with open(file=file_path,mode="r", newline='') as f:
                reader = csv.reader(f)
                data = list(reader)
            data_columns = []
            data_rows=[]
            #print(data)
            for column in data[0]:
                data_columns.append(ft.DataColumn(ft.Text(column)))
            for row in data[1:]:
                data_row = ft.DataRow()
                for value in row:
                    data_row.cells.append(ft.DataCell(ft.Text(value)),)
                data_rows.append(data_row)

            csv_table.columns = data_columns
            csv_table.rows = data_rows
            csv_table.update()

    def pick_file_write_result(e: ft.FilePickerResultEvent):
        file_path = e.path
        print(config)
        merged_config = exo_edit.merge_config(config,section_content_data_list,csv_path)

        with open(file_path, 'w') as configfile:
            # 設定をファイルに書き込む
            merged_config.write(configfile, space_around_delimiters=False)

    #表示を変えるイベント群
    nav_folus_now = 0
    def change_section(n):
        nonlocal nav_folus_now
        nav_folus_now = n
        temp = section_content_data_list[nav_folus_now]
        section_content.rows = [item for sublist in temp for item in sublist]
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
                    "Pick files",
                    icon=ft.icons.FILE_OPEN,
                    on_click=lambda _: filepicker.pick_files(allow_multiple=False,allowed_extensions =["exo","csv"])
                )
    #write button
    filepicker_write = ft.FilePicker(on_result=pick_file_write_result)
    write_button = ft.ElevatedButton(
                    "Save files",
                    icon=ft.icons.SAVE,
                    on_click=lambda _: filepicker_write.save_file(allowed_extensions=["exo"])
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
            ft.DataColumn(ft.Text("挿入",width=80),tooltip="選択して任意の値を入力"),
            ft.DataColumn(ft.Text("挿入",width=200),tooltip="選択して任意の値を入力"),
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
        ft.Row([read_button,write_button]),
        ft.Row([
            section_nav,
            ft.VerticalDivider(width=1),
            section_content_box,
            csv_table_box,
            ],
            expand=True,) 
    )

ft.app(target=main)