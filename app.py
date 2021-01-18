#! usr/bin/env python3
 
import csv
import datetime
import sys
import os
import pandas

from collections import OrderedDict
from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = PrimaryKeyField()
    product_name = CharField(max_length=255, unique=True)
    product_price = IntegerField()
    product_quantity = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def upload_db():
    """Upload's data to database."""
    with open('inventory.csv', newline='') as csvfile:
        csvreader = csv.DictReader(csvfile)
        rows = list(csvreader)
        for row in rows:
            row['product_price'] = int(row['product_price'].replace('$', '').replace('.', ''))
            row['product_quantity'] = int(float(row['product_quantity']))
            try:
                Product.create(
                    product_name=row['product_name'],
                    product_price=row['product_price'],
                    product_quantity=row['product_quantity'],
                    date_updated=row['date_updated']
                )
            except IntegrityError: 
                product_record = Product.get(product_name = row['product_name'])
                product_record.product_name = row['product_name']
                product_record.product_price = row['product_price']
                product_record.product_quantity = row['product_quantity']
                product_record.date_updated = row['date_updated']
                product_record.save()
                if product_record != row['product_name']:
                    product_record.update(product_record.date_updated)


def initialize():
    '''Initializes the database.'''
    db.connect()
    db.create_tables([Product], safe=True)
    upload_db()
    menu_loop()


def menu_loop():
    '''Shows the menu.'''
    choice = None
    clear()

    print('#'*40)
    print(' '*15,'Main Menu')
    print('#'*40)
    print(
        'Welcome to the store inventory.',
        '\nby: Adrian Brown'
    )

    while choice != 'q':
        print("\nEnter 'q' to quit.\n")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('\nAction: ').lower().strip()

        if choice in menu:
            clear()
            menu[choice]()


def clear():
    '''clear the screen'''
    os.system('cls' if os.name == 'nt' else 'clear')


def add():
    """Add items to inventory."""
    print('-'*35)
    print("press ctrl + d when finished.")
    print('-'*35)
    clear()

    while True:
        name = input('\nWhat is your product name: ')
        print('-'*35)
        try:
            if not name or name == ' ':
                raise ValueError("Enter a valid product name.")
        except ValueError as e:
            print(e)
            print("You might've hit the enter key on accident.")
            print('-'*35)
        else:
            break

    while True:
        price = input('Price of the product: ').strip()
        print('-'*35)
        
        try:
            price = int(float(price)*100)
            break
        except ValueError:
            print("Try again, format: (0.00)")
            continue

    while True:
        quantity = input('Quantity of product: ').strip()
        print('-'*35)
        try:
            quantity = str(int(quantity))
            break
        except ValueError:
            print("Please enter a integer.")
            continue
    
    now = datetime.datetime.today
    updated = now().strftime("%m/%d/%Y")
    price = str(price)
    print(('\n'+name+','+price+','+quantity+','+updated))
    print()
    if input('Save Entry? [Yn]').lower() != 'n':
        with open('inventory.csv', 'a') as file: 
            file.write('\n'+name+','+price+','+quantity+','+updated)
        print('-'*35)
        print('Saved successfully!')
        print('-'*35)
        upload_db()


def search(search_query=None):
    """View items in inventory."""
    products = Product.select().order_by(Product.product_id.asc())
    if search_query:
        products = products.where(Product.product_id.contains(search_query))
    
    for product in products:
        timestamp = product.date_updated
        clear()
        print(timestamp) 
        print('='*len(timestamp))
        print(product.product_id, product.product_name, '| price:', '$'+str(product.product_price*.01), '| quantity:', product.product_quantity)
        print('='*len(timestamp))
        print()
        print('n) next entry')
        print('q) return to main menu')
        print('-'*35)

        next_action = input('Action: [Ndq]').lower().strip()
        if next_action == 'q':
            break


def backup():
    """Back-up data to database."""
    clear()
    print("Loading...")
    print("Sync completed. Database.csv uploaded.")
    print()
    now = datetime.datetime.today
    updated = now().strftime("%m/%d/%Y")
    print(updated)
    select = pandas.read_sql_query("SELECT * FROM product", db)
    select.to_csv('database.csv', index=False)
    

def view():
    '''Search entries in database.'''
    search(input('Search: '))

menu = OrderedDict([
    ('a', add),
    ('v', view),
    ('b', backup),
])

if __name__ == "__main__":
    initialize()