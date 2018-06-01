import discord
import asyncio
import json
import requests
import re

client = discord.Client()

def lookupDragon(dragonid):
    baseurl = "http://flightrising.com"
    #dragonid = "29939190"

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
    #(json.dumps(ddata,indent=4))
    return ddata

def getDragonImage(dragonid):
    id = int(dragonid)
    link = "http://flightrising.com/rendern/{2}/{0}/{1}_{2}.png".format(int((id/100)+1),id,350)
    return link

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("."):
        client.send_typing(message.channel)
        command = message.content[1:].split(" ")
        if command[0] == "hi" or command[0] == "hello":
            await client.send_message(message.channel, 'hello!')
        elif command[0] == "lookup":
            dragonid = command[1]
            print("Parsing dragon id #{}".format(dragonid))
            ddata = lookupDragon(dragonid)
            print("Getting dragon iamge")
            image = getDragonImage(dragonid)

            print("Creating embed")
            embed = discord.Embed(title="**Dragon Profile:** #{}".format(dragonid),colour=discord.Colour(0xFFFFFF))
            
            embed.set_image(url=image)
            
            na = "Not Available"

            embed.add_field(name="**Name**",value=ddata["data"]["name"],inline=True)
            embed.add_field(name="**Owner**",value=na,inline=True)
            embed.add_field(name="**Breed**",value=ddata["data"]["breed"],inline=True)
            embed.add_field(name="**Sex**",value=ddata["data"]["sex"],inline=True)

            embed.add_field(name="**Flight**",value=na,inline=True)
            embed.add_field(name="**Hatchday**",value=ddata["data"]["hatchday"],inline=True)
            embed.add_field(name="**Links**",value=na,inline=True)

            embed.add_field(name="**Colors and Genes**",value="""
**Primary:** {0[data][gene_primary]:20}
**Secondary:** {0[data][gene_secondary]:20}
**Tertiary:** {0[data][gene_tertiary]:20}""".format(ddata),inline=False)

            embed.add_field(name="Lineage",value="{0}\n{0}\n{0}".format(na))
            
            embed.add_field(name="Stats",value=" ".join(["**{0:left 3}**: {1:right 4} {2}".format(i,ddata["stats"][i]["base"],ddata["stats"][i]["mod"]) for i in ddata["stats"].keys()]),inline=False)

            embed.add_field(name="Length",value=ddata["data"]["length"])
            embed.add_field(name="Wingspan",value=ddata["data"]["wingspan"],inline=True)
            embed.add_field(name="Weight",value=ddata["data"]["weight"],inline=True)
            await client.send_message(message.channel, None, embed=embed)
            
creds = json.load(open("creds.json","r"))

client.run(creds["token"])
