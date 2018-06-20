import discord
import asyncio
import json
import requests
import re
import os
import time
import random
import csv

client = discord.Client()

baseurl = "http://flightrising.com"
commandChar = "!"

commands={}

responses={}

with open("bossdad-responses.csv","r",newline='') as f:
    reader = csv.reader(f,delimiter=",",quotechar='"')
    for i in reader:
        for j in i[0].split(","):
            if j.startswith(commandChar):
                key = j[1:].lower()
                if not key in commands:
                    commands[key] = []
                commands[key].append((i[1].split(","),i[2]))
            else:
                key = j.lower()
                if not key in responses:
                    responses[key] = []
                responses[key].append((i[1].split(","),i[2]))

def getDragonImageURL(dragonid):
    id = int(dragonid)
    link = "http://flightrising.com/rendern/{2}/{0}/{1}_{2}.png".format(int((id/100)+1),id,350)
    return link

def getDragonURL(dragonid):
    global baseurl
    return "{}/main.php?dragon={}".format(baseurl,dragonid)

def lookupDragon(dragonid):
    global baseurl
    
    # stats = {"str" : "",
    #          "int" : "",
    #          "agi" : "",
    #          "vit" : "",
    #          "def" : "",
    #          "mnd" : "",
    #          "qck" : ""}
    # for i in stats.keys():
    #     r = requests.get("{}/includes/ol/dstats.php?d={}&s={}".format(baseurl,dragonid,i))
    #     matches = re.match(re.compile("^.*?left[^>]*>(?P<name>\w+).*?right[^>]*>(?P<base>\d+)[^>]*>(?P<mod>[^<]*).*?color[^>]*>(?P<battle>[^<]*).*?color[^>]*>(?P<dom>[^<]*).*$",re.DOTALL),r.text)
    #     stats[i] = matches.groupdict()
        
    r = requests.get(getDragonURL(dragonid))
    data = re.search(re.compile("\
>\s*(?P<owner>[^:]*):\ <a\ href=\"main.php\?p=lair&id=(?P<lair>\d*)\
.*?font-size.22px..text-align.left..color..?731d08[^>]*>\s*(?P<name>\w*).*?<br>[^>]*>\s*\#(?P<id>[0-9]*)\
.*?a\ class=\"elemclue\"\ TITLE.\"(?P<flight>\w*)\
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
.*?Eye\ Type</span>(?P<eye_type>[^<]*)\
.*?\
Parents\
.*?margin-left.*?(<em>(?P<parents>none)</em>|\
(a\ href=main.php\?p=view&id=\d*&tab=dragon&did=(?P<father_id>\d*)[^>]*>(?P<father_name>\w*))\
.*?\
(a\ href=main.php\?p=view&id=\d*&tab=dragon&did=(?P<mother_id>\d*)[^>]*>(?P<mother_name>\w*))\
)\
",re.VERBOSE | re.DOTALL),r.text)
        
    # ddata = {"data" : data.groupdict(),
    #              "stats" : stats}
    
    ddata = {"data" : data.groupdict()}

    offspring = re.search(re.compile("Offspring.*?margin-left[^>]*>(.*?)</div>",re.DOTALL),r.text)
    
    ddata["data"]["offspring"] = len(re.findall(re.compile("<br />",re.DOTALL),offspring.group(1)))

    
    #(json.dumps(ddata,indent=4))
    return ddata

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

@client.event
async def on_message(message):
    #lets not bother with responding to other bots
    if message.author.bot:
        return

    global responses
    global commands
    #this is somewhat of a mess, I'm sorry
    triggeredResponses = [i for i in responses.keys() if i in message.content]
    if triggeredResponses and random.randint(0,2) <= 1:
        await client.send_typing(message.channel)

        trig = random.choice(triggeredResponses)
        a = responses[trig]
        possible = [i for i in a if ((i[0][0] == "any") or (set(message.author.roles) & set(i[0])))]
        if not possible:
            return
        await client.send_message(message.channel, random.choice(possible)[1])
        return
    elif message.content.startswith(commandChar):
        await client.send_typing(message.channel)

        content = message.content[1:]
        command = message.content[1:].split(" ")
        if content.lower() in commands:
            content = content.lower()
            possible = [i for i in commands[content] if ((i[0][0] == "any") or (set(message.author.roles) & set(i[0])))]
            await client.send_message(message.channel, random.choice(possible)[1])
            return
        #        elif command[0] == "brew":
#            await client.send_message(message.channel, 'Got it, setting reminder for {} in 30 minutes'.format(message.author.mention()))
#        elif command[0] == "scry":
            #http://flightrising.com/includes/ol/scryer_bloodlines.php
            #post feilds
            #id1	29939190+
            #id2	29994524+
#            print("Checking bloodlines")
        # elif command[0] == "work" or command[0] == "shout":
        #     if len(message.mentions) > 0:
        #         #I'm lazy so I'm just responding with whatever the first mention is in the list
        #         await client.send_message(message.channel, "{} GET BACK TO WORK".format(message.mentions[0].mention))
        #     else:
        #         await client.send_message(message.channel, "GET BACK TO WORK")
        elif command[0] == "exalt":
            if len(message.mentions) > 0:
                if message.mentions[0].id == client.user.id:
                    await client.send_message(message.channel, random.choice(["No","YOU'RE FIRED"]))
                else:
                    await client.send_message(message.channel, "{0} HAS BEEN EXALTED FOR {1} TREASURE.".format(message.mentions[0].mention,random.randint(2494,38161)))
        elif command[0] == "lookup":
            global baseurl
            dragonid = command[1]

            print("Parsing dragon id #{}".format(dragonid))
            ddata = lookupDragon(dragonid)
            
            print("Getting dragon image")
            imagesDir = "dergs"
            tempFile = "/".join([imagesDir,"{0}-{1}-{2}.png".format(dragonid,ddata["data"]["name"],int(time.time()/60))])
            if not os.path.isdir(imagesDir):
                os.makedirs(imagesDir)

            imageURL = getDragonImageURL(dragonid)
            if not os.path.isfile(tempFile):
                with open(tempFile, 'wb') as f:
                    r = requests.get(imageURL, stream=True)
                    for chunk in r.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)
                            
            with open(tempFile,"rb") as f:
                await client.send_file(message.channel,f)
                
            
            print("Creating embed")
            flightmap = {"arcane" : 0xee14dc,
                         "earth" : 0x6b3918,
                         "fire" : 0xff8c0f,
                         "ice" : 0xd3e2ff,
                         "light" : 0xf3e336,
                         "lightning" : 0x33f2ed,
                         "nature" : 0x288d13,
                         "plague" : 0xfe0000,
                         "shadow" : 0x560081,
                         "water" : 0x2f45f3,
                         "wind" : 0xc3f874}

            embed = discord.Embed(title="**Dragon Profile**",description="[#{0}]({1})".format(dragonid,getDragonURL(dragonid)),colour=discord.Colour(flightmap[ddata["data"]["flight"].lower()]))
            
            na = "Not Available"
            
            embed.add_field(name="Name",value=ddata["data"]["name"],inline=True)
            embed.add_field(name="Owner",value=ddata["data"]["owner"],inline=True)
            embed.add_field(name="Flight",value=ddata["data"]["flight"],inline=True)
            embed.add_field(name="Breed",value=ddata["data"]["breed"],inline=True)
            embed.add_field(name="Sex",value=ddata["data"]["sex"],inline=True)
            embed.add_field(name="Level",value=ddata["data"]["level"],inline=True)
            embed.add_field(name="Hatchday",value=ddata["data"]["hatchday"],inline=True)
            
            embed.add_field(name="Colors and Genes",value="""\
**Primary:** {0[data][gene_primary]:20}
**Secondary:** {0[data][gene_secondary]:20}
**Tertiary:** {0[data][gene_tertiary]:20}
**Eye Type:** {0[data][eye_type]:20}""".format(ddata),inline=True)

#            stats = "{0[0]}\t{0[1]}\n{0[2]}\t{0[3]}\n{0[4]}\t{0[5]}\n{0[6]}".format(["**{0:4}**: {1:4} {2}".format(i.upper(),ddata["stats"][i]["base"],ddata["stats"][i]["mod"],align="right") for i in ddata["stats"].keys()])
#            embed.add_field(name="Stats",value=stats,inline=False)

            if ddata["data"]["parents"]:
                embed.add_field(name="Lineage",value="No Parents\nOffspring: {0}".format(ddata["data"]["offspring"]),inline=True)
            else:
                embed.add_field(name="Lineage",value="Father: {0}\nMother: {1}\nOffspring: {2}".format(
                    "[{0}]({1})".format(ddata["data"]["father_name"],getDragonURL(ddata["data"]["father_id"])),
                    "[{0}]({1})".format(ddata["data"]["mother_name"],getDragonURL(ddata["data"]["mother_id"])),
                    ddata["data"]["offspring"]),inline=True)

#            embed.add_field(name="Length",value=ddata["data"]["length"])
#            embed.add_field(name="Wingspan",value=ddata["data"]["wingspan"],inline=True)
#            embed.add_field(name="Weight",value=ddata["data"]["weight"],inline=True)

            embed.add_field(name="Links",value="""\
[Dressing room](http://www1.flightrising.com/dressing/outfit)
[Bloodline](http://flightrising.com/main.php?p=scrying&view=bloodlines)
[Morphology](http://flightrising.com/main.php?p=scrying&view=morphintime)""",inline=False)
            

            await client.send_message(message.channel, None, embed=embed)
            
creds = json.load(open("creds.json","r"))

client.run(creds["token"])
