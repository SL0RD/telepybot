from mcstatus import MinecraftServer

server = MinecraftServer.lookup("198.50.193.198")

print "this is a test"


#def get_players():
#    logging.info("Checking MC server for connected players")
#    players = ", ".join(server.query(retries=5).players.names)
#    if len(players) > 1:
#        return players
#    else:
#        return None
                    

def command_minecraft(bot, update):
    print "testing 12"
    message = update.message.text
    print message
    if len(message.split()) > 1:
        o = message.split()[1]
        if o == "players":
            players = get_players()
            t = None
            if players:
                if len(players.split()) > 1:
                    t = "The following players are online: {0}".format(players)
                else:
                    t = "{0} is the only one online. Why not join them?".format(players)
            else:
                t = "There is no one connected to the server."
        if o == "oregen":
            t = "A graph of the ore spawn levels can be found here: http://bit.ly/1m3vbdc"
        if t:
            bot.sendMessage(update.message.chat_id, text=t)
    else:
        bot.sendMessage(update.message.chat_id, text="The server ip for Memecraft is 198.50.193.198\n"
                            "There are currently {0} players online.\n"
                            "Server Ping: {1}\n"
                            "The server is running a modified version of the DireWolf20 FTB modpack (Modpack Version 1.8.0). \n"
                            "For more info regarding setup use the \"/memecraft mods\" command.".format(server.status().players.online, server.status().latency))

