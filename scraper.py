# import requests
from lxml import etree
from contextlib import closing
import psycopg2

import dbconnection

#******should be able to update in addition to the initial pull


def scrapeRecurse():

    recursers = open('Recursers.html')

    parser = etree.HTMLParser()
    tree = etree.parse(recursers, parser)

    #result = etree.tostring(tree.getroot(), pretty_print=True, method = 'html')


    batches = tree.xpath('//*[@id="batches"]/li')
    for batch in batches:
        bs = BatchScrape(batch)
        personsList = bs.getPersonsList()
        dp = DatabasePersons(personsList)
        dp.databasePersons()

class BatchScrape():
    def __init__(self, batch):
        self.batch = batch
        self.personsList = []

    def getPersonsList(self):
        self.getBatchDetails()
        self.getPeopleInBatch()
        return self.pullPeople()

    def getPeopleInBatch(self):
        self.people = self.batch.xpath('ul/li[@class="person"]')

    def getBatchDetails(self):
        self.batchDate = self.batch.xpath('h2/@title')[0]
        self.batchTitle = self.batch.xpath('h2/text()')[0].replace("\n","")
        self.personsList.append([self.batchDate, self.batchTitle])

    def pullPeople(self):
        def xPathForInfo(info, a="/a"):
            info = person.xpath('div[@class="{}"]{}/text()'.format(info, a))
            if info:
                return info[0]
            else:
                return None

        def parseLinks(links):
            linkDict = {}
            for link in links:
                if 'twitter' in link:
                    linkDict['Twitter'] = link.replace("https://twitter.com/","")
                elif 'github' in link:
                    linkDict['GitHub'] = link.replace("https://github.com/","")
                elif 'mailto' in link:
                    linkDict['Email'] = link.replace('mailto:','')
            return linkDict

        for person in self.people:
            personsDict = {}
            personsDict['Name'] = xPathForInfo("name")
            phone = xPathForInfo("phone-number")
            pnum = ""

            if phone:
                digitList = [s for s in phone if s.isdigit()]
                if digitList:
                    pnum = ''.join(digitList)

            personsDict['Phone'] = pnum
            personsDict['Job'] = xPathForInfo("job", "")
            skills = person.xpath('span[@class="skills"]/text()')
            if skills:
                personsDict['Skills'] = ", ".join(skills)
            else: personsDict['Skills'] = None

            links = person.xpath('div[@class="icon-links"]/a/@href')
            if links: personsDict['Links'] = parseLinks(links)
            else: personsDict['Links'] = None

            self.personsList.append(personsDict)

        return self.personsList

class DatabasePersons():
    def __init__(self, personsList):
        self.personsList = personsList
        infoList = personsList.pop(0)
        self.batchDate = infoList[0]
        self.batchTitle = infoList[1]

    def databasePersons(self):
        db = dbconnection.start()
        with closing(db.cursor()) as cur:
            for personsDict in self.personsList:
                #print personsDict
                cur.execute('''INSERT INTO recursers
                    (name, phone, job, skills, gitUser, twitterUser, email, batchname)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (personsDict.get('Name'), personsDict.get('Phone'),personsDict.get('Job'),
                    personsDict.get('Skills'),personsDict.get('Links').get('GitHub'),
                    personsDict.get('Links').get('Twitter'),personsDict.get('Links').get('Email'),
                     self.batchTitle,))
            db.commit()
            cur = self.checkBatches(cur)
            db.commit()
        db.close()

    def checkBatches(self, cur):
        batchCheck = cur.execute('SELECT 1 FROM batches WHERE batchname = %s', (self.batchTitle,))
        if not batchCheck:
            cur.execute('''INSERT INTO batches
                    (batchname, batchdate)
                    VALUES (%s, %s)''',
                    (self.batchTitle, self.batchDate))
        return cur

if __name__ == "__main__":
    personsList = scrapeRecurse()


