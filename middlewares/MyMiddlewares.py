from django.db import connection 

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from users.models import Users
from notifications.models import Notifications, UsersNotifications
from stores.models import Stores
from customers.models import Customers
from catalogues.models import Person
from purchases.models import PurchasesDetails
from sales.models import Sales
from tasks.models import Tasks, UsersTasks

from datetime import datetime

class TasksNotificationsMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response
		# One-time configuration and initialization.

	def __call__(self, request):
		# Code to be executed for each request before
		# the view (and later middleware) are called.

		response = self.get_response(request)

		# Code to be executed for each request/response after
		# the view is called.

		# print('******request******')
		# print(request.build_absolute_uri('?'))

		req=request.build_absolute_uri('?')
		modules=[
			'stores', 'customers', 'purchases', 'products-stores', 'brands',
			#'products-stores', 'brands',
			'products', 'providers', 'shops', 'users/admin', 'sales'
		]
		watch=['INSERT', 'DELETE', 'UPDATE']
		tables=[
			'stores_stores', 'customers_customers', 'purchases_purchases',
			'purchases_purchasesproductsdetails', 'brands_brands',
			'products_products', 'providers_providers', 'shops_shops',
			'users_users', 'sales_sales'
		]
		actions=[
			[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18],
			[19,20,21],[22,23,24],[25,26,27],[28,29,30],[31,32,33]
		]

		for x in range(len(modules)):
			if modules[x] in req:
				# print('**********entro 1********')
				for query in connection.queries:
					q=query['sql'].upper()
					for y in range(len(watch)):
						if watch[y] in q:
							# print('**********entro 2********')
							for z in range(len(tables)):
								table=tables[z].upper()
								# print('**********re********')
								# print(req)
								if table in q and 'SELECT "AUTH_USER"."ID"' not in q:
									# print('**********entro 3********')
									# print(q)
									# print('**********x********')
									# print(x)
									# print('**********y********')
									# print(y)
									# print('**********z********')
									# print(z)
									# print('**********re********')
									# print(req)
									try:
										notif=Notifications(pk=actions[x][y])
									except IndexError:
										if 'CUSTOMERS' in q:
											if 'INSERT' in q:
												notif=Notifications(pk=actions[1][0])

									un=UsersNotifications()
									# un.done=True
									un.created_by_user=Users.objects.get(pk=1)
									name=''
									x_=x
									if 'CUSTOMERS' in q:
										x_=1
									elif 'PROVIDERS_PROVIDERS' in q:
										x_=6
									elif 'PURCHASES_PURCHASES' in q:
										x_=2
									elif 'SALES_SALES' in q:
										x_=9

									# print('**********module********')
									# print(modules[x_])

									today=datetime.now()
									un.created_at=today
									un.created_when=today

									try:
										user=Users.objects.get(email__iexact=request.user)
									except ObjectDoesNotExist:
										return response

									'''
									stores
									'''
									if modules[x_]=='stores':
										if watch[y]=='INSERT':
											name=q[q.find('VALUES (')+len('VALUES ('):]
											name=name[name.find(", '")+len(", '"):name.find("',")]
											store=Stores.objects.get(created_at=name,created_when=today)
											name=store.name
											task=Tasks.objects.get(pk=2)
											ut=UsersTasks.objects.get(task=task,user=user)
											ut.percent=100
											ut.save()
										elif watch[y]=='UPDATE':
											if '"DROPPED" = 1' in q:
												notif=Notifications(pk=actions[x_][y-1])
											x=q.find('"NAME" = \'')+len('"NAME" = \'')
											name=q[x:q.find("'", x)]

									# customers
									elif modules[x_]=='customers':
										if 'INSERT' in q:
											name=q[q.find('SELECT ')+len('SELECT '):q.rfind(',')]
											# name=q[q.find('PERSON_PTR_ID" = ')+len('PERSON_PTR_ID" = '):]
											person=Person.objects.get(pk=name)
											name=person.full_name
										elif watch[y]=='UPDATE' and 'do-add' not in req: 
											name=q[q.find('PERSON_PTR_ID" = ')+len('PERSON_PTR_ID" = '):]
											if 'confirmed-delete' in req:
												notif=Notifications(pk=actions[x][1])

											person=Person.objects.get(pk=name)
											name=person.full_name

									# purchases
									elif modules[x_]=='purchases':
										if 'INSERT' in q and '"PURCHASES_PURCHASES"' in q:
											q_=q[q.find('VALUES (')+len('VALUES ('):]
											for x in range(3):
												y=q_.find(", '")+len(", '")
												q_=q_[y:]
											name=q_[0:q_.find("',")] + ' (' + _('Purchase identifier') + ')'
										elif 'UPDATE' in q and '"PURCHASES_PURCHASES"' in q:
											if '"DROPPED" = 1' in q:
												notif=Notifications(pk=actions[x_][y-1])
											name=q[q.find('IDENTIFIER" = \'')+len('IDENTIFIER" = \''):]
											name=name[:name.find("',")] + ' (' + _('Purchase identifier') + ')'

										# products-stores (inventarios)
										elif 'UPDATE' in q and '"PURCHASES_PURCHASESPRODUCTSDETAILS"' in q:
											# notif=Notifications(pk=actions[x_+1][y-1])
											if 'products-stores/update' in req:
												if '"STORED" = 1' in q:
													notif=Notifications(pk=actions[x_+1][0])
												else:
													notif=Notifications(pk=actions[x_+1][2])
											elif 'products-stores/confirmed-delete' in req:
												notif=Notifications(pk=actions[x_+1][1])
											name=q[q.find('"PURCHASE_DETAIL_ID" = ')+len('"PURCHASE_DETAIL_ID" = '):]
											name=name[:name.find(",")]
											pd=PurchasesDetails.objects.get(pk=name)
											name=pd.product.name + ' ' + pd.brand.name

									# brands
									elif modules[x_]=='brands':
										if watch[y]=='INSERT':
											name=q[q.rfind(", '")+len(", '"):q.rfind("')")]
											task=Tasks.objects.get(pk=3)
											ut=UsersTasks.objects.get(task=task,user=user)
											ut.percent=100
											ut.save()
										elif watch[y]=='UPDATE':
											if '"DROPPED" = 1' in q:
												notif=Notifications(pk=actions[x_][y-1])
											elif '"DROPPED" = 0' in q:
												notif=Notifications(pk=actions[x_][y-2])
											x=q.find('"NAME" = \'')+len('"NAME" = \'')
											name=q[x:q.find("'", x)]

									# products
									elif modules[x_]=='products':
										if watch[y]=='INSERT':
											name=q[q.rfind(", '")+len(", '"):q.rfind("')")]
											task=Tasks.objects.get(pk=4)
											ut=UsersTasks.objects.get(task=task,user=user)
											ut.percent=100
											ut.save()
										elif watch[y]=='UPDATE':
											if '"DROPPED" = 1' in q:
												notif=Notifications(pk=actions[x_][y-1])
											elif '"DROPPED" = 0' in q:
												notif=Notifications(pk=actions[x_][y-2])
											x=q.find('"NAME" = \'')+len('"NAME" = \'')
											name=q[x:q.find("'", x)]

									# providers
									elif modules[x_]=='providers':
										if watch[y]=='INSERT':
											if '"PROVIDERS_PROVIDERS"' in q:
												x=q.rfind("',")
												q_=q[:x]
												name=q_[q_.rfind(", '")+len(", '"):]
												task=Tasks.objects.get(pk=5)
												ut=UsersTasks.objects.get(task=task,user=user)
												ut.percent=100
												ut.save()
										elif watch[y]=='UPDATE':
											if '"DROPPED" = 1' in q:
												notif=Notifications(pk=actions[x_][y-1])
											x=q.find('"NAME" = \'')+len('"NAME" = \'')
											name=q[x:q.find("'", x)]

									# shops
									elif modules[x_]=='shops':
										if watch[y]=='INSERT':
											q_=q[q.find("VALUES (")+len("VALUES ("):]
											for x in range(12):
												q_=q_[q_.find(', ')+len(', '):]
											name=q_[1:q_.find("',")]
											task=Tasks.objects.get(pk=1)
											ut=UsersTasks.objects.get(task=task,user=user)
											ut.percent=100
											ut.save()
										elif watch[y]=='UPDATE':
											if '"DROPPED" = 1' in q:
												notif=Notifications(pk=actions[x_][y-1])
											x=q.find('"NAME" = \'')+len('"NAME" = \'')
											name=q[x:q.find("'", x)]

									# users/admin
									elif modules[x_]=='users/admin':
										if 'automatic-updates' not in req:
											if watch[y]=='INSERT':
												q_=q[q.find("SELECT ")+len("SELECT "):]
												name=q_[:q_.find(",")]
											elif watch[y]=='UPDATE':
												if '"DROPPED" = 1' in q:
													notif=Notifications(pk=actions[x_][y-1])
												x=q.find('WHERE "USERS_USERS"."USER_PTR_ID" = ')+len('WHERE "USERS_USERS"."USER_PTR_ID" = ')
												name=q[x:]
											usr=Users.objects.get(pk=name)
											name=usr.full_name

									# sales
									elif modules[x_]=='sales':
										if 'INSERT' in q and '"SALES_SALESDETAILS"' in q:
											# if '"SALES_SALESDETAILS"' in q:
												q_=q[q.find("VALUES (")+len("VALUES ("):]
												for x in range(11):
													q_=q_[q_.find(', ')+len(', '):]
												name=q_[:q_.find(",")]
												sale=Sales.objects.get(pk=name)
												name=sale.identifier + ' (' + _('Sale identifier') + ')'
										# elif watch[y]=='UPDATE':
										elif 'UPDATE' in q and '"SALES_SALES"' in q:
											if '"DROPPED" = 1' in q:
												notif=Notifications(pk=actions[x_][y-1])
											name=q[q.find('"SALES_SALES"."ID" = ')+len('"SALES_SALES"."ID" = '):]
											# name=name[:name.find("',")] + ' (' + _('Sale identifier') + ')'
											sale=Sales.objects.get(pk=name)
											name=sale.identifier + ' (' + _('Sale identifier') + ')'

									if name and len(name.strip())>0:
										un.notification=notif
										un.obj_name=name
										un.user=user
										if '"PURCHASES_PURCHASESPRODUCTSDETAILS"' in q:
											un_=UsersNotifications.objects.filter(obj_name__icontains=name,user=user,notification=notif)
											if len(un_)<1:
												un.save()
										else:
											un.save()

										# if 'UPDATE' in q and '"SALES_SALESDETAILS"' in q:
										# if '"SALES_SALESDETAILS"' in q:
										if 'sales/do-add' in req and un.notification.id==33:
											un.delete()
											# print('*********notif*******')
											# print(un.notification.id)
											# print('*********query*******')
											# print(q)
											# print('*********req*******')
											# print(req)

									# if '"PURCHASES_PURCHASESPRODUCTSDETAILS"' in q:
									# 	uns=UsersNotifications.objects.filter(user=user,obj_name__icontains=name).order_by('-id')
									# 	print('********uns ANTES******')
									# 	print(uns)
									# 	uns=uns[0:3]
									# 	print('********uns DESPUES******')
									# 	print(uns)
									# 	for un in uns:
									# 		un.delete()


		# if [int(i) for i in modules] in req:
		# 	print('ok')

		# from sys import stdout
		# if stdout.isatty():
		# 	for query in connection.queries:
		# 		print('*************query**********')
		# 		print(query['sql'])
				# print("\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (query['time']," ".join(query['sql'].split())))

		return response