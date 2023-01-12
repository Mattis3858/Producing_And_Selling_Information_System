from flask import Flask, render_template, url_for, redirect, request, session, flash
from datetime import timedelta
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
from functions import *
import pandas as pd
from pandas import DataFrame
from ArticutAPI import Articut
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


app = Flask(__name__)
app.secret_key = 'hello'
# app.permanent_session_lifetime = timedelta(minutes=60)
# app.permanent_session_lifetime = timedelta(seconds=1)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        flash('Login Successful!')
        return redirect(url_for('order'))
    else:
        if 'user' in session:
            flash("Already logged in")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route('/user', methods=['POST', 'GET'])
def user():
    email = None
    if "user" in session:
        user = session['user']

        if request.method == 'POST':
            email = request.form["email"]
            session["email"] = email
            
            flash("Email was saved")
            flash(f'{email}')
        else:
            if "email" in session:
                email = session['email']
        return render_template("user.html", user = user, email = email)
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    if "user" in session:
        user = session['user']
        flash(f"You have been logged out!, {user}", "info")
        session.pop("user", None)
        session.pop('email', None)
        return redirect(url_for("login"))
    else:
        flash("You need to login first!")
        return redirect(url_for("login"))


@app.route('/order', methods=["POST","GET"])
def order():
    
    if request.method == "POST":
        
        # session['table_items'] = table_items
        # session['table_units'] = table_units
        # session['table_prices'] = table_prices
        #step1

        message = getName('order')
        articut = articut_lv2(username, apikey)
        # 極致斷詞lv3設定
        detailed_articut = articut_lv3(username, apikey)
        
        # flash(f"{'order_table_dict' in session}")
            # step2
            # 表格設定
        if 'order_table_dict' in session:
            order_table = pd.DataFrame(session['order_table_dict'])
            item_price_table = pd.DataFrame(session['item_price_table_dict'])
            item_and_price_columns = session['item_and_price_columns']
            # flash(type(item_and_price_columns))
            customer_df = pd.DataFrame(session['customer_df_dict'])
            customer_df['歷史訂單編號']=customer_df['歷史訂單編號'].astype('object')
            # flash(type(customer_df))
            inventory_table = pd.DataFrame(session['inventory_table_dict'])
            stastics = pd.DataFrame(session['statistics_dict'])
            # flash(stastics)
        else:
            result_table = setting_order_table(input_to_list(session['columns_set_statement']), session['table_id'], session['table_items'], session['table_units'], session['table_prices'])

            order_table = result_table[0]
            # session['initial_order_table_dict'] = order_table.to_dict()
            # order_table = pd.DataFrame(session['initial_order_table_dict'])
            # flash(order_table)
            item_price_table = result_table[1]
            # session['initial_item_price_table_dict'] = item_price_table.to_dict()
            # item_price_table = pd.DataFrame(session['initial_item_price_table_dict'])
            # # flash(session['initial_item_price_table_dict'])
            item_and_price_columns = result_table[2]
            customer_df = setting_customer_table()
            # flash(customer_df)
        #     session['initial_customer_df_dict'] = customer_df.to_dict()
        #     customer_df = pd.DataFrame(session['initial_customer_df_dict'])

            inventory_table = setting_invetory_table(item_and_price_columns)
        #     session['initial_inventory_table_dict'] = inventory_table.to_dict()
        #     inventory_table = pd.DataFrame(session['initial_inventory_table_dict'])

            stastics = setting_stastics(item_and_price_columns)#貼在統計頁面 (DF)
        #     session['initial_stastics_dict'] = stastics.to_dict()
        #     stastics = pd.DataFrame(session['initial_stastics_dict'])

            

        # step3
        line_message_enter_result =  line_message_enter(message, articut, detailed_articut, order_table, item_price_table, item_and_price_columns, customer_df, stastics, inventory_table,'果乾')
    
        if(len(line_message_enter_result)==2): # 代表輸入訂購訊息
                # 以下兩個是要顯示出來的
            order_table = line_message_enter_result[0]
            wrong_msg = line_message_enter_result[1]
        elif(len(line_message_enter_result)==4): # 代表輸入付款訊息
                # 以下兩個是要顯示出來的
            wrong_msg = '輸入的為付款訊息'
            order_table = line_message_enter_result[0]
            # 以下三個純更新即可
            customer_df = line_message_enter_result[1]
            stastics = line_message_enter_result[2]
            inventory_table = line_message_enter_result[3]
            flash(wrong_msg)
        elif(len(line_message_enter_result)==1): #代表無法讀取、出錯
            flash('無法讀取')
        else:
            flash('回傳失敗')
            

        # #     # step4
        item_price_table_dict = item_price_table.to_dict()

        order_table_dict = order_table.to_dict()

        customer_df_dict = customer_df.to_dict()
        inventory_table_dict = inventory_table.to_dict()
        statistics_dict = stastics.to_dict()

        session['item_price_table_dict'] = item_price_table_dict
        session['order_table_dict'] = order_table_dict
        session['item_and_price_columns'] = item_and_price_columns
        session['customer_df_dict']=customer_df_dict
        session['inventory_table_dict'] = inventory_table_dict
        session['statistics_dict'] = statistics_dict
        df = pd.DataFrame(session['order_table_dict'])
        return render_template('order.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
        return render_template('order.html')

        
    return render_template('order.html')
#------------------------------------------------------------
    
#------------------------------------------------------------

    return render_template('order.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/relation')
def relation():
    df = pd.DataFrame(session['customer_df_dict'])

    return render_template('customerRelation.html', tables=[df.to_html()], titles=[''])



@app.route('/activity', methods=['GET', 'POST'])
def activity():
    
    if request.method == "POST":
        table_items = []#!
        table_units = []
        table_prices = []
        columns_set_statement = getName('other')
        session['columns_set_statement'] = columns_set_statement
        table_id = getName('actID')
        apple = getName('apple')
        apple_box = getName('apple_box')
        mango = getName('mango')
        peach = getName('peach')
        peach_seed = getName('peach_seed')
        apple_price = getName('apple_price')
        apple_box_price= getName('apple_box_price')
        mango_price = getName('mango_price')
        peach_price = getName('peach_price')
        peach_seed_price = getName('peach_seed_price')
        if checkOn(apple):
            session['apple'] = 'apple'
            table_items.append('蘋果乾')
            table_units.append('包')
            table_prices.append(apple_price)
        if checkOn(apple_box):
            session['apple_box'] = 'apple_box'
            table_items.append('蘋果禮盒')
            table_units.append('盒')
            table_prices.append(apple_box_price)
        if checkOn(mango):
            session['mango'] = 'mango'
            table_items.append('芒果乾')
            table_units.append('包')
            table_prices.append(mango_price)
        if checkOn(peach):
            session['peach'] = 'peach'
            table_items.append('水蜜桃乾')
            table_units.append('包')
            table_prices.append(peach_price)
        if checkOn(peach_seed):
            session['peach_seed'] = 'peach_seed'
            table_items.append('水蜜桃籽乾')
            table_units.append('包')
            table_prices.append(peach_seed_price)
        session['table_id'] = table_id
        session['table_items'] = table_items
        session['table_units'] = table_units
        session['table_prices'] = table_prices
        
        #!Dataframe
        articut = articut_lv2(username, apikey)
        # 極致斷詞lv3設定
        detailed_articut = articut_lv3(username, apikey)

        
        return redirect(url_for('activity'))
    return render_template('activity.html')

@app.route('/salesStatistics')
def salesStatistics():
    df = pd.DataFrame(session['statistics_dict'])

    return render_template('salesStatistics.html', tables=[df.to_html()], titles=[''])

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():

    inventory_edit_message_list = []
    if request.method == "POST":
        # inventory_table = manual_edit_inventory(inventory_table, inventory_edit_message, item_and_price_columns) ##回傳inventory table(DF)
        apple_inventory = checkNone(getName('apple_inventory'))
        apple_box_inventory = checkNone(getName('apple_box_inventory'))
        mango_inventory = checkNone(getName('mango_inventory'))
        peach_inventory = checkNone(getName('peach_inventory'))
        peach_seed_inventory = checkNone(getName('peach_seed_inventory'))
        
        inventory_edit_message_list.append(apple_inventory)
        inventory_edit_message_list.append(apple_box_inventory)
        inventory_edit_message_list.append(mango_inventory)
        inventory_edit_message_list.append(peach_inventory)
        inventory_edit_message_list.append(peach_seed_inventory)
        session['inventory_edit_message'] = inventory_edit_message_list
        
    
        df = manual_edit_inventory(pd.DataFrame(session['inventory_table_dict']),  session['inventory_edit_message'], session['item_and_price_columns'])

        return render_template(('inventory.html'), tables=[df.to_html()], titles=[''])
    return render_template('inventory.html')

def checkNone(inventory):
    if inventory == "":
        return '0'
    else:
        return inventory


def getName(果乾):
    return request.form.get(果乾)
def checkOn(果乾):
    if 果乾 == 'on':
        return True
    else:
        return False


if __name__ == "__main__":
    app.run(debug=True)