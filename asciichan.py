import webapp2
import urllib2
import logging
from xml.dom import minidom

from google.appengine.api import memcache
from google.appengine.ext import db

from common import BaseHandler

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
    #ip = "4.2.2.2"
    url = IP_URL + ip
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except URLError:
        return

    if content:
        d = minidom.parseString(content)
        coords = d.getElementsByTagName("gml:coordinates")
        if coords and coords[0].childNodes[0].nodeValue:
            lon, lat = coords[0].childNodes[0].nodeValue.split(',')
            return db.GeoPt(lat, lon)

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
def gmaps_img(points):
    return GMAPS_URL + '&'.join('markers=%s,%s' % (p.lat,p.lon) 
                                for p in points)

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    coords = db.GeoPtProperty()



def top_arts(update = False):
    key = 'top'
    arts = memcache.get(key)
    if arts is None or update:
        logging.error("DB QUERY")
        arts = db.GqlQuery("SELECT * "
                           "FROM Art "
                           "ORDER BY created DESC "
                           "LIMIT 10")

        #prevent the running of multiple queries
        arts = list(arts)
        memcache.set(key, arts)
    return arts    
    
class MainPage(BaseHandler):
    def render_front(self, title="", art="", error=""):
        arts = top_arts()

        img_url = None
        #find which arts have coords
        points = filter(None, (a.coords for a in arts))
        if points:
            img_url = gmaps_img(points)
        
        self.render("asciichan/front.html", title=title, art=art, error=error, arts=arts, img_url=img_url)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
        
            coords = get_coords(self.request.remote_addr)
            if coords:
                a.coords = coords

            a.put()
            #rerun the query and update the cache
            top_arts(True)

            self.redirect('/asciichan')
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title, art, error)

app = webapp2.WSGIApplication([('/asciichan', MainPage)], debug = True)
