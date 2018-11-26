import logging

import mysql.connector as mysql_connector

from bot.poster import Poster
from bot.config import Config


class Database:
    def __init__(self):
        self.conn = mysql_connector.connect(
            host=Config.mysql_host,
            user=Config.mysql_login,
            password=Config.mysql_password,
            database=Config.mysql_db,
            auth_plugin='mysql_native_password'
        )

    def execute(self, sql_query: str, *args):
        cur = self.conn.cursor()
        cur.execute(sql_query, args)
        try:
            result = cur.fetchall()
        except mysql_connector.errors.InterfaceError:
            result = None
        self.conn.commit()
        return result

    def disconnect(self):
        self.conn.close()


class DiscountChecker:
    def __init__(self, db: Database):
        self.db = db

    def get_discounts(self):
        discounts = self.db.execute(
            "SELECT Idlistdiscount, PriceID, Discount FROM shopdb.historydiscount WHERE VK = 0 AND Discount > 30"
        )
        return discounts

    def get_item(self, price_id):
        shop_id, item_id = self.db.execute("SELECT ShopID, ItemID FROM shopdb.price WHERE PriceID = %s", price_id)[0]
        return shop_id, item_id

    def get_urls(self, item_id):
        url, photo_url = self.db.execute("SELECT Url, UrlPhoto FROM shopdb.article WHERE ItemID = %s", item_id)[0]
        return url, photo_url

    def get_price(self, price_id):
        price = self.db.execute("SELECT Price FROM shopdb.price WHERE PriceID = %s", price_id)[0]
        return price

    def get_item_name(self, item_id):
        item_name = self.db.execute("SELECT ItemName FROM shopdb.item WHERE ItemID = %s", item_id)[0]
        return item_name

    def get_shop_name(self, shop_id):
        shop_name = self.db.execute("SELECT ShopName FROM shopdb.shop WHERE ShopID = %s", shop_id)[0]
        return shop_name

    def mark_as_posted(self, discount_id):
        self.db.execute("UPDATE `shopdb`.`historydiscount` SET `VK`='1' WHERE `Idlistdiscount`= %s", discount_id)


def scheduled_job():
    logging.info('Started scheduled_job')
    db = Database()
    logging.debug('Connected to the database')
    poster = Poster()
    logging.debug('Created VK API session')
    checker = DiscountChecker(db)
    discounts = checker.get_discounts()
    logging.info(f'Found {len(discounts)} discounts')
    for discount_id, price_id, discount in discounts:
        try:
            shop_id, item_id = checker.get_item(price_id)
            url, photo_url = checker.get_urls(item_id)
            price = checker.get_price(price_id)[0]
            item_name = checker.get_item_name(item_id)[0]
            shop_name = checker.get_shop_name(shop_id)[0]

            text = f"""
            #{shop_name}\n
            Cкидка {discount}%
            {item_name} за {price}₽.\n
            {url}
            """
            attach = f'{url}'
            if Config.post_photo:
                photo = poster.upload_photo(photo_url)
                attach += f',{photo}'
            poster.post(text, attachments=attach)
            checker.mark_as_posted(discount_id)
            logging.info(f'Successfuly processed discount with ID={discount_id}')
        except Exception:
            logging.warning(f'Discount with ID={discount_id} was not processed', exc_info=True)
            continue
    db.disconnect()
    logging.info('Ended scheduled job')

