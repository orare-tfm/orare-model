from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

class CrawlingSpider(CrawlSpider):
    name = "mycrawler" # Name of the spider
    allowed_domains = ["esglesia.barcelona"] # Allowed domains
    start_urls = ["https://esglesia.barcelona/es/parroquia/"] # Starting URL

    rules = (
        Rule(LinkExtractor(allow="es/parroquies"), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        js = {} # JSON object
        # Extract title
        js["parroquia"] = response.css(".parish__title::text").get().strip()
        # Información general de la parroquia
        item1 = response.css(".parish__dl").getall()
        sel = Selector(text=item1[0])
        direccion =  sel.xpath('//dt[text()="Dirección"]/following-sibling::dd[1]/text()').get().strip()
        codigo_postal_city = sel.xpath('//dt[text()="Dirección"]/following-sibling::dd[2]/text()').get().strip()
        telefono = sel.xpath('//dt[text()="Teléfono"]/following-sibling::dd[1]/text()').get().strip()
        # Extract Web
        try:
            web = sel.xpath('//dt[text()="Web"]/following-sibling::dd[1]/a/text()').get().strip()
        except:
            web = ""
        # Process extracted data
        codigo_postal, city = codigo_postal_city.split(maxsplit=1)
        js["direccion"] = direccion
        js["codigo_postal"] = codigo_postal
        js["city"] = city
        js["telefono"] = telefono
        js["web"] = web
        # Horarios de misas, descripción, actividades...
        items2 = response.css(".accordion-item").getall() 
        for item in items2:
            sel = Selector(text=item)
            t = sel.css(".accordion-title span::text").get() # Title
            vec = sel.css(".accordion-inner::text, .accordion-inner br::text").getall() # Content
            js[t] = vec
        yield js