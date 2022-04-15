import scrapy, telegram
from urllib.parse import urlencode

class CourseSpider(scrapy.Spider):
    name = "courses"
    link_limit = 4

    def closed(self,reason):
        if reason == 'finished':
            self.tel_bot.send_message(text='scrapping is done!', chat_id = self.user_id)
        else:
            self.tel_bot.send_message(text='Some error occured! \n Please try again later!', chat_id = self.user_id)

    def start_requests(self):
        # parsing query argument
        q_arg = self.query
        q = urlencode({'s': q_arg})
        # tel bot init
        self.tel_bot = telegram.Bot(token = self.crawler.settings.get('TEL_BOT_ID'))
        self.tel_bot.send_message(text='Scrapping process started!', chat_id = self.user_id)
        # sites to scrap
        sites_get = [
            {
                'url': f'https://tutsnode.net/?{q}',
                'callback': self.parse_tutsnode
            },
            {
                'url': f'https://freetutsdownload.com/?{q}',
                'callback': self.parse_freetuts
            },
            {
                'url': f'https://coursedrive.org/?{q}',
                'callback': self.parse_coursedrive
            },
            {
                'url': f'https://www.1337xx.to/sort-category-search/{q_arg}/Other/seeders/desc/1/',
                'callback': self.parse_1337x
            },
        ]
        sites_post = [
            {
                'url': 'https://tetacourse.com/',
                'callback': self.parse_tetacourse,
                'body': urlencode({'story': q_arg, 'do': 'search', 'subaction': 'search'})
            },
        ]
        for site in sites_get[:-1]:
            yield scrapy.Request( url= site['url'], callback= site['callback'] )
            
        for site in sites_post:
            yield scrapy.Request(
                url= site['url'],
                callback= site['callback'],
                method= 'POST',
                body= site['body'],
                headers= { "Content-Type": "application/x-www-form-urlencoded"}
            )

    def parse_tutsnode(self, response):
        links = response.xpath("//h2[@class='entry-title']/a/@href").getall()
        for link in links[:self.link_limit]:
            yield scrapy.Request( url= link, callback= self.parse_tutsnode_content )

    def parse_tutsnode_content(self, response):
        yield {
            'title': response.xpath("//h1[@class='entry-title']/text()").get(),
            'date': response.xpath("//p/strong[starts-with(text(), 'Last Updated')]/text()").get(),
            'links': response.xpath("//p/strong[contains(text(),'Direct Download')]/parent::p/following-sibling::blockquote[1]/p/a/@href").getall(),
            'size': response.xpath("//p/strong[contains(text(),'Direct Download')]/parent::p/following-sibling::blockquote[1]/p/text()").get(),            
        }

    def parse_freetuts(self, response):
        links = response.xpath("//h4/a/@href").getall()
        for link in links[:self.link_limit]:
            yield scrapy.Request( url= link, callback= self.parse_freetuts_content )
    
    def parse_freetuts_content(self, response):
        yield {
            'title': response.xpath("//h1/text()").get(),
            'date': response.xpath("//header[@class='entry-header']/div/div[last()]/a/span[2]/text()").get(),
            'links': response.xpath("//div[@class='entry-content']//p//a[not(starts-with(@href,'https://freetutsdownload.com')) and @target='_blank']/@href").getall(),
        }

    def parse_coursedrive(self, response):
        links = response.xpath("//article/div/h2/a/@href").getall()
        for link in links[:self.link_limit]:
            yield scrapy.Request( url= link, callback= self.parse_coursedrive_content )
    
    def parse_coursedrive_content(self, response):
        yield {
            'title': response.xpath("//h1/span/text()").get(),
            'date': response.xpath("//span[@class='time']/time/b/text()").get(),
            'links': response.xpath("//article//h5[starts-with(text(),'Direct Download')]/following-sibling::blockquote[1]//a/@href").getall() + response.xpath("//article/div/p/a[ not(contains(text(),'Visit')) ]/@href").getall() + response.xpath("//article//a[contains(text(),'Visit')]/parent::p/following-sibling::p[1]/a/@href").getall(),      
        }
    
    def parse_tetacourse(self, response):
        links = response.xpath("//h2/a/@href").getall()
        for link in links[:self.link_limit]:
            yield scrapy.Request( url= link, callback= self.parse_tetacourse_content )
    
    def parse_tetacourse_content(self, response):
        yield {
            'title': response.xpath("//h1/b/text()").get(),
            'date': response.xpath("//div/b[starts-with(text(), 'Last Update') or starts-with(text(), 'Last updated')]/text()").get(),
            'links': response.xpath("//div[contains(text(),'Source: ')]/preceding-sibling::div[1]/a[1]/@href").getall(),      
            'size': response.xpath("//div/b[starts-with(text(),'Size') or contains(text(),'GB')]/text()").getall(),  
        }

    def parse_1337x(self, response):
        links = response.xpath("//tbody/tr/td[1]/a[2]/@href").getall()
        for link in links[:self.link_limit]:
            yield response.follow(link, callback=self.parse_1337x_content)
    
    def parse_1337x_content(self, response):
        return {
                'title': response.xpath("//h1/text()").get(),
                'magnet': response.xpath("//ul/li[1]/a[@id='down_magnet']/@href").get(),
                'date': response.xpath("//li/strong[contains(text(),'Date uploaded')]/following-sibling::span/text()").get(),
                'seeders': response.xpath("//li/strong[contains(text(),'Seeders')]/following-sibling::span/text()").get(),
                'size': response.xpath("//li/strong[contains(text(),'Total size')]/following-sibling::span/text()").get(),
            }   
    