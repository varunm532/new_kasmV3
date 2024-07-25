import json, jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime

from model.user import User
from model.stocks import StockUser,StockTransaction,TableStock, UserTransactionStock

stock_api = Blueprint('stock_api', __name__,
                   url_prefix='/stock')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(stock_api)
""" For this code to work, first you would need to bulk update the stock table by using the data in the csv file: stocks_table_exp.csv. 
Then the first thing to run is _initilize_user to create a new user in the StockUser table. 
A possible post request of postman:{"uid":"niko","quantity":10,"symbol": "AAPL"}.
All db change are found in the model/user.py file"""
class StockAPI:
    # used to create a user log to stockuser table
    # Supposed to be called when user first starts
    class _initilize_user(Resource):
        def post(self):
            body = request.get_json()
            uid = body.get('uid')
            u = User.add_stockuser(self,uid)
            print(str(u))
    # not final,  used to test if major db changes work
    # contains no logic for project yet
    class _transaction_buy1(Resource):
        def post(self):
            body = request.get_json()
            
            quantity = body.get("quantity")
            symbol = body.get("symbol")
            uid = body.get("uid")
            current_stock_price = TableStock.get_price(self,body)
            value = quantity * current_stock_price
            bal = StockUser.get_balance(self,body)
            userid = StockUser.get_userid(self,uid)
            stockid = TableStock.get_stockid(self,symbol)
            u=StockTransaction.createlog_buy(self,body)
            z= UserTransactionStock.multilog_buy(self,body = body,value = value,transactionid=u)
            print(str(z))
            print("this is transactionid" + str(u))
            print("this is user id" + str(userid))
            print("this is stockid" + str(stockid))
            
    class _tranaction_buy(Resource):
        def post(self):
            body = request.get_json()
            userbal = StockUser.get_balance(self,body)
            stockval = TableStock.get_price(self,body)
            quantity = body.get("quantity")
            isbuy = True
            transactionval = quantity * stockval
            if userbal >= transactionval:
                # update user bal
                StockUser.updatebal(self,body,transactionval)
                # create stocktransacotin log
                u=StockTransaction.createlog_buy(self,body)
                UserTransactionStock.multilog_buy(self,body = body,value = transactionval,transactionid=u)
                # update stock quantity
                TableStock.updatequantity(self,body,isbuy)
            else:
                return jsonify({'error': 'Insufficient funds'}), 400
                

                
                
                
            

    class _transaction_sell(Resource):
        def post(self):
            body = request.get_json()
    api.add_resource(_initilize_user, '/initilize')
    api.add_resource(_tranaction_buy, '/buy')
    api.add_resource(_transaction_sell, '/sell')

