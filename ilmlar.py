import os, json, requests, random, sqlite3
from traceback import format_exc
from types import SimpleNamespace

class Ilmlar:

    constants = {}

    def __init__(self):
            try:
                with open('{}/constants.json'.format(os.path.dirname(__file__)), encoding="utf8") as f:
                    self.constants = json.load(f)                  
            except: 
                self.constants = None
                print('Error occured')
            self.pager = 0

    def search(self, keywoard, page_num):
        keyword = keywoard.replace(" ", "+")
        url = '{}{}&page={}&per_page={}'.format(self.constants['web_site']+self.constants['search_params']['search'],keyword, page_num,self.constants['search_params']['def_count'])
        result = requests.get(url)
        
        res = json.loads(result.text, object_hook=lambda d: SimpleNamespace(**d))

        mystr = ''

        j=1
        #print(random.sample(range(0, len(res)),len(res)))
        for i in random.sample(range(0, len(res)),len(res)):
            #mystr += str(j+((page_num-1)*self.constants['search_params']['def_count'])) +'. '+res[i].title + '\n'+res[i].url+'\n\n'
            mystr += '✅ '+res[i].title + '\n'+res[i].url+'\n\n'
             
            j+=1

        return mystr

    def inline_search(self, keywoard):
        keyword = keywoard.replace(" ", "+")
        url = '{}{}&page={}&per_page={}'.format(self.constants['web_site']+self.constants['search_params']['search'],keyword, 1,self.constants['search_params']['def_count'])
        result = requests.get(url)
        
        res = json.loads(result.text, object_hook=lambda d: SimpleNamespace(**d))

        myres = {}

        for i in random.sample(range(0, len(res)),len(res)):
            myres['✅ '+res[i].title] = res[i].url
            

        return myres        

    def add_user(self, uid):
        
        try:
            
            con = sqlite3.connect('{}/{}'.format(os.path.dirname(__file__), self.constants['db_name']))
            cur = con.cursor()
            cur.execute("insert into users values (?,?)", (None,uid))   
            con.commit()         
            con.close()

        except Exception as e:
            print('[db] error on iserting in [users]')

    def count_user(self):
        count = 0
        try:
            con = sqlite3.connect('{}/{}'.format(os.path.dirname(__file__), self.constants['db_name']))
            cur = con.cursor()
            cur.execute("select count(*) from users")
            count = cur.fetchone()[0]
            con.close()

            return count

        except Exception as e:
            return count

    def add_search(self, keyword):
        
        try:
            
            con = sqlite3.connect('{}/{}'.format(os.path.dirname(__file__), self.constants['db_name']))
            cur = con.cursor()
            cur.execute("insert into searchs values (?,?)", (None,keyword))   
            con.commit()         
            con.close()

        except Exception as e:
            print('[db] error on iserting in [search]')            