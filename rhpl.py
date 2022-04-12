from requests import Session;
from bs4 import BeautifulSoup as bs;
from datetime import date;

with Session() as s:
   
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36", }
    
    login_url = "https://catalog.rhpl.org/polaris/logon.aspx"
    site = s.get(login_url, headers=headers)
    login_content = bs(site.content, "html.parser")
    VIEWSTATE_token = login_content.find("input", {"name":"__VIEWSTATE"})["value"]
    VIEWSTATE_GENERATOR_token = login_content.find("input", {"name":"__VIEWSTATEGENERATOR"})["value"]
    EVENTVALIDATION_token = login_content.find("input", {"name":"__EVENTVALIDATION"})["value"]


    login_data = {
        "ctl00$BodyMainContent$textboxBarcodeUsername" : "<username>",
        "ctl00$BodyMainContent$textboxPassword" : "<password>",
        "__VIEWSTATE" : VIEWSTATE_token,
        "__VIEWSTATEGENERATOR" : VIEWSTATE_GENERATOR_token,
        "__EVENTVALIDATION":  EVENTVALIDATION_token ,
        "ctl00$BodyMainContent$buttonSubmit" : "Log In",
        "MIME Type" : "application/x-www-form-urlencoded"
    }
    
    headers["referer"] = login_url

    response = s.post(login_url, data = login_data, headers = headers)

    home_page = s.get("https://catalog.rhpl.org/polaris/patronaccount/itemsout.aspx", headers=headers)
    bs_content = bs(home_page.content, "html.parser")
    dueDates = bs_content.select("span[id=labelDueDate]")
    renewals = bs_content.select("span[id=labelRenewalsLeft]")

s.close()

with open('LibraryBooks.txt', 'w') as f:
    for i in range(len(dueDates)):
        print(dueDates[i].text, renewals[i].text)
        f.write(dueDates[i].text)
        f.write(" ")
        f.write(renewals[i].text)
        f.write("\n")

    #  if (date.today() 
f.close()

# read in dates and renewals from file
# calculate actual date
# if actual date is within 4 days of today (today - actual <= 4), generate a message