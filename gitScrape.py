import requests
from contextlib import closing
import datetime


#https://api.github.com/
#/users/:username/received_events/public

#list languages
#GET /repos/:owner/:repo/languages

#list user repos
#GET /users/:username/repos


#*****handle pages
class getGitHubData():
    def __init__(self, username):
        self.username = username

    def getAndLoadData(self, urlInfo):
        data = self.requestData(urlInfo)
        return data

    def requestData(self, urlInfo):
        rpd = RequestPageData(urlInfo)
        data = rpd.requestData()
        return data

    def loadJson(self, data):
        parsedData = json.loads(data)
        return parsedData

    def getUserRepos(self):
        urlInfo = "users/{}/repos".format(self.username)
        data = self.getAndLoadData(urlInfo)
        return data

    def getRecentEvents(self):
        urlInfo = "users/{}/events".format(self.username)
        data = self.getAndLoadData(urlInfo)
        return data


class RequestPageData():
    def __init__(self, urlInfo):
        self.urlInfo = urlInfo

    def createURL(self, urlInfo, page):
        urlBase = "https://api.github.com/"
        url = urlBase + urlInfo + "?page={}".format(str(page))
        return url

    def requestData(self, data=[], pageNum=1):
        url = self.createURL(self.urlInfo, pageNum)
        page = requests.get(url)
        #rare error if exactly 30 items and goes to next page, will not
        #return proper structure, so need to catch that
        if page.json():
            data = data + page.json()
        else: return data
        if len(data)%30 != 0:
            return data
        else:
            pageNum += 1
            return self.requestData(data, pageNum)

class ParseGitData():
    def __init__(self, data):
        self.data = data

    #'PushEvent' 'ForkEvent' 'CreateEvent' 'WatchEvent'
    def parseForTypeEvents(self, eventType):
        typeEvents = [event for event in self.data if event['type']==eventType]
        return typeEvents

    def commitsEachDay(self, numDays=30):
        pushEvents = self.parseForTypeEvents('PushEvent')
        commitDict = {}

        for pEvent in pushEvents:
            createdDate = datetime.datetime.strptime(pEvent['created_at'][0:10], "%Y-%m-%d").date()
            if createdDate < datetime.datetime.now().date()-datetime.timedelta(days=numDays):
                continue
            elif createdDate in commitDict:
                commitDict[createdDate] += len(pEvent['payload']['commits'])
            else:
                commitDict[createdDate] = len(pEvent['payload']['commits'])
        return commitDict

    def getReposWorkedOn(self, numDays=30):
        repoList = list(set([(repo['type'], repo['repo']['name']) for repo in self.data
                         if datetime.datetime.strptime(repo['created_at'][0:10], "%Y-%m-%d").date()
                             >= datetime.datetime.now().date()-datetime.timedelta(days=numDays)]))
        return repoList

    # eventTypes is a list of strings
    # repoList is returned from getReposWorkedOn
    def reposActionedOn(self, eventTypes, repoList):
        repoTypeList = list(set([repo[1] for repo in repoList if repo[0] in eventTypes]))
        return repoTypeList


def testMethod():
    import json

    with open('ack8006Events.html') as dataFile:
        data = json.load(dataFile)
    return data


if __name__ == "__main__":
    #gus = getGitHubData("aaylward")
    gus = getGitHubData("ack8006")
    data = gus.getRecentEvents()

    #data=testMethod()


    pgd = ParseGitData(data)
    commitDict = pgd.commitsEachDay(7)
    repoList = pgd.getReposWorkedOn(7)
    #repos action performed on
    repoTypeList = pgd.reposActionedOn(['PushEvent', 'CreateEvent'], repoList)
    print commitDict
    print repoList
    print repoTypeList











