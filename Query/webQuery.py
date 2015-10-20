import webbrowser
import urllib
import urllib2




id = 0
pageURL = 'http://www.monosaccharidedb.org/display_monosaccharide.action?id=' + str(id)


response = urllib2.urlopen(pageURL)
html = response.read()
print(html)

