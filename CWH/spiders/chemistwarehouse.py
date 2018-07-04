# -*- coding: utf-8 -*-
import scrapy
import re

class ChemistwarehouseSpider(scrapy.Spider):
    name = 'chemistwarehouse'
    allowed_domains = ['www.chemistwarehouse.com.au']
    start_urls = ['https://www.chemistwarehouse.com.au/Special-Pages/BestSellers?size=120']
    category_url = 'https://www.chemistwarehouse.com.au/categories'
    best_sellers = []

    def parse(self, response):
        selector = scrapy.Selector(response)
        skus = selector.css('.PageGroupSKUs::attr(value)').extract()
        self.best_sellers = skus

        yield scrapy.Request(
            self.category_url,
            callback = self.parse_categories
        )

    def parse_categories(self, response):
        selector = scrapy.Selector(response)
        links = selector.css('table td[nowrap="nowrap"] a::attr(href)').extract()
        count = 0
        for link in links:
            yield scrapy.Request(
                '{}{}'.format(
                    'https://www.chemistwarehouse.com.au', 
                    link
                ),
                callback = self.parse_category
            )

    def parse_category(self, response):
        selector = scrapy.Selector(response)
        product_urls = selector.css('.product-list-container .product-container::attr(href)').extract()

        for product_url in product_urls:
            yield scrapy.Request(
                'https://www.chemistwarehouse.com.au' + product_url,
                callback = self.parse_product
            )
            
    
    def parse_product(self, response):
        selector = scrapy.Selector(response)
        
        product_name = self.sstrip(selector.css('.productDetail .product-name h1::text').extract_first())
        page_title = self.sstrip(selector.css('head title::text').extract_first())
        meta_description = self.sstrip(selector.css('head meta[name="description"]::attr(content)').extract_first())
        sale_price = self.get_price(selector.css('.productDetail .Price span::text').extract_first())
        retail_price = self.get_price(selector.css('.productDetail .retailPrice::text').extract_first())
        sku = self.get_sku(selector.css('.productDetail .product-id::text').extract_first())
        html_description_full = response.xpath('//div[@class="product-info-container"]').extract_first()
        html_description = self.get_html_description(selector.css('.product-info-container .general-info .details').extract_first())
        image_urls = selector.css('.image_enlarger::attr(href)').extract()
        image_descriptions = selector.css('.image_enlarger::attr(data-title)').extract()
        categories = selector.css('.breadcrumbs a::text').extract()[1:]
        best_seller = 1 if sku in self.best_sellers else 0
        low_stock = 0 if len(response.xpath('//div[contains(@content, "OutOfStock")]').extract()) == 0 else 1

        data = {
            'PRODUCT NAME' : product_name,
            'PAGE TITLE' : page_title,
            'META DESCRIPTION' : meta_description,
            'SALE PRICE' : sale_price,
            'RETAIL PRICE' : retail_price,
            'SKU' : sku,
            'CATEGORY' : '/'.join(categories),
            'BESTSELLER' : best_seller,
            'LOW STOCK' : low_stock,
            'HMTL DESCRIPTION' : html_description,
            'HTML DESCRIPTION(FULL)' : html_description_full, 
            'IMAGE URLS' : image_urls
        }

        for index, image_url in enumerate(image_urls):
            data['IMAGE' + str(index)] = image_url
            data['IMAGE DESCRIPTION' + str(index)] = product_name

        yield data

    def get_html_description(self, str):
        if str == None:
            return ''

        html_description = ''
        matches = re.findall(r'[^\>]+[\<|$]', str)

        for match in matches:
            html_description = html_description + self.sstrip(match[:-1])

        return html_description

    def get_sku(self, str):
        match = re.search(r'\d+', str)
        return match.group()
    
    def get_price(self, str):
        match = re.search(r'(\d)+\.(\d+)', str)
        return match.group()

    def sstrip(self, str):
        if str == None:
            return ''

        str.replace('\n', '')
        str.replace('\t', '')
        str.replace('\r', '')

        return str.strip()


