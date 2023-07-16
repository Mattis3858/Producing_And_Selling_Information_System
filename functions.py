import json
import pandas as pd
import numpy as np
from datetime import datetime,timezone,timedelta
from ArticutAPI import Articut
from pprint import pprint
# with open('果乾.json') as f:
fruit = r'果乾.json'

# with open('KNOWLEDGE_bankTW.json') as f:
bank = r'KNOWLEDGE_bankTW.json'


username = "wenyeh6@gmail.com" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "vBn1h3VsMIg$E!f=iiqIsfzsPc-ByeI"

# 用是否有address來區分是訂購表單還是付款表單 --> 分為三種情況
def order_payment_classifier(articut, message):
  count = 0
  result = 0

  resultDICT = articut.parse(message)
  message_pos_list = resultDICT['result_pos']
  zipped_message_pos_list = ''.join(message_pos_list)

  if(zipped_message_pos_list.find('KNOWLEDGE_addTW') != -1): #判斷為order訊息
    result = 1
    count += 1
  if(zipped_message_pos_list.find('KNOWLEDGE_currency') != -1): #判斷為pay訊息
    result = 2
    count += 1
  if(count != 1): #表示數據異常，請求重新輸入
    result = 3
  
  return result

# Def 農民設定訂單表格
# def 將農民input轉化為list型態

# 將使用者input轉化為list型態
def input_to_list(columns_input):
  vocabulary =''
  word_list = []

  for i in range(len(columns_input)):
    if(columns_input[i]!= ','):
      vocabulary += columns_input[i]
    else:
      word_list.append(vocabulary)
      vocabulary = ''
    
    if(i==(len(columns_input)-1)):
      word_list.append(vocabulary)

  return word_list

# def 將input_list轉換為 order_table
# 將input_list轉換為 order_table
def input_list_to_df(columns_set_statement, table_id):
  # 先將input_list 加上必要欄位：訂單編號, 付款與否, 銀行名稱, 末五碼
  input_list = columns_set_statement
  input_list.insert(0, '訂單編號')
  input_list.insert(1, '下單時間')
  input_list.insert(2, '付款與否')
  input_list.insert(len(input_list), '銀行名稱')
  input_list.insert(len(input_list), '末五碼')

  # 輸入本次活動編號
  activity_id = input_to_list(table_id)

  # def 將使用者輸入的list轉化為訂單表格
  order_table = pd.DataFrame(columns=input_list)

  # 生成100筆資料
  for order_num in range(10):
    if(order_num+1 < 10):
      order_detail_num = '0' + '0' + f'{(order_num+1)}'
    if(order_num+1 >= 10 and order_num+1 < 100):
      order_detail_num = '0' + f'{(order_num+1)}'
    if(order_num+1 >= 100):
      order_detail_num = f'{(order_num+1)}'

    activity = activity_id[0] + order_detail_num
    order_table.loc[int(order_num), '訂單編號'] = activity

  return order_table

# def 品項設定並轉化為表格

# 將使用者輸入的品項存取並轉化為表格
def item_and_price_input_and_df(order_table, table_items, table_units, table_prices):
  item_and_price_columns = []
  
  #輸入品項與價格
  for i in range(len(table_items)):
    item = table_items[i]
    unit = table_units[i]
    price = table_prices[i]
      

    #將兩個list加入訂單表格中
    item_and_price = item + "(" + f'{unit}' + ')' + f'{price}'
    item_and_price_columns.append(item_and_price)
    order_table[item_and_price] = np.nan


  # 建立品項、價格對照表
  item_price_table = pd.DataFrame({
      '訂購產品': table_items,
      '單位': table_units,
      '價格': table_prices
  })

  return order_table, item_price_table, item_and_price_columns

  # Def line訊息斷詞
  # def 訂購訊息斷詞

  # def 訊息斷詞設定、輸入
  # lv2為普通段詞
def articut_lv2(username, apikey):
  articut = Articut(username, apikey,level='lv2')
  return articut

# lv3 為極致段詞
def articut_lv3(username, apikey):
  detailed_articut = Articut(username, apikey,level='lv3')
  return detailed_articut

# 將訂購訊息輸入，用ARTICUT進行拆解
def order_message_input(message, articut, dict_defined_response):
  # 選擇是否要輸入自定義字典
  if((dict_defined_response=='')==True):
    resultDICT = articut.parse(message)
  else:
    resultDICT = articut.parse(message, userDefinedDictFILE=dict_defined_response)

  result_obj_dic = resultDICT['result_obj']
  return result_obj_dic

# def 姓名、電話、地址
# 截取姓名、電話、地址
def name_phone_address_lister(result_obj_dic):
  name_list = []
  phone_list = []
  address_list = []

  for i in range(len(result_obj_dic)):
    for j in range(len(result_obj_dic[i])):
      pos = result_obj_dic[i][j].get('pos')
      if((not name_list)==True & (pos=='ENTITY_person')==True):
        name = result_obj_dic[i][j].get('text')
        name_list.append(name)
      if((not phone_list)==True & (pos=='ENTITY_num')==True):
        splited_phone = result_obj_dic[i][j].get('text').split(' ')[1]
        phone_list.append(splited_phone)
      if((not address_list)==True & (pos=='KNOWLEDGE_addTW')==True):
        address = result_obj_dic[i][j].get('text')
        address_list.append(address)
  
  # print(name_list)
  # print(phone_list)
  # print(address_list)

  return name_list, phone_list, address_list


# def 截取品項、數量
# 擷取品項數量
def item_classifier_indexer(result_obj_dic):
  noun_index_list=[]
  classifier_index_list = []

  for i in range(len(result_obj_dic)):
    for j in range(len(result_obj_dic[i])):
      pos = result_obj_dic[i][j].get('pos')
      #將oov與classifier找到其存在index
      if(pos == 'ENTITY_oov'):
        noun_index_list.append([i,j])
      if(pos == 'ENTITY_nouny'):
        noun_index_list.append([i,j])
      if(pos == 'ENTITY_nounHead'):
        noun_index_list.append([i,j])
      if(pos == 'UserDefined'):
        noun_index_list.append([i,j])
      if(pos == 'ENTITY_classifier'):
        classifier_index_list.append([i,j])

  # print(noun_index_list)
  # print(classifier_index_list)
  
  return noun_index_list, classifier_index_list

#將兩個list加入訂單表格中，形成訂購表格
def order_items_num(detailed_articut, noun_index_list, classifier_index_list, result_obj_dic):
  oov_list = []
  classifier_list = []
  num_list = []
  unit_list = []

  len_noun_or_classifier = min(len(noun_index_list), len(classifier_index_list))

  for i in range(len_noun_or_classifier):
    oov_index_i = noun_index_list[i][0]
    oov_index_j = noun_index_list[i][1]
    oov = result_obj_dic[oov_index_i][oov_index_j].get('text').strip()
    oov_list.append(oov)

    classifier_index_i = classifier_index_list[i][0]
    classifier_index_j = classifier_index_list[i][1]
    clssifier = result_obj_dic[classifier_index_i][classifier_index_j].get('text')
    classifier_list.append(clssifier)


    #對數量(amount)進行極致斷詞
    amount_dict = detailed_articut.parse(classifier_list[i])
    amount_num = list(amount_dict['number'].values())[0]
    num_list.append(amount_num)

    #對單位(unit)進行極致斷詞
    unit_dict = detailed_articut.parse(classifier_list[i])
    unit = list(unit_dict['unit'].values())[0]
    unit_list.append(unit)


  # 建立訂購品項、數量、單位對照表
  order_item_amount_table = pd.DataFrame({
    '訂購產品': oov_list,
    '數量及單位': classifier_list,
    '數量': num_list,
    '單位': unit_list
  })

  return order_item_amount_table

# def 備註訊息(其他訊息)截取
# 備註訊息(其他訊息)截取
def other_message_fuc(result_obj_dic, order_message, noun_index_list, classifier_index_list):

  # 先設定基準index_list --> 比較小的當作基準
  if(len(noun_index_list) > len(classifier_index_list)):
    index_list = classifier_index_list
    min_len = len(classifier_index_list)
  else:
    index_list = noun_index_list
    min_len = len(noun_index_list)
  
  #計算index
  first_index = index_list[len(index_list)-1][0]
  max_index = max(noun_index_list[min_len-1][1], classifier_index_list[min_len-1][1])

  last_str = result_obj_dic[first_index][max_index].get('text')

  #擷取訊息
  splited_message = order_message.split(last_str)
  other_message = splited_message[len(splited_message)-1]
  # print('other_message:',other_message )
  
  return other_message

# def 系統取得當前時間
# 抓取系統現在時間
def now_time_generator():
  dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
  dt2 = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
  time = dt2.strftime("%Y-%m-%d %H:%M:%S")
  return time

# def 組合成大table
# 找出空資料列，才可以存放資料
def find_available_row_index(order_table):

  for i in range(len(order_table)):
    available_index = 0
    try:
      if((pd.Series(order_table.loc[i, '姓名']).isnull()[0])==True):
        available_index = i
        break
    except:
      if((pd.Series(order_table.loc[f'{i}', '姓名']).isnull()[0])==True):
        available_index = f'{i}'
        break

  # for i in range(len(order_table)):
  #   if((pd.Series(order_table.loc[i, '姓名']).isnull()[0])==True):
  #     available_index = i
  #     break
  # if(len(order_table)==100):
  #   available_index = 0
  # else:
  #   available_index = len(order_table)

  return available_index

# 將品項以外的欄位填入表格
def fill_table(available_index, order_table, name_list, phone_list, address_list, time, other_message):
  order_table.loc[available_index, '姓名'] = name_list[0]
  order_table.loc[available_index, '電話'] = phone_list[0]
  order_table.loc[available_index, '住址'] = address_list[0]
  order_table.loc[available_index, '下單時間'] = time
  order_table.loc[available_index, '備註'] = other_message
  return order_table

# def 組合訂購品項
# 將品項、數量進行組合，並且計算金額
def order_items_fill_table(order_table, available_index, item_price_table, order_item_amount_table):

  set_item_unit_table_list = []
  set_item_unit_price_table_list = []

  for i in range(len(item_price_table)):
    try:
      set_item = item_price_table.loc[f'{i}', '訂購產品']
      set_unit = item_price_table.loc[f'{i}', '單位']
      set_price = item_price_table.loc[f'{i}', '價格']
    except:
      set_item = item_price_table.loc[i, '訂購產品']
      set_unit = item_price_table.loc[i, '單位']
      set_price = item_price_table.loc[i, '價格']

    item_unit_str = set_item + '(' + set_unit + ')'
    set_item_unit_table_list.append(item_unit_str)

    item_unit_price_str = set_item + '(' + set_unit + ')' + f'{set_price}'
    set_item_unit_price_table_list.append(item_unit_price_str)

  # print(set_item_unit_table_list)
  # print(set_item_unit_price_table_list) 

  # 填滿wrong_msg 
  wrong_msg_list = []
  columns_list = order_table.columns.tolist()
  complete_name = ''

  for i in range(len(order_item_amount_table)):
    try:
      ms_item = order_item_amount_table.loc[i, '訂購產品'].strip()
      ms_num = order_item_amount_table.loc[i, '數量']
      ms_unit = order_item_amount_table.loc[i, '單位'].strip()
      ms_num_unit = order_item_amount_table.loc[i, '數量及單位'].strip()
    except:
      ms_item = order_item_amount_table.loc[f'{i}', '訂購產品'].strip()
      ms_num = order_item_amount_table.loc[f'{i}', '數量']
      ms_unit = order_item_amount_table.loc[f'{i}', '單位'].strip()
      ms_num_unit = order_item_amount_table.loc[f'{i}', '數量及單位'].strip()
    ms_item_unit_str = ms_item + '(' + ms_unit + ')' #蘋果(包)

    #若訊息中提及的品項正確，則列進訂購表中
    if(ms_item_unit_str in set_item_unit_table_list): # 訊息品項正確
      complete_name = ''
      for j in range(len(set_item_unit_table_list)): #先找到在set_item_unit_table_list的哪裡
        if(set_item_unit_table_list[j] == ms_item_unit_str):
          complete_name = set_item_unit_price_table_list[j] #從set_item_unit_price_table_list呼叫出完整名字
          break
      
      #將完整訂購品項等輸入column找
      for k in range(len(columns_list)):
        try:
          if(columns_list[k]==complete_name):
            order_table.iloc[int(available_index), k] = ms_num
            break
        except:
          if(columns_list[k]==complete_name):
            order_table.iloc[available_index, k] = ms_num
            break
    #若訊息中錯 誤，則列出無法辨識的品項訊息
    else:
      wrong_msg = ms_item + '(' + ms_num_unit + ')'
      wrong_msg_list.append(wrong_msg)

  #   print(ms_item_unit_str)


  # 計算本次訂購總價格
  res = pd.merge(order_item_amount_table, item_price_table, how='inner', on=['訂購產品','單位'])
  #將價格、數量型態轉換為int
  res['數量'] = res['數量'].astype(int)
  res['價格'] = res['價格'].astype(int)
  #執行計算
  res['總價'] = res['數量'] * res['價格']
  #併入大訂購表中
  order_table.loc[available_index, '總價'] = res['總價'].sum()


  # print('wrong_msg_list:', wrong_msg_list)
  return order_table, wrong_msg_list

# def 付款資訊斷詞
# def 姓名、電話、銀行、末五碼、金額
# 使用者輸入pay_message的def
def pay_message_input(message, articut):
  # pay_message = input('請輸入付款訊息：')
  pay_message = message
  resultDICT = articut.parse(message, userDefinedDictFILE = bank)
  result_obj_dic = resultDICT['result_obj']
  return pay_message, result_obj_dic

# 取出付款訊息的姓名、電話、銀行、末五馬、轉帳金額
def pay_message_lister(result_obj_dic, detailed_articut):
  name_list = []
  phone_list = []
  text_list = []
  count = -1
  start = ''
  start_count = False


  for i in range(len(result_obj_dic)):
    for j in range(len(result_obj_dic[i])):
      pos = result_obj_dic[i][j].get('pos')
      if((not name_list)==True & (pos=='ENTITY_person')==True):
        name = result_obj_dic[i][j].get('text')
        name_list.append(name)
      if((not phone_list)==True & (pos=='ENTITY_num')==True):
        splited_phone = result_obj_dic[i][j].get('text').split(' ')[1]
        phone_list.append(splited_phone)
      
      # 把電話到currency之間的訊息擷取下來，列為bank
      if(pos == 'ENTITY_num'):
        ENTITY_num_index = [i,j]
        if(count==-1):
          start_index = [i,j]
          start = 'ENTITY_num'
          start_count = True
        else:
          start_count = False
          break

      if(pos == 'KNOWLEDGE_currency'):
        KNOWLEDGE_currency_index = [i,j]
        if(count==-1):
          start_index = [i,j]
          start = 'KNOWLEDGE_currency'
          start_count = True
        else:
          start_count = False
          break
      
      if(start_count == True):
        if(count != -1):
          text = result_obj_dic[i][j].get('text')
          text_list.append(text)
        count += 1

  bank = ''.join(text_list)

  # 把currency用空白切分
  splited_currency = result_obj_dic[KNOWLEDGE_currency_index[0]][KNOWLEDGE_currency_index[1]].get('text').split(' ')
  bank_account = splited_currency[1]
  payment = splited_currency[2]
  int_payment = list(detailed_articut.parse(payment)['number'].values())[0]
  return name_list, phone_list, bank, bank_account, int_payment

# def 找出空資料列，回傳index
# 找出顧客關係表的空資料列，可以填入新會員
def find_available_row_index_customer_df(order_table):
  available_index = 0

  for i in range(len(order_table)):
    available_index = 0
    try:
      if((pd.Series(order_table.loc[i, '*會員姓名']).isnull()[0])==True):
        available_index = i
        break
    except:
      if((pd.Series(order_table.loc[f'{i}', '*會員姓名']).isnull()[0])==True):
        available_index = f'{i}'
        break

  return available_index

# def line訊息輸入總fun
def line_message_enter(message, articut, detailed_articut, order_table, item_price_table, item_and_price_columns, customer_df, stastics, inventory_table, dict_input):
  #設定時間
  time = now_time_generator()

  #開始判斷
  if(order_payment_classifier(articut, message) == 1): #代表是訂購訊息
    # 設定訂購物品名稱字典
    if dict_input=='果乾':
      order_message_input_result = order_message_input(message, articut, fruit)
    else:
      dict_defined_response = ''
      order_message_input_result = order_message_input(message, articut, dict_defined_response)

    result_obj_dic = order_message_input_result

    noun_index_list = item_classifier_indexer(result_obj_dic)[0]
    classifier_index_list = item_classifier_indexer(result_obj_dic)[1]
    other_message = other_message_fuc(result_obj_dic, message, noun_index_list, classifier_index_list)
    available_index = find_available_row_index(order_table)
    order_item_amount_table = order_items_num(detailed_articut, noun_index_list, classifier_index_list, result_obj_dic)

    name_phone_address_list = name_phone_address_lister(result_obj_dic)
    name_list = name_phone_address_list[0]
    phone_list = name_phone_address_list[1]
    address_list = name_phone_address_list[2]

    order_table = fill_table(available_index, order_table, name_list, phone_list, address_list, time, other_message)

    order_items_fill_table_result = order_items_fill_table(order_table, available_index, item_price_table, order_item_amount_table)
    order_table = order_items_fill_table_result[0]
    wrong_msg_list = order_items_fill_table_result[1]

    
    # *********************************************************************
    # 第一個是order_table(訂購表格), 第二個是wrong_msg_list，就是可以顯示在網頁上，讓小農知道無法辨識的訊息內容
    return order_table, wrong_msg_list
    # *********************************************************************D



  # 若為payment
  elif(order_payment_classifier(articut, message) == 2): #代表是付款訊息
    pay_message_input_result = pay_message_input(message, articut)
    result_obj_dic = pay_message_input_result[1]

    pay_message_list = pay_message_lister(result_obj_dic, detailed_articut)
    name_list = pay_message_list[0]
    phone_list = pay_message_list[1]
    bank = pay_message_list[2]
    bank_account = pay_message_list[3]
    int_payment = pay_message_list[4]

    #找表格內對應的index
    paid_index = order_table[order_table['姓名']==name_list[0]][order_table['電話']==phone_list[0]].index.tolist()
    if(paid_index != []): #代表付款信息打對
      order_table.loc[paid_index, '付款與否'] = '已付款'
      order_table.loc[paid_index, '付款登陸時間'] = time
      order_table.loc[paid_index, '銀行名稱'] = bank
      order_table.loc[paid_index, '末五碼'] = bank_account
      order_table.loc[paid_index, '付款金額'] = int_payment
      payment_result = order_table
    else:
      payment_result ='訊息錯誤，找不到此人、電話，請再輸入一次！'


    # 付完款之後，將已付款訂單編號納入顧客關係表中
    customer_df['歷史訂單編號']=customer_df['歷史訂單編號'].astype('object')

    member_or_not = customer_df[customer_df['*會員姓名']==name_list[0]][customer_df['*會員電話']==phone_list[0]].index.tolist()
    if(member_or_not != []):#代表是member
      member_index = customer_df[customer_df['*會員姓名']==name_list[0]][customer_df['*會員電話']==phone_list[0]].index.tolist()[0]

      order_id_list = order_table.loc[paid_index,'訂單編號'].tolist()

      for order_id in order_id_list:
        customer_df.at[str(member_index), '歷史訂單編號'].append(order_id)

    else:
      available_index = find_available_row_index_customer_df(customer_df)
      try:
        customer_df.loc[str(available_index), '*會員姓名'] = name_list[0]
        customer_df.loc[str(available_index), '*會員電話'] = phone_list[0]
        customer_df.loc[str(available_index), '初次加入時間'] = time
        customer_df.at[str(available_index), '歷史訂單編號'] = []
      except:
        customer_df.loc[available_index, '*會員姓名'] = name_list[0]
        customer_df.loc[available_index, '*會員電話'] = phone_list[0]
        customer_df.loc[available_index, '初次加入時間'] = time
        customer_df.at[available_index, '歷史訂單編號'] = []
      member_index = customer_df[customer_df['*會員姓名']==name_list[0]][customer_df['*會員電話']==phone_list[0]].index.tolist()[0]
      order_id_list = order_table.loc[paid_index,'訂單編號'].tolist()

      for order_id in order_id_list:
        customer_df.at[str(member_index), '歷史訂單編號'].append(order_id)

      # 取得住址 --> 回去order_table找此訂購人最後一次的地址
      newest_id = order_table[order_table['姓名']==name_list[0]][order_table['電話']==phone_list[0]].tail(1).index.tolist()
      newest_address = order_table.loc[newest_id, '住址'].values[0]

      try:
        customer_df.loc[str(available_index), '地址'] = newest_address
      except:
        customer_df.loc[available_index, '地址'] = newest_address
    # 銷量統計表更新
    stastics = fill_stastics(stastics, item_and_price_columns, order_table, item_price_table)

    # 庫存管理表更新
    inventory_table = order_edit_inventory(order_table, inventory_table, item_and_price_columns)



    # *********************************************************************
    # 第一個是order_table(訂購表格), 第二個是顧客關係表
    return payment_result, customer_df ,stastics ,inventory_table
    # *********************************************************************



  else:
    return '這裡錯誤喔！訊息錯誤！請再確認一次！'
    # *********************************************************************

# def 設定此訂單活動表格
# 設定參數
def setting_order_table(columns_set_statement, table_id, table_items, table_units, table_prices):
  result_table = item_and_price_input_and_df(input_list_to_df(columns_set_statement, table_id), table_items, table_units, table_prices)
  order_table = result_table[0]
  item_price_table = result_table[1]
  item_and_price_columns = result_table[2]

  return order_table, item_price_table, item_and_price_columns

# def 建立顧客關係表
# 建立顧客關係空表
def setting_customer_table():
  customer_df = pd.DataFrame({
    '會員號碼': [],
    '*會員姓名': [],
    '*會員電話': [],
    '地址': [],
    '歷史訂單編號':[],
    '初次加入時間':[],
    '備註':[] 
  })

  # 生成100筆資料
  for customer_num in range(1,101):
    if((customer_num) < 10):
      customer_id = '0' + f'{(0)}' + f'{(customer_num)}'
    if(customer_num >= 10 and customer_num < 100):
      customer_id = '0' + f'{(customer_num)}'
    if(customer_num >= 100):
      customer_id = f'{(customer_num)}'

    customer_df.loc[customer_num-1, '會員號碼'] = customer_id


  customer_df['歷史訂單編號']=customer_df['歷史訂單編號'].astype('object')

  return customer_df

# def 銷量統計
# 設定銷量統計表格
def setting_stastics(item_and_price_columns):
  stastics = pd.DataFrame({
    '項目': ['件數', '總金額'],
  })

  stastics[item_and_price_columns] = np.nan

  return stastics

# 有付款才會登入到銷量統計中
def fill_stastics(stastics, item_and_price_columns, order_table, item_price_table):
  for i in range(len(item_and_price_columns)):
    # 件數
    item_and_price_column = item_and_price_columns[i]
    amount = order_table[order_table['付款與否']=='已付款'][item_and_price_column].sum()
    stastics.loc['0', item_and_price_column] = amount

    # 價格
    price = item_price_table.loc[f'{i}', '價格']
    total_price = int(price) * int(amount)
    stastics.loc['1', item_and_price_column] = total_price

  return stastics

# def 庫存管理表
def setting_invetory_table(item_and_price_columns):
  inventory_table = pd.DataFrame({
    '項目': ['件數', '水位狀況'],
  })
  inventory_table[item_and_price_columns] = np.nan


  # 基本的庫存設定，預設庫存為50
  for i in range(len(item_and_price_columns)):
    item_and_price_column = item_and_price_columns[i]
    
    inventory_table.loc[0, item_and_price_column] = 50
    inventory_table.loc[1, item_and_price_column] = '狀態良好'

  return inventory_table

# 使用者手動輸入編輯庫存
def manual_edit_inventory(inventory_table, inventory_edit_message, item_and_price_columns):
  for i in range(len(item_and_price_columns)):
    item_and_price_column = item_and_price_columns[i]
    previous_amount = inventory_table.loc['0', item_and_price_column]
    inventory_table.loc['0', item_and_price_column] = int(previous_amount) + int(inventory_edit_message[i])

    # 水位警報
    current_amount = inventory_table.loc['0', item_and_price_column]
    current_amount = int(current_amount)
    if(current_amount < 0):
      status = '緊急補貨'
    elif(current_amount >= 0 and current_amount < 10):
      status = '庫存不足'
    elif(current_amount >= 10 and current_amount < 30):
      status = '準備補貨'
    elif(current_amount >= 30 and current_amount < 60):
      status = '狀態良好'
    elif(current_amount >= 60):
      status = '庫存過多'

    inventory_table.loc['1', item_and_price_column] = status

  return inventory_table

# 依照已付款表格編輯庫存管理
def order_edit_inventory(order_table, inventory_table, item_and_price_columns):
  for i in range(len(item_and_price_columns)):
    # 件數
    item_and_price_column = item_and_price_columns[i]
    amount = order_table[order_table['付款與否']=='已付款'][item_and_price_column].sum()
    try:
      previous_inventory = inventory_table.loc[f'{0}', item_and_price_column]
      inventory_table.loc[f'{0}', item_and_price_column] = int(previous_inventory) - int(amount)
      current_amount = inventory_table.loc[f'{0}', item_and_price_column]
    except:
      previous_inventory = inventory_table.loc[0, item_and_price_column]
      inventory_table.loc[0, item_and_price_column] = int(previous_inventory) - int(amount)
      current_amount = inventory_table.loc[0, item_and_price_column]

    # 水位警報
    
    current_amount = int(current_amount)
    if(current_amount < 0):
      status = '緊急補貨'
    elif(current_amount >= 0 and current_amount < 10):
      status = '庫存不足'
    elif(current_amount >= 10 and current_amount < 30):
      status = '準備補貨'
    elif(current_amount >= 30 and current_amount < 60):
      status = '狀態良好'
    elif(current_amount >= 60):
      status = '庫存過多'

    try:
      inventory_table.loc['1', item_and_price_column] = status
    except:
      inventory_table.loc[1, item_and_price_column] = status


  return inventory_table

