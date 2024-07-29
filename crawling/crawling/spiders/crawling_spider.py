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

class CrawlingSpider(CrawlSpider):
    name = "mycrawler_events" # Name of the spider
    allowed_domains = ["catalunyareligio.cat"] # Allowed domains
    start_urls = [#"https://www.catalunyareligio.cat/ca/agenda?page=0",
                  "https://www.catalunyareligio.cat/ca/agenda?page=1",
                  "https://www.catalunyareligio.cat/ca/agenda?page=2",
                  "https://www.catalunyareligio.cat/ca/agenda?page=3",
                  "https://www.catalunyareligio.cat/ca/agenda?page=4",
                  "https://www.catalunyareligio.cat/ca/agenda?page=5",
                  "https://www.catalunyareligio.cat/ca/agenda?page=6",
                  "https://www.catalunyareligio.cat/ca/agenda?page=7",
                  "https://www.catalunyareligio.cat/ca/agenda?page=8",
                  "https://www.catalunyareligio.cat/ca/agenda?page=9",
                  "https://www.catalunyareligio.cat/ca/agenda?page=10",
                  "https://www.catalunyareligio.cat/ca/agenda?page=11",
                  "https://www.catalunyareligio.cat/ca/agenda?page=12",
                  "https://www.catalunyareligio.cat/ca/agenda?page=13",
                  "https://www.catalunyareligio.cat/ca/agenda?page=14"]

    rules = (
        Rule(LinkExtractor(allow="ca/agenda"), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        js = {} # JSON object
        
        title = response.css(".col.my-3.in-node-body span::text").get() # Title event
        js["title"] = title
        event_date_label = response.css(".field__label::text").get() # Data de l'esdeveniment:
        event_date = response.css(".field__item time::attr(datetime)").get() # Event date
        js[event_date_label] = event_date
        event_loc_label = response.css(".field__label::text").getall()[1] # Nom del lloc:
        loc = response.css('.field--name-field-nom-del-lloc .field__item::text').get() # Location
        js[event_loc_label] = loc
        direction_label = response.css(".field__label::text").getall()[2] # Adreça (carrer i número)
        direction = response.css('.field--name-field-direccio .field__item::text').get() # Location
        js[direction_label] = direction
        municipi_label = response.css(".field__label::text").getall()[3] # Municipi
        municipi = response.css('.field--name-field-municipi .field__item::text').get() # Municipi
        js[municipi_label] = municipi
        diocesis_label = response.css(".field__label::text").getall()[4] #"Diòcesi on es realitza l'esdeveniment"
        diocesis = response.css('.field--name-field-territori a::text').get() # diocesis
        js[diocesis_label] = diocesis
        tematica_label = response.css(".field__label::text").getall()[5] # Temática
        tematica = response.css('.field--name-field-seccio .field__items a::text').getall() # Temática value
        combined_text = ' '.join([item.strip() for item in tematica])
        js[tematica_label] = combined_text
        tipus_label = response.css('div.field--name-field-tipus-esdeveniment div.field__item a::text').get() # Tipus d'esdeveniment
        js["Description_typo"] = tipus_label
        description = response.css('div.field--name-field-resum-esdeveniment ::text').get()
        body_paragraphs =response.css('.card-body.fieldset-wrapper p::text').getall()
        full_text = [description.strip()] if description else []
        full_text.extend([p.strip() for p in body_paragraphs if p.strip()])
        comb_text = ' '.join(full_text)
        js["Description"] = comb_text

        yield js
