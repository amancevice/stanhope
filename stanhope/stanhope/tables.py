"""
StanhopeFramers Tables
"""
import io
import subprocess

import pandas
from stanhope import utils

pandas.set_option('display.max_rows', 100)
pandas.set_option('display.width', 100)


class Table(object):
    def __init__(self, *tables):
        self.tables = tables or (type(self).__name__,)
        self.frame = None

    @staticmethod
    def read(table):
        cmd = ['mdb-export', '/data/StanhopeFramers.mdb', table]
        out = subprocess.check_output(cmd)
        return io.BytesIO(out)

    def load(self):
        frame = pandas.DataFrame()
        for table in self.tables:
            page = pandas.read_csv(self.read(table), **self.READ_CSV)
            # page['Table'] = table
            frame = frame.append(page)
        self.frame = frame


class Customers(Table):
    READ_CSV = {
        'converters': {
            'Customer Number': utils.upper,
            'Credit': utils.boolean,
            'Tax Exempt': utils.boolean,
            'Deceased': utils.boolean},
        'parse_dates': [
            'Date',
            'Last Order',
            'Last Update']}

    def accounts(self):
        frame = self.frame.copy()

        # Copy legacy record
        frame['Legacy Customer Record'] = \
            frame.apply(utils.legacy_record, axis=1)

        # Drop unused columns
        frame.drop(['Address',
                    'City',
                    'Date',
                    'Deceased',
                    'Email',
                    'Last Order',
                    'Last Update',
                    'State',
                    'Telephone',
                    'Zip'],
                   axis=1,
                   inplace=True)

        # Rename columns
        frame.rename(inplace=True,
                     columns={'Customer Number': 'Legacy Customer Number',
                              'Name': 'Account',
                              'Comment': 'Comments'})

        # Set account name
        frame.loc[:, 'Account'] = \
            frame['Account'].apply(utils.replace_newline)\
                            .combine_first(frame['Legacy Customer Number'])

        # Massage fields
        frame.loc[~frame['Category'].isnull(), 'Category'] = \
            frame.loc[~frame['Category'].isnull(), 'Category'].apply(
                utils.account_category)
        frame.loc[~frame['Source'].isnull(), 'Source'] = \
            frame.loc[~frame['Source'].isnull(), 'Source'].apply(utils.source)

        # Return
        return frame

    def contacts(self):
        frame = self.frame.copy()

        # Drop unused columns
        frame.drop(['Category',
                    'Comment',
                    'Credit',
                    'Date',
                    'Last Order',
                    'Last Update',
                    'Source',
                    'Tax Exempt'],
                   axis=1,
                   inplace=True)

        # Rename columns
        frame.rename(inplace=True,
                     columns={'Customer Number': 'Account Link',
                              'Name': 'Contact'})

        # Massage fields
        frame.loc[:, 'Contact'] = \
            frame['Contact'].apply(utils.replace_newline)\
                            .combine_first(frame['Account Link'])
        frame.loc[:, 'Contact'] = frame['Contact'].apply(utils.replace_newline)
        frame.loc[:, 'Address'] = frame['Address'].apply(utils.replace_newline)
        frame.loc[:, 'City'] = frame['City'].apply(utils.replace_newline)
        frame.loc[:, 'State'] = frame['State'].apply(utils.replace_newline)
        frame.loc[:, 'Zip'] = frame['Zip'].apply(utils.replace_newline)
        frame.loc[:, 'Telephone'] = \
            frame['Telephone'].apply(utils.replace_newline)

        # Return
        return frame


class FrameOrders(Table):
    READ_CSV = {
        'converters': {'CustomerNo': utils.upper, 'OrderNo': utils.upper},
        'parse_dates': ['DateCompleted', 'DueDate', 'OrderDate']
    }

    def orders(self):
        frame = self.frame.copy()

        # Copy legacy record
        frame['Legacy Order Record'] = frame.apply(utils.legacy_record, axis=1)

        # Add Legacy Order ID
        frame['Legacy Order ID'] = frame.apply(utils.legacy_order_id, axis=1)

        # Drop unused columns
        frame.drop(['Artist',
                    'BinNo',
                    'Comments',
                    'DateCompleted',
                    'Fitting',
                    'Frame Height',
                    'Frame Width',
                    'FrameMfg',
                    'FrameNo',
                    'Glazing',
                    'Joining',
                    'Mat',
                    'MatColor',
                    'MatMfg',
                    'Matting',
                    'MattingSize',
                    'ProductionComments',
                    'Qty',
                    'SalesCatgy',
                    'SalesType',
                    'TotalSale'],
                   axis=1,
                   inplace=True)

        # Rename columns
        frame.rename(inplace=True,
                     columns={'OrderNo': 'Order Number',
                              'OrderDate': 'Order Date',
                              'DueDate': 'Due Date',
                              'CustomerNo': 'Account Link',
                              'Status': 'Order Status',
                              'Location': 'Order Location',
                              'SalesPers': 'Salesperson Link',
                              'Delivery': 'Delivery Location',
                              'Cust-Client': 'Client'})

        # Massage fields
        frame.loc[:, 'Delivery Location'] = \
            frame['Delivery Location'].apply(utils.delivery_location)
        frame.loc[:, 'Discount'] = frame['Discount'].apply(utils.discount)
        frame.loc[:, 'Order Location'] = \
            frame['Order Location'].apply(utils.order_location)
        frame.loc[:, 'Order Status'] = \
            frame['Order Status'].apply(utils.status)
        frame.loc[:, 'Salesperson Link'] = \
            frame['Salesperson Link'].apply(utils.salesperson)
        frame.loc[frame['Discount'].isnull(), 'Discount'] = 'No Discount'
        frame.loc[:, 'Delivery Location'] = \
            frame['Delivery Location'].combine_first(frame['Order Location'])
        frame.loc[:, 'Client'] = frame['Client'].fillna('None')

        # Return
        return frame

    def treatments(self):
        frame = self.frame.copy()

        # Add Legacy Order ID
        frame['Order Link'] = frame.apply(utils.legacy_order_id, axis=1)

        # Drop unused columns
        frame.drop(['Artist',
                    'Cust-Client',
                    'DateCompleted',
                    'Delivery',
                    'Discount',
                    'DueDate',
                    'Fitting',
                    'FrameMfg',
                    'Glazing',
                    'Location',
                    'Mat',
                    'Matting',
                    'OrderDate',
                    'OrderNo',
                    'SalesCatgy',
                    'SalesPers',
                    'Status'],
                   axis=1,
                   inplace=True)

        # Rename fields
        frame.rename(inplace=True,
                     columns={'BinNo': 'Bin Number',
                              'Comments': 'Description',
                              'CustomerNo': 'Account Link',
                              'FrameNo': 'Frame Style',
                              'Joining': 'Frame Join',
                              'MatColor': 'Mat Color',
                              'MatMfg': 'Mat Manufacturer',
                              'MattingSize': 'Mat Size',
                              'ProductionComments': 'Production Comments',
                              'Qty': 'Quantity',
                              'SalesType': 'Type',
                              'TotalSale': 'Price'})

        # Massage fields
        frame.loc[:, 'Frame Join'] = frame['Frame Join'].apply(utils.join)
        frame.loc[:, 'Mat Manufacturer'] = \
            frame['Mat Manufacturer'].apply(utils.matmfg)
        frame.loc[:, 'Type'] = frame['Type'].apply(utils.sales_type)

        # Add dimensions
        frame['Frame Width Inches'] = \
            frame['Frame Width'].apply(utils.inches)
        frame['Frame Width Fraction'] = \
            frame['Frame Width'].apply(utils.fraction)
        frame['Frame Height Inches'] = \
            frame['Frame Height'].apply(utils.inches)
        frame['Frame Height Fraction'] = \
            frame['Frame Height'].apply(utils.fraction)
        frame.drop(['Frame Width', 'Frame Height'], axis=1, inplace=True)

        # Return
        return frame