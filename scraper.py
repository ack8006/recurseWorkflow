# import requests
from lxml import etree
from contextlib import closing
import psycopg2

import dbconnection


def scrapeRecurse():

    recursers = open('Recursers.html')

    parser = etree.HTMLParser()
    tree = etree.parse(recursers, parser)

    #result = etree.tostring(tree.getroot(), pretty_print=True, method = 'html')

    people = tree.xpath('//*[@class="person"]')

    personDict = pullPeople(people)
    return personDict


def pullPeople(people):
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
    personsList=[]

    for person in people:
        personsDict = {}
        personsDict['Name'] = xPathForInfo("name")
        phone = xPathForInfo("phone-number")
        pnum = ""

        #***** THIS NEEDS TO BE DEALT WITH problem if string no nums
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

        personsList.append(personsDict)

    return personsList


def databasePersons(personsList):
    db = dbconnection.start()
    with closing(db.cursor()) as cur:
        for personsDict in personsList:
            #print personsDict
            cur.execute('''INSERT INTO recursers
                (name, phone, job, skills, gitUser, twitterUser, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (personsDict.get('Name'), personsDict.get('Phone'),personsDict.get('Job'),
                personsDict.get('Skills'),personsDict.get('Links').get('GitHub'),
                personsDict.get('Links').get('Twitter'),personsDict.get('Links').get('Email')))

        db.commit()
    db.close()

if __name__ == "__main__":
    personsList = scrapeRecurse()
    databasePersons(personsList)


