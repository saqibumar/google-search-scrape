import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
#from scraper.items import ScraperItem
import re
from scrapy import Request
from googleScraper.items import ScraperItem
from PIL import Image
import base64
import os
import json
import uuid
import io

import requests 
from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import urlparse
from urllib.request import urlopen
from io import BytesIO
# import m3u8
# from selenium import webdriver
# import pafy
# import youtube_dl

# import ffmpy

# scrapy crawl others -a city="guadalajara" -a country="mexico" -a countryCode="MX" -a lang="es" -a skeyword=""
class OthersSpider(scrapy.Spider):
    name = "others"
    rule = (Rule(LinkExtractor(canonicalize=True, unique=True), callback="parse", follow=True))
    #allowed_domains = ["google.com"]
    allowed_domains = ["*"]
    start_urls = ['https://ret.io/r/mx/jal/GDL/cat/trafico/'] #, 'https://ret.io/r/mx/jal/GDL/cat/bloqueos/', 'https://ret.io/r/mx/jal/GDL/cat/inundaciones/']
    keyword = ""
    country = ""
    CountryCode = ""
    rotate_user_agent = True

    def other_pages(self, query, html):
        url = query
        html1 = requests.get(url)
        
        ''' self.html_file.write(html.text)
        self.html_file.close() '''
        #print(html)
        if html1.status_code==200:
            soup = BeautifulSoup(html.text, 'lxml')
            rex = re.compile(r'(\d+ mins ago)|(\d+ hour ago)|(\d+ hours ago)|(hace \d+ hora)|(hace \d+ horas)|(hace \d+ min)')
            x = soup.find_all(string=rex)
        print(len(x))
        for j in x:
            div = j.find_parents("div")
            print(div)

    def __init__(self, city=None, country=None, countryCode=None, lang=None, skeyword=None, *args, **kwargs):
        super(OthersSpider, self).__init__(*args, **kwargs)
        country = country.replace(" ", "%20")
        skeyword = skeyword.replace(" ", "%20")
        #merged_keword = "{}%20{}%20news".format(city, country)
        merged_keword = "{}%20{}".format(city, country)
        # self.start_urls = ['http://noozter.com'] #['https://ret.io/r/mx/jal/GDL/cat/trafico/', 'https://ret.io/r/mx/jal/GDL/cat/bloqueos/', 'https://ret.io/r/mx/jal/GDL/cat/inundaciones/', 'https://ret.io/r/mx/jal/GDL/cat/accidentes/', 'https://ret.io/r/mx/jal/ZPP/cat/trafico/', 'https://ret.io/r/mx/jal/ZPP/cat/bloqueos/', 'https://ret.io/r/mx/jal/ZPP/cat/inundaciones/', 'https://ret.io/r/mx/jal/ZPP/cat/accidentes/', 'https://ret.io/r/mx/jal/TPQ/cat/trafico/', 'https://ret.io/r/mx/jal/TPQ/cat/bloqueos/', 'https://ret.io/r/mx/jal/TPQ/cat/inundaciones/', 'https://ret.io/r/mx/jal/TPQ/cat/accidentes/']
        self.start_urls = ['file:///Users/saqib/Downloads/index2.html']
        print("Parsing -> %s" % self.start_urls)
        self.city = city
        self.country = country
        self.count = 0
        self.CountryCode = countryCode
        self.headers = {
            'authority': 'www.google.com',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en,en-US;q=0.9,es;q=0.8',
        }

        ''' self.path_to_html = 'index2.html'
        self.path_to_header = 'index2.html'
        self.html_file = open(self.path_to_html, 'w') '''

    def parse_coords2(self, response):
        item = response.meta['item']
        print("++++++++++++COORDS2++++++++++++++")
        latlon = response.xpath('//*/p[@class="font-bold text-blue-500 mt-3 lg:text-lg"]/text()').extract()
        yield {"latlon": latlon}
        #latlon = response.xpath('//div[@role="heading"]/div').getall()
        print('>>>>')
        print(latlon)
        print('<<<<<')
        #33.7130° N, 73.1615° E
        #if len(latlon)>=1:
        split_coords = str(latlon).split(", ")
        item["lat"] = split_coords[0].split('°')[0].replace("'", "").replace("[", "").replace("]", "")
        item["lon"] = split_coords[1].split('°')[0].replace("'", "").replace("[", "").replace("]", "")
        yield {'lat':item["lat"]}
        yield {'lon':item["lon"]}
        for link in item["links"]:
            #print(link)
            yield {'links': link}
            yield Request(link, callback=self.parse_page, dont_filter=True, meta={'item':item})
        #return item

    def parse(self, response):
        import json
        search_str = 'cdmx'
        video_search_str = 'https://www.youtube.com/results?search_query={}'.format(search_str)
        print("++++++++++++YOUTUBE++++++++++++++")
        return
        

    def parse_page(self, response):
        item = response.meta['item']
        print(response)
        headline = response.xpath('//*/h1[@itemprop="headline"]/text()').get()
        afterHeadline = response.xpath('//*/h2[@class="sp-descp"]/text()').get()
        #imgLoc = response.xpath('//*/img[@id="previewImg"]').get()
        images = response.css('img::attr(src)').getall()
        keywords = response.xpath("//meta[@name='keywords']/@content").get()
        #print("+++++++++++++++++++++keywords++++++++++")
        #print(keywords)
        titleLine = response.xpath("//meta[@name='title']/@content").get()
        if not titleLine:
            titleLine = response.xpath("//meta[@property='og:title']/@content").get()

        desc = response.xpath("//meta[@name='description']/@content").get()
        if not desc:
            desc = response.xpath("//meta[@property='og:description']/@content").get()

        source = response.xpath("//meta[@name='url']/@content").get()
        if not source:
            source = response.xpath("//meta[@property='og:url']/@content").get()

        item["content"] = titleLine + '\n' + desc + '\n' + source
        yield {'content': item["content"]}
        #yield item["content"]
        #self.add_nooz(item['content'])
        img = response.xpath("//meta[@property='og:image']/@content").getall()
        item["image_urls"] = img
        yield {'images1': img}
        #print(img)
        imgInBody = response.xpath("//*/div[@class='story-body']//figure")
        #imgInBody = imgInBody.xpath("//*/span[@class='image-and-copyright-container']")
        #imgInBody = imgInBody.css('img::attr(src)')
        #imgInBody = imgInBody.xpath('//img/@src')
        #print(imgInBody.getall())

        images = img + imgInBody.css('img::attr(src)').extract()
        item["image_urls"] = images
        #item['image_urls'] = images[0]
        yield {'images': item["image_urls"]}
        base64images = []
        for image in images:
            #print(image)
            item["images"] = image
            imageX64 = self.get_as_base64(image)
            base64images.append(imageX64)
        item["base64images"] = base64images
        #print("No. of IMAGES = %d" % len(item["base64images"]))
        url_dir = response.request.url.split('/')[2]
        PROJECT_ROOT = os.path.abspath(os.path.dirname('./images/{}/'.format(url_dir)))
        if not os.path.exists(PROJECT_ROOT):
            os.makedirs(PROJECT_ROOT)
        #print("++++++++++ NO OF IMAGES = %d" % len(base64images))
        #print(base64.decodebytes(base64images[0]))

        for i, itemImg in enumerate(base64images):
            #print(os.path.exists("{}/extractedImageToSave{}.png".format(PROJECT_ROOT, i)))
            with open("{}/extractedImageToSave{}.png".format(PROJECT_ROOT, i), "wb") as fh:
                #if not os.path.exists("{}/extractedImageToSave{}.png".format(PROJECT_ROOT, i)):
                fh.write(base64.decodebytes(itemImg))
        #print(' ')
        #yield item
        
        #SAQIB: call api to add nooz here...
        self.add_nooz(item)

    def add_nooz(self, item):
        #print(item['content'])
        print("add nooz text API HERE....")
        #print(item)
        #print(self.keyword)
        meta = item['content']
        links = item['links']
        #print(meta)
        #print(links)
        #a = json.loads(len(meta))
        # "https://noozterwebapi.azurewebsites.net/api/v1/Documents/%@/noozMedias", NoozId
        url = 'https://noozterwebapi.azurewebsites.net/api/v1/nooz'
        item['REQ_ID'] = str(uuid.uuid4())
        my_data = {
        "Latitude": item["lat"],
        "Longitude": item["lon"],
        "User":
        {
            "UserId": 428
        },
        "Country": self.country.title(), #"Pakistan",
        "City": self.city.replace('-', ' ').title(),
        "Blurb": meta,
        "Story": meta,
        "CountryCode": self.CountryCode,
        "ShareLocation": 1,
        "IsPublished": 1,
        "REQ_ID": item['REQ_ID'], #str(uuid.uuid4()) #"2E11CA3D-7FE8-43DC-A159-B99DDB95856B"
        "DeviceInfo": "Scrapy"
        }
        #request = Request(url, method='POST', body=json.dumps(my_data), headers={'Content-Type':'application/json'} )
        #response = requests.post(request)
        #print(request)
        #headers={'Content-Type':'application/json', 'Authorization':'Basic NTA6RTAwM0ZDNTM3NUU4QjNCNkQxNjczMUY0QzE3MEMxMDYwNTRGQTgzMENFMjA4QjRDQzkzMTMwNTU5QzcxMjY2RQ=='}
        #headers={'Content-Type':'application/json', 'Authorization':'Basic NDI4OkY0MjhDMTEyQjhERDI0MjU1NUU4NTAxOTAyNjdCQUMwRDkxQTdFOEZFNkNFNkY3RjZGREI2Nzg0NEYzQzI4Njc='}
        headers={'Content-Type':'application/json', 'Authorization':'Basic NDI4OjJBNjkxNEM3NTU0MUQ4NDg3REMyMEVENkFCQ0E2MjM3Q0YwMjc1RkE3NEJBMDY0NkIwNUE5ODhDQTlGNjE2NkE='}
        
        #print(my_data)
        try:
            response = requests.post(url, headers=headers, data=json.dumps(my_data))
            response = json.loads(response.text)
            item['NoozId'] = response["NoozId"]
            self.add_noozMedia(item)
            print(response)
        except Exception as ex:
            print(str(ex))

    def add_noozMedia(self, item, isImage=True):
        api_url = "https://noozterwebapi.azurewebsites.net/api/v1/Documents/{}/noozMedias".format(item['NoozId'])
        print(api_url)
        uuid_append = str(uuid.uuid4())
        boundary = "-------------------------{}".format(uuid_append)
        #print(boundary)
        contentType = "multipart/form-data; boundary=%s" % boundary
        #print(contentType)

        request_headers = {
            'Authorization': 'Basic NDI4OjJBNjkxNEM3NTU0MUQ4NDg3REMyMEVENkFCQ0E2MjM3Q0YwMjc1RkE3NEJBMDY0NkIwNUE5ODhDQTlGNjE2NkE=',
            'Content-Type': contentType
        }
        #print(' ==========HEADER========== ')
        #print(request_headers)
        body1 = "\r\n--%s\r\n" % boundary
        body2 = "Content-Disposition: form-data; name=model\r\n"
        body3 = "Content-Type: text/plain; charset=UTF-8\r\n\r\n"
        my_data = {
            "Title": "",
            "DisplayPosition": 1, 
            "REQ_ID":item["REQ_ID"]
        }
        body4 = json.dumps(my_data)
        body5 = "\r\n--%s\r\n" % boundary
        if isImage==True:
            print('IMAGE PROCESSING')
            body6 = "Content-Disposition: form-data; model=\"test123\"; filename=\"123.jpg\"\r\n"
            body7 = "Content-Type: image/jpeg\r\n\r\n"
            img64 = base64.decodebytes(item["base64images"])

        if isImage==False:
            print('VIDEO PROCESSING')
            body6 = "Content-Disposition: form-data; model=\"test123\"; filename=\"123.mp4\"\r\n"
            body7 = "Content-Type: video/mp4\r\n\r\n"
            img64 = item["video"]

        #body8 = img64
        body9 = "\r\n"
        body10 = "--%s--\r\n" % boundary

        #body_data = body1 + body2 + body3 + body4 + body5 + body6 + body7 + body8 + body9 + body10
        #request_body = body_data.encode('UTF-8')
        request_body = body1.encode('UTF-8') + body2.encode('UTF-8') + body3.encode('UTF-8') + body4.encode('UTF-8') + body5.encode('UTF-8') + body6.encode('UTF-8') + body7.encode('UTF-8') + img64 + body9.encode('UTF-8') + body10.encode('UTF-8')
        print(' ==========BODY========== ')
        print(body6.encode('UTF-8'))
        response = requests.post(api_url, headers=request_headers, data=request_body)
        print(response.reason)
        print(response.status_code)
        response = json.loads(response.text)
        print(response)



    def get_as_base64(self, url):
        #url = url.split('?')[0]
        print("START ENCODING {}".format(url))
        try:
            headersX = {
                'authority': 'www.google.com',
                'dnt': '1',
                'upgrade-insecure-requests': '1',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en,en-US;q=0.9,es;q=0.8',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            }
            
            # print(headersX)
            # return
            # response = requests.get(url, timeout=10).content
            response = base64.b64decode(requests.get(url, headers=headersX, timeout=5).content)
            print(response)
            # response = base64.b64encode(requests.get(url).content)
            print("FINISHED")
            return response

        except requests.exceptions.ConnectionError:
            print("ConnectionError")
            return
        except requests.exceptions.Timeout:
            print("Timeout error")
            return
        except:
            print("Error getting image")
            return(None)