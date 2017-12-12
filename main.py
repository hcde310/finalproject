import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib.urlopen(url)
    except urllib2.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib2.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None

WOW_KEY = 'qstcsteq6f8e7rhp9b5duh6cusyzsxg4'

def wowREST(method='pet', params={}):
    baseurl = 'https://us.api.battle.net/wow/'
    params['locale'] = 'en_US'
    params['apikey'] = WOW_KEY

    url = baseurl + method + '/?' + urllib.urlencode(params)
    return safeGet(url)

def petdict(url):
    jsondict = json.load(url)
    return jsondict

def collectInfo(dict):
    pets = {}
    for pet in dict['pets']:
        pname=pet['name']
        if len(pname.split()) > 1:
            list = pname.split()
            pname = list[0]
        pets[pname]={}
        pets[pname]['name'] = pname
        pets[pname]['family']= pet['family']
        pets[pname]['icon'] = pet['icon']
        pets[pname]['StrongAgainst'] = pet['strongAgainst'][0]
        pets[pname]['WeakAgainst'] = pet['weakAgainst'][0]
    return pets

def getPetInfo(petname, dict):
    petinfo = {}
    if petname in dict.keys():
        petinfo = dict[petname]
    return petinfo

class Pet():
    def __init__(self, pet):
        self.name = pet['name']
        self.family = pet['family']
        self.icon = pet['icon']
        self.StrongAgainst = pet['StrongAgainst']
        self.WeakAgainst = pet['WeakAgainst']
        self.thumbnailURL = 'https://wow.zamimg.com/images/wow/icons/large/%s.jpg' %(self.icon)

    def __str__(self):
        return '%s\nFamily: %s\nStrong Against: %s\nWeak Against: %s' %(self.name, self.family, self.StrongAgainst, self.WeakAgainst)
    def _repr_(self):
        return self.__str__()

def usePetObject(petname, dict):
    pn = getPetInfo(petname, dict)
    petobject = Pet(pn)
    return petobject

def getTargetedPetInfo(pet, petlist):
    for p in petlist:
        if p.name == pet:
            return p
        else:
            return 'We cannot find the pet you are looking for.'

if __name__ == '__main__':
    print('testing class')
    wowurl = wowREST()
    wowdict = petdict(wowurl)
    pd = collectInfo(wowdict)
    petlist = [usePetObject(p, pd) for p in pd]
    #getTargetedPetInfo("Ash'ana", petlist)

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")

        template_values={}
        template_values['page_title']="World of Warcraft Pet Search"
        template = JINJA_ENVIRONMENT.get_template('greetform.html')
        self.response.write(template.render(template_values))

class GreetResponseHandlr(webapp2.RequestHandler):
    def post(self):
        vals={}
        pet = self.request.get('pet')
        vals['page_title']="World of Warcraft Pet Search: " + pet
        #vals['pet'] = petlist


        if pet:
            pet = self.request.get('pet')
            wowurl = wowREST()
            wowdict = petdict(wowurl)
            pd = collectInfo(wowdict)
            #petlist = [usePetObject(p, collectInfo(wowdict)) for p in collectInfo(wowdict)]
            pn = usePetObject(pet, pd)
            #, 'name': p.name, 'family': p.family, 'weakAgainst': p.WeakAgainst, 'strongAgainst': p.StrongAgainst}
            vals['pet'] = pn

            template = JINJA_ENVIRONMENT.get_template('greetresponse.html')
            self.response.write(template.render(vals))
        else:
            template = JINJA_ENVIRONMENT.get_template('greetform.html')
            self.response.write(template.render(vals))

application = webapp2.WSGIApplication([ \
                                      ('/gresponse', GreetResponseHandlr),
                                      ('/.*', MainHandler)
                                      ],
                                      debug=True)