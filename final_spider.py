import scrapy
import json
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

start_date = 41640 #01-01-2014
end_date = 42370   #31-12-2015 42369    +1 for range
base_links = []
links = []
x = start_date

def TimeLinks():
    for x in range(start_date,end_date):
        text = "https://economictimes.indiatimes.com/archivelist/year-2014,month-1,starttime-"+str(x)+".cms"
        base_links.append(text)


class LinksSpider(scrapy.Spider):
    name = "links"
    allowed_domains = ['economictimes.indiatimes.com']

    def start_requests(self):
        for url in base_links:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        
        no_of_links = len(response.xpath("//ul[@class='content']//@href"))
        head = "https://economictimes.indiatimes.com"
        for i in range(0,no_of_links):
            link_txt = head + response.xpath("//ul[@class='content']//@href").extract()[i]
            links.append(link_txt)


class NewsSpider(scrapy.Spider):
    name = "news"

    def start_requests(self):
        for url in links:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self,response):
        for quote in response.xpath(".//article"):
            no_of_sect = len(quote.xpath("div[@class='artText']/div"))
            txt = []

            for i in range(0,no_of_sect):
                txt = txt + quote.xpath("//div[@class='section"+str(i+1)+"']/div//text()").extract()    
            title = quote.xpath("//h1[@class='clearfix title']//text()").extract()
            date = quote.xpath("//div[@class='publish_on flt']//text()").extract()

            final_title = "".join(map(str,title))
            final_date = "".join(map(str,date))
            final_text = "".join(map(str,txt))
            
            yield {
                'title': final_title ,
                'date': final_date ,
                'content': final_text
            }


settings = get_project_settings()
settings.overrides['FEED_FORMAT'] = 'json'
settings.overrides['FEED_URI'] = 'result5.json'

configure_logging()
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(LinksSpider)
    yield runner.crawl(NewsSpider)
    reactor.stop()

TimeLinks()
crawl()
reactor.run()
