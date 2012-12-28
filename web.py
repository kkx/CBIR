from twisted.web import server, resource
from twisted.internet import reactor
import time
import cgi
import operator
import query

class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return """<html><body>A web demo which shows how does the CBIR system work <form action="" method="post" enctype="multipart/form-data"><input type="file" name="myfile" /> <input type="submit" /></form></body></html>""" 
    def render_POST(self, request):
        self.headers = request.getAllHeaders()
        # For the parsing part look at [PyMOTW by Doug Hellmann][1]
        img = cgi.FieldStorage(
            fp = request.content,
            headers = self.headers,
            environ = {'REQUEST_METHOD':'POST',
                'CONTENT_TYPE': self.headers['content-type'],
            }
        )

        print img["myfile"].name, img["myfile"].filename,
        print img["myfile"].type, img["myfile"].type
        if str(img["myfile"].type).startswith("image"):
            out = open("test/"+img["myfile"].filename, 'wb')
            out.write(img["myfile"].value)
            out.close()
            image_scores = query.query("test/"+img["myfile"].filename)
            sorted_image_scores = sorted(image_scores.iteritems(), key=operator.itemgetter(1))[-90:]
            count = 0
            for i in sorted_image_scores:
                if i[1]>=1:
                    break
                count+=1
            print 90-count

            st = "<ul>"
            count = 0
            for s in sorted_image_scores[::-1]:
                url = "http://img3.douban.com/lpic/s%d.jpg"%(int(s[0]))
                st += "<li>%d "%(count)+str(s)+"""<img src="%s" alt="1" height="300" width="300">"""%(url)+"</li>"
                count += 1

            return "results"+ "\n"+st+"</ul>"+"\n"
           
            return "Posted"
        else:
            return "Shit happens, some error occurred"


site = server.Site(Simple())
reactor.listenTCP(8080, site)
reactor.run()
