import time
import subprocess

def run_crawler():
    subprocess.run(["scrapy", "crawl", "PBSpider"]) 

def schedule_crawler():

    while True:
        run_crawler()
        print("working")
        
        time.sleep(7200)


if __name__ == "__main__":
    schedule_crawler()
