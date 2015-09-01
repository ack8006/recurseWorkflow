import requests
from contextlib import closing


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
        data = data + page.json()
        if len(data)%30 != 0:
            return data
        else:
            pageNum += 1
            return self.requestData(data, pageNum)

class ParseGitData():
    def __init__(self, data):
        self.data = data

    def parseForPushEvents(self):
        pushEvents = [event for event in self.data if event['type']=='PushEvent']
        print pushEvents
        print len(pushEvents)


if __name__ == "__main__":
    #gus = getGitHubData("aaylward")
    gus = getGitHubData("ack8006")
    data = gus.getRecentEvents()

    pgd = ParseGitData(data)
    pgd.parseForPushEvents()












