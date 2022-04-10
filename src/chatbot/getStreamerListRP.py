import scrapy

class rpSpider(scrapy.Spider):
    name = 'rpSpider'
    allowed_domains = ['nopixel.hasroot.com']
    start_urls = ['https://nopixel.hasroot.com/streamers.php']
    
    def parse(self, response):
        streamers = response.xpath('//div[@class="streamerInfo"]/@data-streamername').extract()
        with open('streamers.txt', 'w') as f:
            for i in streamers:
                f.write(f'{i}\n')

