from lxml import html  # nosec
from io import StringIO
import requests
import logging
import hashlib

logger = logging.getLogger("spider.ofi")

__url__ = "https://www.ouestfrance-immo.com/"
__urls__ = [
    "https://www.ouestfrance-immo.com/acheter/maison/?lieux=24303&rayon=30&prix=0_200000",
    "https://www.ouestfrance-immo.com/acheter/maison/?lieux=24163&rayon=30&prix=0_200000",
    "https://www.ouestfrance-immo.com/acheter/maison/dinard-35-35800/?prix=0_200000",
    "https://www.ouestfrance-immo.com/acheter/maison/lamballe-22-22400/?prix=0_200000",
    "https://www.ouestfrance-immo.com/acheter/maison/guerande-44-44350/?prix=0_200000"
]
# https://www.ouestfrance-immo.com/acheter/maison/vannes-56-56000/?prix=50000_80000&surface=60_0&chambres=3_0

# return_exemple = [
#     {
#         'address': "",
#         "description": "",
#         "price": "",
#         "date": "",
#         "size": "",
#         "groundsurface": "",
#         "extra": {}
#     }
# ]


class ofi(object):

    # data_template = {
    #     "address": "",
    #     "description": "",
    #     "price": "",
    #     "date": "",
    #     "surface": "",
    #     "groundsurface": "",
    #     "url": [],
    #     "photos": [],
    #     "extra": {},
    # }

    def compute_ad(self, url):
        url = "https://www.ouestfrance-immo.com" + url
        xml_str = StringIO(requests.get(url, verify=True).text)
        tree = html.parse(xml_str)
        description = " ".join(tree.xpath('/html/body/div/section/div/div/div[@class=\'txtAnn\']/text()'))
        _id = hashlib.sha1(description.encode('utf-8')).hexdigest()
        price = " ".join(tree.xpath('/html/body/div/section/div/div/strong[@itemprop="price"]/text()'))
        price = price.replace('€', "").strip().replace(" ", "")
        price = int(price)
        address = "".join(tree.xpath('/html/body/div/section/div/div/h2[@id="caractDetail"]/text()')).replace("Vente maison", "").strip()
        ground_surface = " ".join(tree.xpath('/html/body/div/section/div/div/div/ul/li[text()="Surf. terrain : "]/strong/text()')).replace(" ", "")
        try:
            ground_surface = int(ground_surface.replace("m²", ""))
        except ValueError:
            ground_surface = 0
        options = " ".join(tree.xpath('/html/body/div/section/div/div/div/ul/li[@class="options"]/text()'))
        surface = " ".join(tree.xpath('/html/body/div/section/div/div/div/ul/li[text()="Surf. habitable : "]/strong/text()')).replace(" ", "")
        try:
            surface = int(surface.replace("m²", ""))
        except ValueError:
            surface = 0
        date = " ".join(tree.xpath('/html/body/div/section/div/h2/em/text()')).replace(" ", "").split("-")[-1].strip()
        img_urls = map(lambda x: x.get("src"), tree.xpath('//ul/li/img'))
        img_urls = list(filter(lambda x: "photo" in x, img_urls))
        return {
            'id': _id,
            'address': address,
            "description": description,
            "price": price,
            "date": date,
            "surface": surface,
            "groundsurface": ground_surface,
            "url": url,
            "img_urls": img_urls,
            "show": True,
            "extra": {
                "options": options
            },
        }

    def compute(self):
        ads = []
        for url in __urls__:
            xml_str = StringIO(requests.get(url, verify=True).text)

            tree = html.parse(xml_str)

            for _a in tree.xpath('/html/body/div/section/div/div/ul/li/div/a[@class="txt lienDetail"]'):
                # logger.debug(_a.get("href"))
                _ad = self.compute_ad(_a.get("href"))
                ads.append(_ad)
                # logger.debug("ad = {}".format(_ad))

                # addresses = tree.xpath('/html/body//h2/a/span/text()')
                #
                # for _address in addresses:
                #     _dict = {
                #         'address': _address.encode("utf-8"),
                #         "description": "",
                #         "price": "",
                #         "date": "",
                #         "surface": "",
                #         "groundsurface": "",
                #         "url": url,
                #         "extra": {},
                #         }
                #     logger.info("addresses={}".format(_address.encode("utf-8")))
                #     ads.append(_dict)

        return ads

__driver__ = ofi()
