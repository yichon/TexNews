import re
import requests
from bs4 import BeautifulSoup
from functools import reduce


class NewsPage_MetaClass(type):
    host_map = {}

    def __new__(cls, clsname, superclasses, attributedict):
        # print("clsname: ", clsname)
        # print("superclasses: ", superclasses)
        # print("attributedict: ", attributedict)

        cls_obj = super().__new__(cls, clsname, superclasses, attributedict)
        NewsPage_MetaClass.host_map[attributedict["host"]] = cls_obj
        return cls_obj


class NewsPage(metaclass=NewsPage_MetaClass):
    host = "*"

    def __init__(self, url_s, prox=None, rm_q=True):  # constructor
        self.rm_q = rm_q
        self.url_s = self._checkURL(url_s)  # instance variables
        self.headers = {'accept-encoding': 'gzip',
                        'connection': 'Keep-Alive',
                        'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 11; XT2125-4 Build/RRN31.Q1-20-52-3)',
                        'host': 'null'}
        self.prox = {"http": "socks5h://127.0.0.1:1060", "https": "socks5h://127.0.0.1:1060"}
        self._pre_process()


        # self.__attr2 = attr2  # pseudo-private instance variables

    @staticmethod
    def getHost(url_s):
        return re.compile("(https://)([^/]+)/").search(url_s).group(2)

    @classmethod
    def get(cls, url_s, rm_q=True):
        h = NewsPage.getHost(url_s)
        if NewsPage.host_map.get(h) is not None:
            return NewsPage.host_map[h].get(url_s, rm_q=rm_q)
        else:
            return NewsPage(url_s, rm_q=rm_q)

    def setHeaders(self, headers):
        self.headers = headers
        self._pre_process()
        return self

    def setProxy(self, prox):
        self.prox = prox
        return self

    def setProxyPort(self, port):
        if self.prox.get("http") and self.prox.get("https"):
            self.prox["http"] = re.compile(r":\d+").sub(":" + str(port), self.prox["http"])
            self.prox["https"] = re.compile(r":\d+").sub(":" + str(port), self.prox["https"])
        else:
            print("No Proxy Setting...")
        return self

    def _checkURL(self, url_s):
        if self.rm_q:
            url_s = re.compile(r"(https://[^?]+)").search(url_s).group(1)
        return url_s

    def _pre_process(self):
        self.url_s = self._checkURL(self.url_s)  # __checkURL defined in subclass, or set to default in meta-class
        self.headers['host'] = NewsPage.getHost(self.url_s)
        # re.compile("(https://)([^/]+)/").search(self.url_s).group(2)
        # print("host:", self.headers['host'])

    def _preprocess_response_txt(self, _txt):
        return _txt

    def get_soup(self):
        response = None
        try:
            if self.prox:
                print("-<>-", self.prox[re.compile(r'^http(s)?').search(self.url_s).group()], "-<><>-")
            print("Request '" + self.url_s + "'...")
            response = requests.get(self.url_s, headers=self.headers, proxies=self.prox)
        except:
            raise ConnectionError("Failed to connect to web page...")
        finally:
            if response is not None:
                response.close()
                print("Response Received. \n")
            else:
                print(self.headers['host'])
                print("Response is 'None'...(Check the proxy)")
                return None

        _txt = response.content.decode(encoding="utf-8")
        # print(_txt)

        self._preprocess_response_txt(_txt)
        return BeautifulSoup(_txt, 'html.parser')

    def _escape(self, _str):
        _str = re.compile(r"(?<!\\)([&$%])").sub(r'\\\1', _str)
        _str = re.compile(r"\s?—\s?").sub(r' -- ', _str)
        _str = re.compile(r"\s?−\s?").sub(r' -- ', _str)
        _str = re.compile(r"…").sub(r'...', _str)
        _str = re.compile(r"[’|‘]").sub(r"'", _str)
        _str = re.compile(r"\s'").sub(" `", _str)
        _str = re.compile(r"“").sub(r'"', _str)  # left quote
        _str = re.compile(r"”").sub(r'"', _str)  # right quote
        _str = re.compile(r"\xa0").sub(r' ', _str)  # remove 'non-breaking space'
        _str = re.compile(r"\u200b").sub(r'', _str)  # remove 'ZERO WIDTH SPACE'
        #_str = re.compile(r"\b").sub(r'@', _str)
        _str = re.compile(r"(\")([^\s]{1}[^\"\n]*)(\1)").sub(r'``\2\3', _str)

        return _str

    def _mark(self, soup):
        for br in soup.find_all("br"):
            br.replace_with("@{br}")

    def _mark_convert(self, _txt):
        _txt = re.compile(r"(@{br})+").sub("\n\\\\\\\\\n", _txt)
        return _txt

    def _reshape(self, soup):
        pass

    def _get_title(self, soup):
        _txt = ""
        t = re.sub(r"^\s{2,}", "", soup.h1.get_text().strip())
        t = re.sub(r"\n", "", t)
        _txt = _txt + '\subsubsection{' + t + '} \n'
        _txt = _txt + '\href{' + self.url_s + '}'
        _txt = _txt + '{' + '.' + '} \n'
        return _txt

    def _get_meta(self, soup):
        return ""

    def _get_H2(self, soup):
        return ""

    def _get_summary(self, soup):
        return ""

    def _get_ul_txt(self, _l):
        def _handle_txt(t):
            if re.compile(r'\.\s*$').search(t):
                return t + " "
            else:
                return t + ". "
        _list = [_handle_txt(li.get_text()) for li in _l]
        _txt = reduce(lambda a, b: a + b, _list)
        return _txt

    def _handle_p(self, para):
        _p = re.sub(r"\s{2,}", " ", para.getText().strip())
        return _p

    def _is_p_selected(self, para):
        if re.compile(r'^[\n|\s]+$').fullmatch(para.get_text()):
            return False
        if para.get_text() == '\n' or para.get_text() == '':
            return False
        return True

    def _get_arctile_so(self, soup):
        return soup

    def _get_content(self, soup):
        ps = self._get_arctile_so(soup).find_all('p')
        p_l = [self._handle_p(p) for p in ps if self._is_p_selected(p)]  # ; print(p_l)
        _txt = ""
        _txt = reduce(lambda a, b: a + b + "\n\\\\\n", p_l, _txt) + "\\\\\n"
        soup.get_text()
        # print(_txt)
        return _txt

    def soup_to_tex(self, soup):
        if soup is None:
            return None

        self._mark(soup)
        self._reshape(soup)

        _tex = ""
        _tex = _tex + self._get_title(soup)
        _tex = _tex + self._get_H2(soup)
        _tex = _tex + self._get_meta(soup)
        _tex = _tex + self._get_summary(soup)
        _tex = _tex + self._get_content(soup)

        _tex = self._escape(_tex)
        _tex = self._mark_convert(_tex)
        return _tex

    def get_tex(self):
        _soup = self.get_soup()
        # print(_soup)
        return self.soup_to_tex(_soup)


class ReutersPage(NewsPage):
    host = "www.reuters.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return ReutersPage(url_s)

    def _get_arctile_so(self, soup):
        div = soup.find('div', {"class": re.compile('article-body__content.*')})  # print(div.getText())
        if div is not None:
            return div
        else:
            return soup

    def _get_summary(self, soup):
        ul = soup.find('ul', {"class": re.compile('summary.*')})
        if ul:
            # list = [li.get_text() + ". " for li in ul]
            # _txt = reduce(lambda a, b: a + b, list)
            _txt = self._get_ul_txt(ul)
            return "Summary: " + _txt + "\n\\\\\n"
        return super()._get_meta(soup)

    def _handle_p(self, para):
        _txt = super()._handle_p(para)
        _txt = re.compile(r"read more$").sub("", _txt)
        # if para.a and para.a.get_text() == "read more":
        #    para.a.decompose()
        return _txt




class KitcoPage(NewsPage):
    host = "www.kitco.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return KitcoPage(url_s)

    # def _reshape(self, soup):
    # eles = soup.article.find("img")
    # print(eles)
    # eles.decompose()
    # return soup

    def _get_arctile_so(self, soup):
        div = soup.select_one('p > img')  # print(div.getText())
        # html = str(div)
        # print(html)
        if div is not None and len(div.find_all("p")) > 0:
            # print(div)
            # print()
            return div
        elif soup.article is not None:
            # print("hello")
            return soup.article
        else:
            # print("hello")
            return soup

    # def _mark(self, soup):
    #    pass


class FoxnewsPage(NewsPage):
    host = "www.foxnews.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return FoxnewsPage(url_s)

    def _get_arctile_so(self, soup):
        div = soup.find("div", {"class": re.compile('article-body')})  # print(div.getText())
        if div is not None:
            return div

        return soup

    def _get_H2(self, soup):
        article = self._get_arctile_so(soup)
        if article.h2 is not None:
           return article.h2.get_text() + '. \n\\\\\n'
        else:
           return ""

    def _is_p_selected(self, para):
        if para.a and len(para.get_text()) == len(para.a.get_text()):
            return False
        return super(FoxnewsPage, self)._is_p_selected(para)



class FoxbusinessPage(FoxnewsPage):
    host = "www.foxbusiness.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return FoxbusinessPage(url_s)

    def _get_arctile_so(self, soup):
        div = soup.find("article", {"class": re.compile('article-wrap')})
        if div is not None:
            # print("'article-wrap' found")
            return div
        # print("Failed to find 'article-wrap'")
        return soup



class BloombergPage(NewsPage):
    host = "www.bloomberg.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return BloombergPage(url_s)

    def _get_summary(self, soup):
        ul = soup.find('ul', {"class": re.compile('abstract_.*')})
        if ul:
            _txt = self._get_ul_txt(ul)
            return "Abstract: " + _txt + "\n\\\\\n"
        return super()._get_meta(soup)

    def _get_arctile_so(self, soup):
        div = soup.find("div", {"class": re.compile('body-content.*')})  # print(div.getText())
        if div is not None:
            return div
        else:
            return soup



class CNBCPage(NewsPage):
    host = "www.cnbc.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return CNBCPage(url_s)

    def _get_arctile_so(self, soup):
        div = soup.find("div", {"class": re.compile('PageBuilder-pageWrapper')})  # print(div.getText())
        if div is not None:
            return div
        else:
            return soup

    def _get_summary(self, soup):
        div = soup.find("div", {"class": re.compile('RenderKeyPoints-list')})
        ul = None
        if div:
            ul = div.find('ul')
        if ul:
            _txt = self._get_ul_txt(ul)
            return "Key Points: " + _txt + "\n\\\\\n"
        return super()._get_meta(soup)

    def _reshape(self, soup):
        for div in soup.find_all("div", {'class': 'RelatedQuotes-relatedQuotes'}):
            div.decompose()
        return soup



class JpmorganPage(NewsPage):
    host = "www.jpmorgan.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return JpmorganPage(url_s)

    def _get_arctile_so(self, soup):
        div = soup.find("div", {"class": "article__body__text"})  # print(div.getText())
        if div is not None:
            return div
        else:
            return soup

    def _reshape(self, soup):
        for h3 in soup.find_all("h3"):
            new_p = BeautifulSoup("<p>" + h3.get_text() + "</p>", 'html.parser')
            h3.replace_with(new_p.p)

        for li in soup.find_all("li"):
            new_p = BeautifulSoup("<p>" + li.get_text() + "</p>", 'html.parser')
            li.replace_with(new_p.p)

        for div in soup.find_all("div", {"class": "quote"}):
            new_p = BeautifulSoup("<p>" + div.get_text() + "</p>", 'html.parser')
            div.replace_with(new_p.p)

        return soup

    def _get_H2(self, soup):
        h2 = soup.find("h2", {"class": re.compile('article__body__subhead.*')})
        if h2 is not None:
            # print("H2 is not None: " + h2.get_text())
            return h2.get_text().strip() + '. \n\\\\\n'
        else:
            return ""

class DWPage(NewsPage):
    host = "www.dw.com"

    @classmethod
    def get(cls, url_s, rm_q=True):
        return DWPage(url_s).setHeaders({'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'en-US,en;q=0.9',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'connection': 'Keep-Alive',
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
           'host': 'www.dw.com'})



if __name__ == '__main__':
    hs_ = {'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'en-US,en;q=0.9',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'connection': 'Keep-Alive',
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
           'host': 'www.reuters.com'}

    addr = "https://www.reuters.com/markets/europe/ecb-tells-banks-factor-recession-shareholder-payouts-2022-07-07/"




    print(NewsPage.host_map)
    np = NewsPage.get(addr)
    # np = NewsPage.get(addr, False)
    print(np.__class__, "selected")

    # txt = np.setProxyPort(1099).get_tex()
    txt = np.setProxyPort(1060).setHeaders(hs_).get_tex()
    print(txt)
    
    
    
    
    
