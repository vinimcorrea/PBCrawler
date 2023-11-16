# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Producto(scrapy.Item):
    nombre = scrapy.Field()
    precio = scrapy.Field()
    descripcion = scrapy.Field()
    tallas = scrapy.Field()
    url_producto = scrapy.Field()
    url_foto = scrapy.Field()
