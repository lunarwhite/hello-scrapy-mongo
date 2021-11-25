# hello-scrapy-mongo
A simple crawler demo for stackoverflow.com newest questions, using Python Scrapy. MongoDB as Pipeline.

## 1 Setup envs

### 1.1 mongodb

- install

  ```shell
  # Import the public key used by the package management system
  wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
  
  # Create a list file for MongoDB
  echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
  
  # Reload local package database
  sudo apt-get update
  
  # Install the MongoDB packages
  sudo apt-get install -y mongodb-org
  ```

- run/stop

  ```shell
  # Start MongoDB
  sudo systemctl start mongod
  
  # Verify that MongoDB has started successfully
  sudo systemctl status mongod
  
  # Stop MongoDB
  sudo systemctl stop mongod
  
  # Restart MongoDB
  sudo systemctl restart mongod
  
  # Begin using MongoDB
  mongosh
  ```

### 1.2 python

- check version

  ```shell
  python3 -V
  ```

- create virtual env

  ```shell
  python3 -m venv .venv
  source .venv/bin/activate
  
  # deactivate
  ```
  
- pkg: `scrapy`

  ```shell
  pip install scrapy
  ```

- pkg: `pymongo`

  ```shell
  python3 -m pip install 'pymongo[srv]'
  ```

- dependency

  ```shell
  pip freeze > requirements.txt
  ```

## 2 Run demo

### 2.1 init project

- start project

  ```shell
  scrapy startproject hello
  ```

- project structure

  ```shell
  .
  ├── scrapy.cfg # config file
  └── hello
      ├── __init__.py
      ├── items.py # data structure
      ├── middlewares.py
      ├── pipelines.py
      ├── settings.py
      └── spiders # directory put your spiders
          ├── __init__.py
          └── hello_spider.py
  ```

### 2.2  define item

- example

  ```python
  # items.py
  
  import scrapy
  
  class HelloItem(scrapy.Item):
      title = scrapy.Field()
      url = scrapy.Field()
      pass
  ```

### 2.3 make spider

- example

  ```python
  # hello_spider.py
  
  import scrapy
  from hello.items import HelloItem
   
  
  class HelloSpider(scrapy.Spider):
      name = "hello"
      allowed_domains = ["stackoverflow.com"]
      start_urls = [
          "http://stackoverflow.com/questions?pagesize=50&sort=newest",
      ]
   
      def parse(self, response):
          questions = response.xpath('//div[@class="summary"]/h3')
   
          for question in questions:
              item = HelloItem()
              item['title'] = question.xpath('a[@class="question-hyperlink"]/text()').extract()[0]
              item['url'] = question.xpath('a[@class="question-hyperlink"]/@href').extract()[0]
              yield item
  ```

### 2.4 use pipeline

- import rules in setting.py

  ```python
  ITEM_PIPELINES = {'hello.pipelines.MongoDBPipeline': 300}
  
  MONGODB_HOST = "localhost"
  MONGODB_PORT = 27017
  MONGODB_DB = "hello"
  MONGODB_COLLECTION = "questions"
  ```

- example

  ```python
  # pipeline.py
  
  import pymongo
  from scrapy.exceptions import DropItem
  from scrapy.utils.project import get_project_settings
  
  class MongoDBPipeline(object):
      
      def __init__(self):
          settings = get_project_settings()
          connection = pymongo.MongoClient(
              settings['MONGODB_HOST'],
              settings['MONGODB_PORT']
          )
          db = connection[settings['MONGODB_DB']]
          self.collection = db[settings['MONGODB_COLLECTION']]
   
      def process_item(self, item, spider):
          isValid = True
          for data in item:
              if not data:
                  isValid = False
                  raise DropItem("Missing {0}!".format(data))
          if isValid:
              self.collection.insert(dict(item))    
          return item
  ```

### 2.5 deploy

- run crawler

  ```shell
  cd hello/
  scrapy crawl hello
  ```

- show db file

  ```shell
  mongosh
  show dbs
  use hello
  
  show collections
  db.questions.find().pretty()
  ```

## 3 Misc

### 3.1 选择考量
- 数据库 mongodb
- 语言&框架 python scrapy  
### 3.2 references
- https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
- https://docs.mongodb.com/drivers/pymongo/
- https://www.runoob.com/mongodb/mongodb-tutorial.html
- https://docs.scrapy.org/en/latest/
- https://docs.scrapy.org/en/latest/topics/settings.html
- https://docs.scrapy.org/en/latest/topics/items.html
- https://doc.scrapy.org/en/latest/topics/item-pipeline.html
- https://docs.scrapy.org/en/latest/topics/spiders.html
