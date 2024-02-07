import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
#from scraper.items import ScraperItem
import re
from scrapy import Request
from googleScraper.items import ScraperItem
from PIL import Image
import requests
import base64
import os
import json
import uuid
import io
import shutil
import requests 
from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import urlparse
from io import BytesIO
import time

# download the page
# scrapy fetch --nolog https://youtube.com/results?search_query=cdmx > yt2.html
# scrapy shell http://test.com
# scrapy crawl google -a city="brisbane" -a country="australia" -a countryCode="AU" -a lang="en" -a skeyword="brisbane"

class GoogleSpider(scrapy.Spider):
    name = "google"
    rule = (Rule(LinkExtractor(canonicalize=True, unique=True), callback="parse", follow=True))
    #allowed_domains = ["google.com"]
    allowed_domains = ["*"]
    start_urls = ["https://www.google.com/search?q=cdmx&hl=en&tbm=nws"]
    keyword = ""
    country = ""
    CountryCode = ""
    rotate_user_agent = True
    
    def googleSearch_v2(self, query, html):
        g_clean = []
        url = query
        ''' query="{}%20{}".format(self.keyword, self.country)
        url = 'https://www.google.com/search?client=ubuntu&channel=fs&q={}&ie=utf-8&oe=utf-8'.format(query) '''
        try:
            
            html1 = requests.get(url, headers=self.headers)
            #print(url)
            #SAQIB: below write content to file
            self.html_file.write(html.text)
            self.html_file.close()
            #print(html)
            if html1.status_code==200:
                soup = BeautifulSoup(html.text, 'lxml')
                ''' result_div = soup.find_all('div', attrs = {'class': 'e2BEnf U7izfe'})
                print(result_div) '''
                #soup = BeautifulSoup(html.text, "html.parser")
                #print({'soup': soup})
                #rex = re.compile(r'(\d+ mins ago)|(\d+ hour ago)|(\d+ hours ago)|(hace \d+ hora)|(hace \d+ horas)|(hace \d+ min)')
                #rex = re.compile(r'(\d+ mins ago)|([0-4] hour ago)|([0-4] hours ago)|(hace [0-4] hora)|(hace [0-4] horas)|(hace \d+ min)')
                #rex = re.compile(r'^([2-4] hours ago)$|^([1] hour ago)$|(hace \d+ min)|(\d+ min*[a-z] ago)|^(hace [1] hora)$|(hace [2-4] horas)$')
                rex = re.compile(r'^([2-8] hours ago)$|^([1] hour ago)$|(hace \d+ min)|(\d+ min*[a-z] ago)|^(hace [1] hora)$|(hace [2-8] horas)$')                
                x = soup.find_all(string=rex)
                #x = soup.find_all(string=re.compile("hour"))
                
                #x = soup.find_all(string=re.compile("hora"))
                print(len(x))
                #return x
                for j in x:
                    lnk = j.find_parents("a", href=True)
                    print(lnk)
                    i=''
                    k=''
                    if len(lnk)>0:
                        i = lnk[0]
                        k = i['href']
                    ''' else:
                        lnk = j.find_parents("div")
                        print(lnk) '''

                    #print('\n')
                    #print(lnk)
                    #print('{}\n'.format(lnk[0]['href']))
                    try:
                        m = re.search("(?P<url>https?://[^\s]+)", k)
                        n = m.group(0)
                        rul = n.split('&')[0]
                        domain = urlparse(rul)
                        if(re.search('google.com', domain.netloc)):
                            continue
                        else:
                            rul = rul.replace('%3F', '?').replace('%3D','=')
                            #print(rul)
                            g_clean.append(rul)

                    except:
                        continue
        except Exception as ex:
            #print(str(ex))
            return str(ex)
        finally:
            #print(g_clean)
            return g_clean

    def __init__(self, city=None, country=None, countryCode=None, lang=None, skeyword=None, *args, **kwargs):
        super(GoogleSpider, self).__init__(*args, **kwargs)
        country = country.replace(" ", "%20")
        skeyword = skeyword.replace(" ", "%20")
        #merged_keword = "{}%20{}%20news".format(city, country)
        merged_keword = "{}%20{}".format(city, country)
        #self.start_urls = ['https://www.google.com/search?q={}&hl={}&tbm=nws&biw=1440&bih=743&ei=lZcwX5LVFNW0tQaT3bvwAw'.format(skeyword, lang)]
        #self.start_urls = ['http://whatsmyuseragent.org/']
        
        # SAQIB: below is the real one
        self.start_urls = ['https://www.google.com/search?q={}&hl={}&tbm=nws'.format(skeyword, lang)]
        
        # self.start_urls = ['http://noozter.com']
        #self.start_urls = ['https://www.google.com/search?q={}&hl={}'.format(skeyword, lang)]
        # self.start_urls = ['https://news.search.yahoo.com/search?p={}'.format(skeyword)]
        #self.start_urls = ['https://ret.io/r/mx/jal/GDL/cat/trafico/', 'https://ret.io/r/mx/jal/GDL/cat/bloqueos/', 'https://ret.io/r/mx/jal/GDL/cat/inundaciones/']
        # self.start_urls = ['file:///Users/saqib/Downloads/google.htm']
        
        print("Parsing -> %s" % self.start_urls)

        self.city = city
        self.country = country
        self.count = 0
        self.CountryCode = countryCode

        self.path_to_html = 'zindexY.html'
        self.path_to_header = 'zindexY.html'
        self.html_file = open(self.path_to_html, 'w')
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

    def parse_coords(self, response):
        item = response.meta['item']
        print("++++++++++++COORDS++++++++++++++")
        latlon = response.xpath('//*/div[@data-attrid="kc:/location/location:coordinates"]/div/text()').extract()
        yield {"latlon": latlon}
        #latlon = response.xpath('//div[@role="heading"]/div').getall()
        print(latlon)
        #33.7130° N, 73.1615° E
        #if len(latlon)>=1:
        split_coords = str(latlon).split(", ")
        item["lat"] = split_coords[0].split('°')[0].replace("'", "").replace("[", "").replace("]", "")
        item["lon"] = split_coords[1].split('°')[0].replace("'", "").replace("[", "").replace("]", "")
        yield {'lat':item["lat"]}
        yield {'lon':item["lon"]}
        return item

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
            print(link)
            yield {'links': link}
            yield Request(link, callback=self.parse_page, dont_filter=True, meta={'item':item})
        #return item

    def parse(self, response):
        ''' item = ScraperItem()
        item["lat"] = 1
        item["lon"] = 1
        # lnk = 'https://www.eluniversal.com.mx/metropoli/cdmx/imagenes-de-la-tormenta-de-este-viernes-en-la-ciudad-de-mexico'
        lnk = 'https://www.app.com.pk/photos-section/hyderabad-october-28-federal-minister-for-energy-power-division-omar-ayub-khan-governor-sindh-imran-ismail-arbab-ghulam-raheem-and-khurram-sher-zaman-present-in-meeting-of-pti-workers-and-offic/'
        item["links"] = lnk
        yield Request(lnk, callback=self.parse_page, dont_filter=True, meta={'item':item})
        return '''

        #print('Proxy : %s' % response.request.meta['proxy'])
        # print('Headers : %s' % response.request.headers)
        # print('User-Agent : %s' % response.request.headers['User-Agent'])
        links_2 = self.googleSearch_v2(self.start_urls[0], response)
        #return
        yield {'links-1': links_2}
        item = ScraperItem()
        item["links"] = links_2
        item["lat"] = 1
        item["lon"] = 1
        coordinates_search_str = 'https://www.geodatos.net/en/coordinates/{}/{}'.format(self.country , self.city)
        #print(coordinates_search_str)
        yield Request(coordinates_search_str, callback=self.parse_coords2, dont_filter=True, meta={'item':item})
        #user-agent
        #print("current user-agent:{}".format(response.request.headers['User-Agent']))
        #print("Existing settings: %s" % self.settings.attributes.keys())
        ''' for link in links_2:
            #print(link)
            yield {'links': link}
            yield Request(link, callback=self.parse_page, dont_filter=True, meta={'item':item}) '''
        #return
        #########################################################################
    
    def parse_page(self, response):
        images = []
        item = response.meta['item']
        # print(response)
        #headline = response.xpath('//*/h1[@itemprop="headline"]/text()').get()
        #afterHeadline = response.xpath('//*/h2[@class="sp-descp"]/text()').get()
        #images = response.css('img::attr(src)').getall()
        #keywords = response.xpath("//meta[@name='keywords']/@content").get()
        titleLine = response.xpath("//meta[@name='title']/@content").get()
        if not titleLine:
            titleLine = response.xpath("//meta[@property='og:title']/@content").get()

        desc = response.xpath("//meta[@name='description']/@content").get()
        if not desc:
            desc = response.xpath("//meta[@property='og:description']/@content").get()
        if not desc:
            desc = response.xpath("//meta[@property='twitter:description']/@content").get()

        source = response.xpath("//meta[@name='url']/@content").get()
        if not source:
            source = response.xpath("//meta[@property='og:url']/@content").get()
        if not desc:
            desc = titleLine
        
        if len(desc)>22:
            #item["content"] = titleLine + '\n' + desc + '\n' + source        
            item["content"] = "{}\n{}\n{}".format(titleLine, desc, source)

            prohibited_words = ['asesin', 'balazos', 'balacer', 'asalt', ' matar', 'murder', 'muere', 
                'crime', 'arrest', 'protest', 'homicid', 'crimi',
                'assault', 'arrest', 'dead', 'death', 'died']
            if any(word.upper() in item["content"].upper() for word in prohibited_words):
                print('---------------------------------------->>>>>>> Encountered PROHIBITED WORD')
                return
                    
            yield {'content': item["content"]}
            #yield item["content"]
            #self.add_nooz(item['content'])
            # img = response.xpath("//meta[@name='image']/@content").re(r'^.*?(?=\?)') 
            img = [];
            img = response.xpath("//meta[@property='og:image']/@content").getall()
            if not img:
                # img = response.xpath("//meta[@property='og:image']/@content").re(r'^.*?(?=\?)')
                img = response.xpath("//meta[@name='image']/@content").getall()

            # print('1111@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            # print(len(img))
            # print(img)
            # print('1111****************')

            item["image_urls"] = img
            yield {'images1': img}
            images = img #+ imgInBody.css('img::attr(src)').extract()
            # print(len(images))
            #if len(images)>0:
            # print("image length is greater than 1")
            item["image_urls"] = images
            #item['image_urls'] = images[0]
            yield {'images': item["image_urls"]}
            # NEW VERSION
            if img:
                base64image = self.get_as_base64(images[0])
                if base64image is None:
                    images = []
                    print('failed to decode')
                    print(len(images))
                    return
                else:
                    item["base64images"] = base64image
                    # saved_img_path = saveImageToLocalDir()
                    url_dir = response.request.url.split('/')[2]
                    PROJECT_ROOT = os.path.abspath(os.path.dirname('./images/{}/'.format(url_dir)))
                    if not os.path.exists(PROJECT_ROOT):
                        os.makedirs(PROJECT_ROOT)

                    needsScaling = False
                    with open("{}/extractedImage.png".format(PROJECT_ROOT), "wb") as fh:
                        fh.write(base64.decodebytes(base64image))
                        size_in_bytes = os.stat('{}/extractedImage.png'.format(PROJECT_ROOT)).st_size
                        print("size in bytes - extractedImage")
                        print(size_in_bytes)
                        width, height = (0, 0)
                        try:
                            foo = Image.open("{}/extractedImage.png".format(PROJECT_ROOT))
                            width, height = foo.size
                        except Exception as ex:
                            print("Error on image below:")
                            print(images)
                            print(str(ex))
                            return

                        if size_in_bytes < 100000:
                            print("IMAGE W = {}, H = {}". format(width, height))

                            # # foo = foo.resize((600, 1200), Image.BICUBIC)
                            foo = foo.resize((width, height), Image.ANTIALIAS)
                            foo.save("{}/scaledImg.png".format(PROJECT_ROOT),optimize=True,quality=85)
                            size_in_bytes = os.stat('{}/scaledImg.png'.format(PROJECT_ROOT)).st_size
                            print("size in bytes - scaledImg")
                            print(size_in_bytes)
                            msg = BytesIO()
                            with open("{}/scaledImg.png".format(PROJECT_ROOT), "rb") as imageFile:
                                # foo = Image.open("{}/scaledImg.png".format(PROJECT_ROOT))
                                msg = base64.b64encode(imageFile.read())
                                base64image = msg
                                item["base64images"] = base64image
                        elif size_in_bytes > 300000 or height > 300:
                            needsScaling = True
                        else:
                            msg = BytesIO()
                            with open("{}/extractedImage.png".format(PROJECT_ROOT), "rb") as imageFile:
                                # foo = Image.open("{}/scaledImg.png".format(PROJECT_ROOT))
                                msg = base64.b64encode(imageFile.read())
                                base64image = msg
                                item["base64images"] = base64image

                        # return
                    if needsScaling:
                        print("SCALING THE IMAGE..........")
                        ffmpeg_cmd_extract_img = 'ffmpeg -nostdin -loglevel panic -i {}/extractedImage.png -vf "scale=-1:280" {}/scaledImg2.png'.format(PROJECT_ROOT, PROJECT_ROOT)
                        os.system(ffmpeg_cmd_extract_img)
                        msg = BytesIO()
                        with open("{}/scaledImg2.png".format(PROJECT_ROOT), "rb") as imageFile:
                            # foo = Image.open("{}/scaledImg.png".format(PROJECT_ROOT))
                            msg = base64.b64encode(imageFile.read())

                            size_in_bytes2 = os.stat('{}/scaledImg2.png'.format(PROJECT_ROOT)).st_size
                            print("size in bytes2")
                            print(size_in_bytes2)

                        base64image = msg
                        item["base64images"] = base64image
                        # print(base64image)
                    ''' else:
                        msg = BytesIO()
                        with open("{}/scaledImg.png".format(PROJECT_ROOT), "rb") as imageFile:
                            # foo = Image.open("{}/scaledImg.png".format(PROJECT_ROOT))
                            msg = base64.b64encode(imageFile.read())

                        base64image = msg
                        item["base64images"] = base64image '''
                        # print(base64image)

                    if os.path.exists(PROJECT_ROOT):
                        shutil.rmtree(PROJECT_ROOT)
                        print("REMOVED THE DIRECTORY")
                    else:
                        print('directory does not exist')


            #SAQIB: call api to add nooz here...
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print(len(images))
            print(images)
            if len(images)>0:
                self.add_nooz(item)
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            # else:
            #     print("NO DATA TO BE ADDED")

    def add_nooz(self, item):
        #print(item['content'])
        print("add nooz text API HERE....")
        # print(item)
        #print(self.keyword)
        meta = item['content']
        links = item['links']
        #print(meta)
        #print(links)
        #a = json.loads(len(meta))
        # "https://noozterwebapi.azurewebsites.net/api/v1/Documents/%@/noozMedias", NoozId
        url = 'https://api.programmingalternatives.com/api/v1/nooz'
        item['REQ_ID'] = str(uuid.uuid4())
        my_data = {
        "Latitude": item["lat"],
        "Longitude": item["lon"],
        "User":
        {
            "UserId": 3
        },
        "Country": self.country.title(), #"Pakistan",
        "City": self.city.replace('-', ' ').title(),
        "Blurb": meta[0:200],
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
        headers={'Content-Type':'application/json', 'Authorization':'Basic Mzo5ODUxRjgwODNERTI1Q0QwNUFDOTBDMzI4RjQ3MTFENDlDRURGNDE5OEI1NkIzQTZDQkY2MEY4RjBGMjUzREVD'}
        
        # print(my_data)
        try:
            response = requests.post(url, headers=headers, data=json.dumps(my_data))
            response = json.loads(response.text)
            item['NoozId'] = response["NoozId"]
            item['DisplayPosition'] = 1
            self.add_noozMedia(item)
            # print(response)
        except Exception as ex:
            print(str(ex))

    def add_noozMedia(self, item, isImage=True):
        api_url = "https://api.programmingalternatives.com/api/v1/Documents/{}/noozMediasHost".format(item['NoozId'])
        print('api_url = ', api_url)
        # print('item = ', item)
        uuid_append = str(uuid.uuid4())
        boundary = "-------------------------{}".format(uuid_append)
        print('boundary = ', boundary)
        contentType = "multipart/form-data; boundary=%s" % boundary
        print('contentType = ',contentType)

        request_headers = {
            'Authorization': 'Basic Mzo5ODUxRjgwODNERTI1Q0QwNUFDOTBDMzI4RjQ3MTFENDlDRURGNDE5OEI1NkIzQTZDQkY2MEY4RjBGMjUzREVD',
            'Content-Type': contentType
        }
        print(' ==========HEADER========== ')
        print(request_headers)
        body1 = "\r\n--%s\r\n" % boundary
        body2 = "Content-Disposition: form-data; name=model\r\n"
        body3 = "Content-Type: text/plain; charset=UTF-8\r\n\r\n"
        my_data = {
            "Title": "",
            "DisplayPosition": item['DisplayPosition'], 
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
            # print('VIDEO PROCESSING')
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
        try:
            response = base64.b64encode(requests.get(url, headers=headersX, timeout=5).content)
            # response = base64.b64encode(requests.get(url).content)
            #print(response)
            return response
        except requests.exceptions.ConnectionError:
            print("ConnectionError")
            return(None)
        except requests.exceptions.Timeout:
            print("!!!!!!!!!!!!!!! Timeout error !!!!!!!!!!!!!!!!!!")
            #response = base64.b64encode(requests.get(url, headers=self.headers, timeout=5).content)
            return(None)
        except:
            print("Error getting image")
            return(None)
