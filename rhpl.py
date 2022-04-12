from requests import Session;
from bs4 import BeautifulSoup as bs;
from datetime import datetime, timedelta;
import re

#TODO split submitpostrequest function into post and get
#TODO set up better handling of erroneous input in makeConfig/validation
#TODO validate successful page load, else throw error
#TODO double check null handling
#TODO test null exception for filenotfound and bad fileinput (config file)
#TODO set up static typing
#TODO check datetime and re package version
#TODO set up email notification


class RHPL(object): 
    def __init__(self, userInfo):
        self.userInfo = userInfo
        self.bookList = []
        self.dueSoon = []

    def main():
        # upon successful load, populate the class
        user = RHPL(RHPL.loadConfig())

        # call post request function
        RHPL.submitPostRequest(user)

        # date calculation
        for i in user.bookList:

            dueDate = datetime.strptime(i[0], "%m/%d/%Y") + timedelta(weeks=int(i[1]))
            if (dueDate - datetime.today()).days < 7:
                user.dueSoon.append((dueDate, i[2]))
        
        # generate the message notification
        if len(user.dueSoon) > 0:
            # sort the entries by soonest due
            user.dueSoon.sort()
            print("The following books are due soon: \n")
            for i in user.dueSoon:
                print(datetime.strftime(i[0], "%A, %d %B %Y"), i[1])

    @staticmethod
    def loadConfig():
        try:
            f = open(".userconfig", 'r')
            userInfo = {
            "username" : str.strip(f.readline()),
            "password" : str.strip(f.readline()),
            "phone" : str.strip(f.readline()),
            "email" : str.strip(f.readline()) 
            }
            f.close()
            RHPL.validConfig(userInfo)
        except AssertionError as e: 
            print(e.args[0])
            print("Configuration not defined or invalid. Re-enter information: ")
            userInfo = RHPL.makeConfig()
        except OSError:
            print("Configuration file could not be loaded. Please enter information: ")
            userInfo = RHPL.makeConfig()
        return userInfo

    @staticmethod
    def validConfig(userInfo):

        try:
            if (userInfo["username"] is None) or not userInfo["username"] or " " in userInfo["username"]:
                raise AssertionError("No username / invalid username defined")

            if (userInfo["password"] is None) or not userInfo["password"] or " " in userInfo["password"]:
                raise AssertionError("No password / invalid password defined")
            
            if (userInfo["phone"] is None) or not userInfo["phone"] or not str.isnumeric(userInfo["phone"]) or \
            len(userInfo["phone"]) != 10:
                raise AssertionError("No phone number / invalid phone number defined")
        
            if (userInfo["email"] is None) or not userInfo["phone"] or " " in userInfo["email"]:
                raise AssertionError("No email / invalid email defined")

            email_split = userInfo["email"].rsplit("@",1)
            address = email_split[0]
            domain = email_split[1].split(".",1)

            if not ("@" in userInfo["email"]) or not ("." in userInfo["email"]) or len(address) <= 0 or \
            len(domain[0]) <= 0 or len(domain[1]) <= 0:
                raise AssertionError("Invalid email address")
        except AssertionError:
            raise
            

    @staticmethod
    def makeConfig():
        username = input("Enter RHPL username: ")
        password = input("Enter RHPL password: ")
        phone = input("Enter phone number you would like notifications to go to: ")
        phone = "".join(re.findall("\d+", phone))

        email = input("Enter email you would like notifications to go to: ")
        with open(".userconfig", 'w') as f:
            for a in (username, password, phone, email):
                f.write(str.strip(a))
                f.write("\n")
        f.close()
        return RHPL.loadConfig()

    def submitPostRequest(self):
        with Session() as s:            
            login_url = "https://catalog.rhpl.org/polaris/logon.aspx"
            site = s.get(login_url)
            login_content = bs(site.content, "html.parser")
            VIEWSTATE_token = login_content.find("input", {"name":"__VIEWSTATE"})["value"]
            VIEWSTATE_GENERATOR_token = login_content.find("input", {"name":"__VIEWSTATEGENERATOR"})["value"]
            EVENTVALIDATION_token = login_content.find("input", {"name":"__EVENTVALIDATION"})["value"]

            login_data = {
                "ctl00$BodyMainContent$textboxBarcodeUsername" : self.userInfo["username"],
                "ctl00$BodyMainContent$textboxPassword" : self.userInfo["password"],
                "__VIEWSTATE" : VIEWSTATE_token,
                "__VIEWSTATEGENERATOR" : VIEWSTATE_GENERATOR_token,
                "__EVENTVALIDATION":  EVENTVALIDATION_token ,
                "ctl00$BodyMainContent$buttonSubmit" : "Log In",
                "MIME Type" : "application/x-www-form-urlencoded"
            }
            
            response = s.post(login_url, data = login_data)

            home_page = s.get("https://catalog.rhpl.org/polaris/patronaccount/itemsout.aspx")
            bs_content = bs(home_page.content, "html.parser")
            dueDates = bs_content.select("span[id=labelDueDate]")
            renewals = bs_content.select("span[id=labelRenewalsLeft]")
            titles = bs_content.select("span[id=labelTitle]")
        s.close()

        for i in range(len(dueDates)):
            self.bookList.append((dueDates[i].text, renewals[i].text, titles[i].text))
        return self

if __name__ == "__main__":
    RHPL.main()

