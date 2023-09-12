import os
import csv
import configparser
import copy
import re
import flet as ft


def merge_config(config,section_content_data_list,csv_path):

    element_name = None
    element_value = None
    element_column = None
    element_insert_type = None
    element_insert_value = None

    #configの分離
    #print(config.sections())
    config_head = copy.deepcopy(config)
    config_body = copy.deepcopy(config)
    for section_name in config.sections():
        if section_name == "exedit":
            continue
        config_head.remove_section(section_name)
    config_body.remove_section(config.sections()[0])
    output_config = copy.deepcopy(config_head)

    #lengthの取得
    end_frame = 0
    start_frame = float('inf')
    for section_name in config_body.sections():
        try:
            start = int(config_body[section_name]["start"])
            start_frame = min(start,start_frame)
            end = int(config_body[section_name]["end"])
            end_frame = max(end,end_frame)
        except:
            pass
    length = end_frame -int(start_frame) + 1

    #print(config_body.sections())
    #csvの読み込み
    with open(file=csv_path,mode="r", newline='') as f:
                reader = csv.reader(f)
                header = next(reader)
                data = list(reader)

    #書き換え
    csvlen = len(data)
    i = 0
    for l in range(csvlen):
        for _, section_content_data in enumerate(section_content_data_list):#オブジェクト　1: テキストとか
            for n,section in enumerate(section_content_data):# 0.0 0.1 とか
                replace_dict = {}
                if n == 0 :
                    section_name = str(i)
                else:
                    section_name = f"{i}.{n-1}"
                
                for ft_row in section:# 各ft_row
                    for n,ft_data_cell in enumerate(ft_row.cells):#それぞれの要素_text x とか
                        content = ft_data_cell.content
                        #print(content.value)
                        if n == 0:#項目名
                            element_name = content.value
                        elif n == 1:#初期値
                            element_value = content.value
                        elif n == 2:#csvの列番号
                            try:
                                element_column = int(content.value)
                            except:
                                element_column = None
                        elif n == 3:#挿入の種類選択
                            element_insert_type = content.value
                        elif n == 4:#挿入する句
                            element_insert_value = content.value
                        
                    #print(element_name,element_value,element_column)
                    #print(type(element_name))
                    #何も入力しなくてもstart,endだけは書き換える
                    if element_name == "start" or element_name ==  "end":
                        element_value = str(int(element_value)+length*l)

                    #テキストは変換する
                    if element_name == "text":
                        element_value = str_to_byt(element_name)
                    #列番号があれば書き換えを行う
                    #print(element_column)
                    if element_column != None:
                        if element_name == "text":
                            element_value = str_to_byt(data[l][element_column-1])
                        else:
                            element_value = str(data[l][element_column-1])
                    if element_insert_type == "文字":
                        element1 = byt_to_str(element_value)
                        element_value = element_insert_value.replace("{text}",element1)
                        element_value = str_to_byt(element_value)
                    if element_insert_type == "数字":
                        #桁数を判定
                        if "." in element_value:
                            decimal_places = len(element_value.split(".")[1])
                        else:
                            decimal_places = 0

                        element_value = element_insert_value.replace("{number}",element_value)
                        if re.match(r'^[\d\s()+\-*/.]*', element_value):
                            result = eval(element_value)
                        element_value=str(round(result,decimal_places))

                    replace_dict[element_name] = element_value
                    
                
                output_config[section_name]=replace_dict
            i +=1

    return output_config

def byt_to_str(text):
    return bytes.fromhex(text).decode('utf-16-le').replace("\x00","")
def str_to_byt(text):
    short_byt = text.encode("utf-16-le").hex()
    while len(short_byt)<4096:
        short_byt += "0"
    return(short_byt)