import scrapy
import os
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from urllib.parse import urlparse
from urllib import robotparser



class PBSpider(CrawlSpider):
    # Nombre de la araña
    name = "pb"

    # Dominios permitidos
    allowed_domains = ['inditex.grp']
    
    # URLs para comenzar a rastrear
    start_urls = [
        'https://axpreprueccwpslb1-pullandbear.central.inditex.grp/'
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)
    
    def _get_robot_parser(self, url):
        robot_txt_url = urlparse(url)._replace(path='/robots.txt').geturl()
        robot_parser = robotparser.RobotFileParser()
        robot_parser.set_url(robot_txt_url)
        robot_parser.read()
        return robot_parser

    def _is_out_of_stock(self, response, talla):
        is_out_of_stock = response.xpath(f'//div[text()="{talla}"]/following-sibling::div[contains(@class, "product-size-info__show-similar")]/span[@class="product-detail-show-similar-products__text"]/span[text()="Ver similares"]')
        return bool(is_out_of_stock)


    def parse(self, response):

        robot_parser = self._get_robot_parser(response.url)
        if not robot_parser.can_fetch("*", response.url):
            self.logger.info(f"Robots.txt disallows crawling: {response.url}")
            return
        
        producto = {}

        # Extraemos los enlaces
        links = LinkExtractor(
            allow_domains=['inditex.grp'],
            restrict_xpaths=["//a"],
            allow="/es/es"
            ).extract_links(response)

        outlinks = []  # Lista con todos los enlaces
        for link in links:
            url = link.url
            outlinks.append(url) # Añadimos el enlace en la lista
            yield Request(url, callback = self.parse) # Generamos la petición

        product = response.xpath('//meta[@content="product"]').extract()

        
        if product:
            # Extraemos la url, el nombre del producto, la descripcion y su precio
            producto['nombre'] = response.xpath('//h1[@id="titleProductCard"]/text()').extract_first()
            producto['precio'] = response.xpath('//span[@class="number hansolo"]/text()').extract_first()
            producto['descripcion'] = response.xpath('//div[@class="c-product-info"]//p[@class="text"]/text()').extract_first()

            tallas = response.xpath('//ul[@class="size-selector__size-list"]//div[@class="product-size-info__main-label"]/text()').extract()

            tallas_filtradas = []
            for talla in tallas:
                # Check if the size is out of stock
                is_out_of_stock = response.xpath(f'//div[text()="{talla}"]/following-sibling::div[contains(@class, "product-size-info__show-similar")]/span[@class="product-detail-show-similar-products__text"]/span[text()="Ver similares"]')
                if not is_out_of_stock:
                    tallas_filtradas.append(talla)


            producto['tallas'] = tallas_filtradas
                
            producto['url_producto'] = response.url

            producto['url_foto'] = response.xpath('//div[@class="media__wrapper media__wrapper--fill media__wrapper--force-height"]//img[@class="media-image__image media__wrapper--media"]/@src').extract_first()

            yield producto
