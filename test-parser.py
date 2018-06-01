import re
import requests
import json

baseurl = "http://flightrising.com"
dragonid = "29939190"

stats = {"str" : "",
         "int" : "",
         "agi" : "",
         "vit" : "",
         "def" : "",
         "mnd" : "",
         "qck" : ""}
for i in stats.keys():
    r = requests.get("{}/includes/ol/dstats.php?d={}&s={}".format(baseurl,dragonid,i))
    matches = re.match(re.compile("^.*?left[^>]*>(?P<name>\w+).*?right[^>]*>(?P<base>\d+)[^>]*>(?P<mod>[^<]*).*?color[^>]*>(?P<battle>[^<]*).*?color[^>]*>(?P<dom>[^<]*).*$",re.DOTALL),r.text)
    stats[i] = matches.groupdict()

r = requests.get("{}/main.php?dragon={}".format(baseurl,dragonid))
data = re.search(re.compile("\
font-size.22px.*?text-align.left.*?731d08[^>]*>\s*(?P<name>\w*).*?<br>[^>]*>\s*\#(?P<id>[0-9]*)\
.*?\
Info\
.*?bold;\">Level\ (?P<level>[^\s<]*)</div>\
.*?margin-left:20px;\">(?P<breed>[\w ]*?) (?P<sex>[^\s<]+)</div>\
.*?bold;\">Hatchday</div>[^>]*>(?P<hatchday>[^<]*)\
.*?\
Growth\
.*?Length</div>\s*(?P<length>[^\t]*)\
.*?Wingspan</div>\s*(?P<wingspan>[^\t]*)\
.*?Weight</div>\s*(?P<weight>[^\t]*)\
.*?\
Genes\
.*?Primary</span>(?P<gene_primary>[^<]*)\
.*?Secondary</span>(?P<gene_secondary>[^<]*)\
.*?Tertiary</span>(?P<gene_tertiary>[^<]*)\
",re.VERBOSE | re.DOTALL),r.text)

ddata = {"data" : data.groupdict(),
         "stats" : stats}

print(json.dumps(ddata,indent=4))
