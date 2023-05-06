from app import application
from flask import jsonify, Response, session,Flask
from app.models import *
from app import *
import uuid
import datetime
from marshmallow import Schema, fields
from flask_restful import Resource, Api
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
import json


class SignUpRequest(Schema):
    name = fields.Str(default="name")
    username = fields.Str(default="Username")
    password = fields.Str(default="password")
    level = fields.Int(default=0)

class LoginRequest(Schema):
    username = fields.Str(default="Username")
    password = fields.Str(default="password")

class AddVendorRequest(Schema):
    user_id = fields.Str(default="user_id")

class AddItemRequest(Schema):
    item_name = fields.Str(default="item_name")
    calories_per_gm = fields.Int(default=100)
    available_quantity = fields.Int(default=100)
    restaurant_name = fields.Str(default="restaurant_name")
    unit_price = fields.Int(default=0)

class PlaceOrderRequest(Schema):
    order_id = fields.Str(default="order_id")


class VendorsListResponse(Schema):
    vendors = fields.List(fields.Dict())

class ItemListResponse(Schema):
    items = fields.List(fields.Dict())

class APIResponse(Schema):
    message = fields.Str(default ="success")

class ItemsOrderListResponse(Schema):
    items_order = fields.List(fields.Dict())

class ListOrderResponse(Schema):
    orders = fields.List(fields.Dict())



class SignUpAPI(MethodResource,Resource):
    @doc(description='Sign Up API', tags =['SignUp API'])
    @use_kwargs(SignUpRequest,location=('json'))
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try:
            user = User(
                uuid.uuid4(),
                kwargs['name'],
                kwargs['username'],
                kwargs['password'],
                kwargs['level']

            )

            db.session.add(user)
            db.session.commit()

            return APIResponse().dump(dict(message="User Is Successfully Registered ")),200
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message="not able to register the user: {str(e)}")),400
        
api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)


class LoginAPI(MethodResource,Resource):
    @doc(description='Login API', tags=['Login API'])
    @use_kwargs(LoginRequest,location=('json'))
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try:
            user = User.query.filter_by(username = kwargs['username'], password = kwargs['password']).first()
            if user:
                print("user logged in")

                session['user_id']= user.user_id
                print(f'User_id : {str(session["user_id"])}')
                return APIResponse().dump(dict(message='User is successfully logged in')),200
            else:
                return APIResponse().dump(dict(message='User not found')),404
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to login the user: {str(e)}')),400

api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)


class LogoutAPI(MethodResource,Resource):
    @doc(description='Logout API', tags=['Logout API'])
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try:
            if session['user_id']:
                session['user_id'] = None
                return APIResponse().dump(dict(message='User is Successfully logged out')),200
            else:
                return APIResponse().dump(dict(message='User is not logged in')),401
            
        except Exception as e:
            return APIResponse().dump(dict(message=f'Not able to logout the user: {str(e)}')),400

api.add_resource(LogoutAPI,'/logout')
docs.register(LogoutAPI)



class AddVendorAPI(MethodResource,Resource):
    @doc(description='Add Vendor API', tags=['Add Vendor API'])
    @use_kwargs(AddVendorRequest,location=('json'))
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                print(user_id)

                if(user_type == 2):
                    vendor_user_id= kwargs['user_id']
                    print(vendor_user_id)
                    user = User.query.filter_by(user_id = vendor_user_id).first()
                    print(user.level)
                    user.level = 1
                    db.session.add(user)
                    db.session.commit()

                    return APIResponse().dump(dict(message='Vendor is Successfully Added ')),200

                else:
                    return APIResponse().dump(dict(message='Logged user is not Admin')),405
            else:
                return APIResponse().dump(dict(message='User is not logged in')),401
            

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add Vendor: {str(e)}')),400


api.add_resource(AddVendorAPI, '/add_vendor')
docs.register(AddVendorAPI) 


class GetVendorsAPI(MethodResource,Resource):
    @doc(description='Get All Vendors API', tags=['Get All Vendor API'])
    @marshal_with(VendorsListResponse)
    def get(self):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type= User.query.filter_by(user_id = user_id).first().level
                print(user_id)
                if user_type == 2:
                    vendors = User.query.filter_by(level=1)
                    vendors_list=list()

                    for vendor in vendors:
                        vendor_dict=dict()
                        vendor_dict['vendor_id']=vendor.user_id
                        vendor_dict['name']=vendor.name

                        vendors_list.append(vendor_dict)

                    return VendorsListResponse().dump(dict(vendors = vendors_list)),200
                else:
                    return APIResponse().dump(dict(message='Loggen in User is not an admin')),405
            
            else:
                return APIResponse().dump(dict(message='User not logged in')),401
        except Exception as e:
            return APIResponse().dump(dict(message=f'Not able to list Vendors: {str(e)}')),400
                

api.add_resource(GetVendorsAPI, '/list_vendors')
docs.register(GetVendorsAPI)


class AddItemAPI(MethodResource,Resource):
    @doc(description="Add Item API", tags=['Add Item API'])
    @use_kwargs(AddItemRequest,location=('json'))
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                print(user_id)
                if user_type == 1:
                    item = Item(
                        uuid.uuid4(),
                        session['user_id'],
                        kwargs['item_name'],
                        kwargs['calories_per_gm'],
                        kwargs['available_quantity'],
                        kwargs['restaurant_name'],
                        kwargs['unit_price']
                    )
                   
                    # order_items= OrderItems(
                    #     uuid.uuid4(),
                    #     uuid.uuid4(),
                    #     item.item_id,
                    #     item.available_quantity,
                    #     1,
                    #     datetime.utcnow()
                    # )
                    # db.session.add(order_items)
                    
                    db.session.add(item)
                    db.session.commit()

                    return APIResponse().dump(dict(message='Item is successfully Added')),200
                else:
                    return APIResponse().dump(dict(message='Logged in user is not a vendor')),405
                
            return APIResponse().dump(dict(message='Vendor is not logged in')),401
        
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add the Items ')),400
        

api.add_resource(AddItemAPI, '/add_item')
docs.register(AddItemAPI)

class PlaceOrderAPI(MethodResource,Resource):
    @doc(description='Place Order API',tags=['Place Order API'])
    @use_kwargs(PlaceOrderRequest,location=('json'))
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                print(user_id)

                if user_type == 0:
                    order_items = OrderItems.query.filter_by(order_id = kwargs['order_id'],is_active =1)
                    order = Order.query.filter_by(order_id = kwargs['order_id'],is_active =1).first()

                    total_amount =0

                    for order_item in order_items:
                        item_id = order_item.item_id
                        quantity = order_item.quantity
                        item = Item.query.filter_by(item_id = item_id,is_active =1).first()

                        total_amount += quantity * item.unit_price

                        item.available_quantity -= quantity

                    order.total_amount = total_amount
                    db.session.commit()
                    return APIResponse().dump(dict(message="order is successfully placed")),200
                else:
                    return APIResponse().dump(dict(message="Logged in user is not a customer")),405
                
            else:
                return APIResponse().dump(dict(message="Customer is not logged in")),401
            
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f"Not able to place the order :{str(e)}")),400
        

api.add_resource(PlaceOrderAPI, '/place_order')
docs.register(PlaceOrderAPI)


class ListOrdersByCustomerAPI(MethodResource,Resource):
    @doc(description="List Orders by the Customers API",tags=['List Orders by Customer API'])
    @marshal_with(ListOrderResponse)

    def get(self):
        try:
            if session['user_id']:
                user_id = session['user_id']

                user_type = User.query.filter_by(user_id=user_id).first().level
                print(user_id)

                if user_type == 0:
                    orders = Order.query.filter_by(user_id=user_id,is_active=1)
                    order_list = list()

                    for order in orders:
                        order_items = OrderItems.query.filter_by(order_id=order.order_id,is_active =1)
                        order_dict = dict()
                        order_dict['order_id']= order.order_id
                        order_dict['items']=list()

                        for order_item in order_items:
                            order_item_dict= dict()
                            order_item_dict['item_id']= order_item.item_id
                            order_item_dict['quantity']= order_item.quantity
                            order_dict['items'].append(order_item_dict)

                        order_list.append(order_dict)

                    return ListOrderResponse().dump(dict(orders = order_list)),200
                
                else:
                    return APIResponse().dump(dict(message='Logged in user is not a Customer ')),405
                
            else:
                return APIResponse().dump(dict(message='Customer is not logged in ')),401
            
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list the orders :{str(e)} ')),400

api.add_resource(ListOrdersByCustomerAPI,'/list_orders')
docs.register(ListOrdersByCustomerAPI)


class ListAllOrdersAPI(MethodResource,Resource):
    @doc(description='List All Orders API', tags=['List All Orders API'])
    @marshal_with(ListOrderResponse)
    def get(self):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level

                print(user_id)

                if user_type == 2:
                    orders = Order.query.filter_by(is_active =1)
                    order_list = list()
                    for order in orders:
                        order_items = OrderItems.query.filter_by(order_id = order.order_id, is_active =1)
                        order_dict = dict()
                        order_dict['order_id']= order.order_id
                        order_dict['items']= list()

                        for order_item in order_items:
                            order_item_dict = dict()
                            order_item_dict['item_id']= order_item.item_id
                            order_item_dict['quantity']= order_item.quantity
                            order_dict['items'].append(order_item_dict)

                        order_list.append(order_list)

                    return ListOrderResponse().dump(dict(orders= order_list)),200
                else:
                    return APIResponse().dump(dict(message="Logged in user is not an admin")),405
                
            else:
                return APIResponse().dump(dict(message="Admin is not logged in")),401

        except Exception as e:
            print(e)
            return APIResponse().dump(dict(message=f"Not able to list all the orders: {str(e)}")),400

api.add_resource(ListAllOrdersAPI, '/list_all_orders')
docs.register(ListAllOrdersAPI)

