#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from quart import Quart, request, abort
from datetime import datetime
from pearsonr import pearsonr_py
import scipy.stats
from scipy.stats import pearsonr
from pymysql import connect
from typing import List, Tuple, Type

host = 'db'
port = 3306
db = 'iot_data'
user = 'analitic'
passwd = 's9cre93'

def get_connection() : # -> connection
    return connect(host=host, user=user, passwd=passwd, db=db,port=port)

async def verified(data : dict) -> bool:
    return 'data' in data and 'x' in data['data'] and 'y' in data['data'] \
    and 'x_data_type' in data['data'] and 'y_data_type' in data['data']


async def set_data(user : int,xtype : str, ytype : str, value : float, p: float) -> Tuple[str, bool]:
    '''
    transfer correlation coefficient to db
    '''
    try:

        if 'connection' not in app.__dict__:
            app.connection =  get_connection()
        if not app.connection.open or not app.connection.ping():
            app.connection.close()
            try:
                app.connection = get_connection()
                
            except Exception as e:
                open("log.txt", "a").write("Connect to db: {}".format(str(e)))
                del app.connection
                return
        cur = app.connection.cursor()
        # print("Replace into correlation  VaLUE ({}, '{}', '{}', {}, {})".format(user,xtype,ytype,value,p))
        cur.execute("Replace into correlation  VaLUE ({}, '{}', '{}', {}, {})".format(user,xtype,ytype,value,p))
        app.connection.commit()
        return "", True
    except Exception as e:
        return "Something wrong: " + str(e), False

async def do_calculate(data : dict, msg : str) -> Tuple[str, bool]:
    '''
    calculate correlation and save one to db
    data: json from POST
    msg: log string
    '''
    if not await verified(data):
        msg = "Some data is wrong"
        return msg, False
    
    xtype = data['data']['x_data_type']
    ytype = data['data']['y_data_type']
    user = data['user_id']
    r,p = 0,0
    try:
        d = {'x':{datetime.strptime(row['date'],"%Y-%m-%d"):row['value'] for row in data['data']["x"]},
                'y':{datetime.strptime(row['date'], "%Y-%m-%d"):row['value'] for row in  data['data']['y']}}
        xkeys = set(d['x'].keys())
        ykeys = set(d['y'].keys())
        keys = xkeys.intersection(ykeys)
        x = [r[1] for r in sorted(filter( lambda it: it[0] in keys, d['x'].items() ), key=lambda a: a[0] )]
        y = [r[1] for r in sorted(filter( lambda it: it[0] in keys, d['y'].items() ), key=lambda a: a[0] )]
        if len(x) < 150:
            r,p = pearsonr_py(x, y)
        else:
            r,p = pearsonr(x,y)
    except Exception as e:
        print('do_calculate: ', e)
        return "wrong with math", False

    msg, t= await set_data(user,xtype,ytype, r, p)    
    
    return msg, t
 

app = Quart(__name__)

@app.route('/calculate', methods=["POST"])
async def calculate() -> str:
    '''
    API method
    calculate Pearson's correletion of POSTed data
    '''
    # if 'token' not in request.args:
    #     return 'token requested'

    # if request.args['token'] not in tokens:
    #     return 'valid token requested'
    
    json = await request.get_json()
    
    if not json :
        abort(400)
    msg = "Data is recieved"
    if isinstance(json, dict):
        msg,result = await do_calculate(json, msg)

    elif isinstance(json, list):
        for data in json:
            msg, result = await do_calculate(data,msg)
            if not result:
                break
    else:
        msg = "Wrong json: "

    print(msg)
    return ''

@app.route('/correlation', methods=['GET'])
async def correlation() -> str:
    '''
    Get correlation from db
    '''
    if "x_data_type" not in request.args or 'y_data_type' not in request.args or 'user_id' not in request.args:
        abort(404)

    xtype = request.args["x_data_type"]
    ytype = request.args['y_data_type']
    userid = request.args['user_id']

    try:
        connection = get_connection()
        with connection:
            cur = connection.cursor()
            cur.execute("Select  value,p from correlation where xtype = '{}' and ytype='{}' and user_id={}".format(xtype,ytype,userid))
            value = cur.fetchone()
            if value == (): abort(404)
    except Exception as e:
        print('correlation: ', e)
        abort(404)

    responseOk="""{{
   "user_id" : {},
   "x_data_type" : "{}",
   "y_data_type" : "{}",
   "correlation" : {{
    "value" : {},
    "p_value" : {}  # I don't know what your math notation is, so I guess p_value == value
   }}
}}   
"""

    return responseOk.format(userid, xtype, ytype, value[0],value[1]) 
    

if __name__ == '__main__':
    try:
        app.connection = get_connection()
    except Exception as e:
        print('main: ', e)
        exit(1)
    app.run(host='0.0.0.0',debug=True)


