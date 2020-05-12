#!/usr/bin/python3.1

import socket
import threading
from struct import *


class Player(object):
    def __init__(self, sock, name, attack, defense, regen, description):
       self.sock = sock
       self.name = name
       self.flags = 200 #Dont know if I can just set this automaticly 11001000 Alive, Join, Ready
       self.attack = attack
       self.defense = defense
       self.regen = regen
       self.health = 300
       self.gold = 35
       self.description = description
       self.alive = True
       self.room = 0
       self.playing = False

    def getName(self):
        return self.name
     
    def getFlags(self):
        return self.flags
    
    def getAttack(self):
        return self.attack

    def getDefense(self):
        return self.defense
    
    def getRegen(self):
        return self.regen
    
    def getHealth(self):
        return self.health
    
    def getGold(self):
        return self.gold
    
    def getDescription(self):
        return self.description

    def getRoom(self):
        return self.room
    
    def changeRoom(self, newRoom):
        self.room = newRoom
    
    def setRoom(self, r):
        roomNum = r
        self.room = roomNum.getRoomNum()
    
    def sendMessage(self, msg):
        self.sock.send(msg)
        return
    
    def recieveMessage(self, size):
        # print("Inside recieve msg") 
        data = self.sock.recv(size)
        # print("data recieved")
        return data

    def damageCal(self, defense, attack):
        damage = 0
        if attack == 0:
            return 0
        else:
            damage = attack * (100 / (100 + defense))
        return damage
    
    
    def setPlaying(self, stat):
        self.playing = stat
        self.flags = 216
    
    
    def updateHealth(self, dmg):
        if self.health - dmg < 0:
            self.health = 0
            self.alive = False
            self.flags = 0
        
        elif self.health - dmg == self.health:
            self.health = self.health
        
        else:
            self.health = self.health - dmg

    def fight(self, other):
        damage = self.damageCal(self.defense, other.attack)
        self.updateHealth(damage)
    
    def start(self, skt):
        self.sock = skt
        self.playing = True
    
    def characterType(self):
        Type = (10).to_bytes(1, 'little')
        charName = self.name.ljust(32, '\00')
        name = charName.encode('utf-8')
        flags = self.flags.to_bytes(1, 'little')
        attack = self.attack.to_bytes(2, 'little')
        defense = self.defense.to_bytes(2, 'little')
        regen = self.regen.to_bytes(2, 'little')
        health = self.health.to_bytes(2, 'little')
        gold = self.gold.to_bytes(2, 'little')
        room = self.room.to_bytes(2, 'little')
        descLen = (len(self.description)).to_bytes(2, 'little')
        description = self.description.encode('utf-8')

        pkt = bytearray()

        lurkChar = [Type, name, flags, attack, defense, regen, health, gold, room, descLen, description]

        for i in lurkChar:
            pkt += i

        return pkt



class Monster(object):
    def __init__(self, room, name, attack, defense, regen, description):
       self.room = room
       self.name = name
       self.flags = 186 #Dont know if I can just set this automaticly 
       self.attack = attack
       self.defense = defense
       self.regen = regen
       self.health = 300
       self.gold = 0
       self.description = description
       self.alive = True

    def getName(self):
        return self.name
    
    def getFlags(self):
        return self.flags
    
    def getAttack(self):
        return self.attack

    def getDefense(self):
        return self.defense
    
    def getRegen(self):
        return self.regen
    
    def getHealth(self):
        return self.health
    
    def getGold(self):
        return self.gold
    
    def getDescription(self):
        return self.description

    def getRoom(self):
        return self.room

    def damageCal(self, defense, attack):
        damage = 0
        if attack == 0:
            return 0
        else:
            damage = attack * (100 / (100 + defense))
        return damage

    def updateHealth(self, dmg):
        if self.health - dmg < 0:
            self.health = 0
            self.alive = False
            self.flags = 32
        
        elif self.health - dmg == self.health:
            self.health = self.health
        
        else:
            self.health = self.health - dmg

    def monsterType(self):
        Type = (10).to_bytes(1, 'little')
        monName = self.name.ljust(32, '\00')
        name = monName.encode('utf-8')
        flags = self.flags.to_bytes(1, 'little')
        attack = self.attack.to_bytes(2, 'little')
        defense = self.defense.to_bytes(2, 'little')
        regen = self.regen.to_bytes(2, 'little')
        health = self.health.to_bytes(2, 'little')
        gold = self.gold.to_bytes(2, 'little')
        room = self.room.to_bytes(2, 'little')
        descLen = (len(self.description)).to_bytes(2, 'little')
        description = self.description.encode('utf-8')

        pkt = bytearray()

        lurkMonster = [Type, name, flags, attack, defense, regen, health, gold, room, descLen, description]

        for i in lurkMonster:
            pkt += i

        return pkt

class Room:
    def __init__(self, roomNum, name, description):
        self.roomNum = roomNum
        self.name = name
        self.description = description
        self.players = {}
        self.monsters = []
        self.conncections = {}
    
    def getRoomNum(self):
        return self.roomNum

    def getName(self):
        return self.name
    
    def getDescription(self):
        return self.description
    
    def msgPlayers(self, msg):
        for name in self.players:
            player = self.players[name]
            player.sendMessage(msg)
    
    def addPlayer(self, player):
        if player.getName() not in self.players:
            newPlayer = player.characterType()
            self.msgPlayers(newPlayer)
            self.players[player.getName()] = player

    def removePlayer(self, player):
        self.players.pop(player.getName(), None)
    
    def addMonster(self, monster):
        self.monsters.append(monster)
    
    def addConnection(self, room):
        self.conncections[room.getRoomNum()] = room
    
    def romoveConnection(self, room):
        del self.conncections[room.getRoomNum()]

    def checkConnection(self, room):
        if room.getRoomNum() in self.conncections:
            return True
        else:
            return False
    
    def fightMonster(self, player):
        if player.getName() not in self.players:
            return False
        
        for i in self.monsters:
            if i.alive:
                player.fight(i)
            else:
                return False
        
        update = self.roomDescription()

        for i in update:
            player.sendMessage(i)
        
        return True

    def getPlayerStats(self):
        pkt = bytearray()
        playerStat = []

        for i in self.players:
            player = self.players[i]
            stats = player.characterType()
            playerStat.append(stats)
        
        for i in playerStat:
            pkt += i
        
        return playerStat

    def getMonsterStats(self):
        pkt = bytearray()
        monsterStat = []

        for i in self.monsters:
            stats = i.monsterType()
            monsterStat.append(stats)
        
        for i in monsterStat:
            pkt += i
        return monsterStat

    def getConnections(self):
        roomConnections = []
        # pkt = bytearray()
        for i in self.conncections.values():
            Type = (13).to_bytes(1, 'little')
            rNumber = i.getRoomNum()
            rNumber = rNumber.to_bytes(2, 'little')
            rName = i.getName().ljust(32, '\00')
            rName = rName.encode('utf-8')
            rDesc = i.getDescription()
            rDescLen = len(rDesc)
            rDescLen = rDescLen.to_bytes(2, 'little')
            rDesc = rDesc.encode('utf-8')
            roomConnections.append(Type)
            roomConnections.append(rNumber)
            roomConnections.append(rName)
            roomConnections.append(rDescLen)
            roomConnections.append(rDesc)
        
        # for i in roomConnections:
        #     pkt += i

        return roomConnections

    def roomType(self):
        pkt = bytearray()

        Type = (9).to_bytes(1, 'little')
        number = self.roomNum.to_bytes(2, 'little')
        roomName = self.name.ljust(32, '\00')
        name = roomName.encode('utf-8')
        descriptionLen = len(self.description).to_bytes(2, 'little')
        description = self.description.encode('utf-8')

        lurkRoom = [Type, number, name, descriptionLen, description]

        for i in lurkRoom:
            pkt += i
        
        return pkt
    
    def roomDescription(self):
        pkt = []

        players = self.getPlayerStats()
        monsters = self.getMonsterStats()
        room = self.roomType()
        connections = self.getConnections()

        pkt.append(room)

        for i in players:
            pkt.append(i)
        
        for i in monsters:
            pkt.append(i)
        
        
        
        for i in connections:
            pkt.append(i)

        return pkt
    
    def roomDescription2(self):
        roomDes = []
        pkt = bytearray()

        players = self.getPlayerStats()
        monsters = self.getMonsterStats()
        room = self.roomType()
        connections = self.getConnections()

        roomDes.append(room)

        for i in players:
            roomDes.append(i)
        
        for i in monsters:
            roomDes.append(i)
        
        for i in connections:
            roomDes.append(i)
        
        for i in roomDes:
            pkt += i

        return pkt

class Game:
    def __init__(self):
        self.rooms = {}
        self.players = {}
        self.errors = {}
        self.description = "You have entered Hogwarts. The Basilisk is trying to kill all of the muggle-borns. The fate of Hogwarts is in your hands. Make your way to the Chamber of Secrets and kill the Basalisk"
        self.initialRoom = None
        self.initialPoints = 150
        self.statLimit = 65535
        self.majorVersion = 2
        self.minorVersion = 2
        self.playing = False
        self.lock = threading.RLock()
        self.gameInfo()

    def sendGameDescription(self):
        pkt = bytearray()
        Type = 11
        Type = Type.to_bytes(1, 'little')
        initialPoints = self.initialPoints.to_bytes(2, 'little')
        statLimit = self.statLimit.to_bytes(2, 'little')
        descriptionLen = len(self.description).to_bytes(2, 'little')
        description = self.description.encode('utf-8')

        gameDes = [Type, initialPoints, statLimit, descriptionLen, description]

        for i in gameDes:
            pkt += i
    
        return pkt
    
    def sendVersion(self):
        pkt = bytearray()
        Type = 14
        Type = Type.to_bytes(1, 'little')
        major = self.majorVersion.to_bytes(1, 'little')
        minor = self.minorVersion.to_bytes(1, 'little')
        size = 0
        size = size.to_bytes(2, 'little')

        version = [Type, major, minor, size]

        for i in version:
            pkt += i

        return pkt

    def sendError(self, error):
        pkt = bytearray()

        Type = (7).to_bytes(1, 'little')
        errorCode = error.to_bytes(1, 'little')
        desLen = len(self.errors[error]).to_bytes(2, 'little')
        desc = self.errors[error].encode('utf-8')

        errorMsg = [Type, errorCode, desLen, desc]

        for i in errorMsg:
            pkt += i

        return pkt

    def startPlayer(self, skt):
        print("top of start player")
        name = ""
        playerReady = False
        versionMsg = self.sendVersion()
        skt.send(versionMsg)
        gameMsg = self.sendGameDescription()
        skt.send(gameMsg)
        while not playerReady:
            print("Inside player ready while loop")
            Type = skt.recv(1)

            if Type[0] != 10:
                error = self.sendError(5)
                skt.send(error)
        
            nameBuff = skt.recv(32)
            name = nameBuff.decode('utf')

            flag = skt.recv(1)
            flag = int.from_bytes(flag, 'little')

            attack = skt.recv(2)
            attack = int.from_bytes(attack, 'little')

            defense = skt.recv(2)
            defense = int.from_bytes(defense, 'little')

            regen = skt.recv(2)
            regen = int.from_bytes(regen, 'little')

            health = skt.recv(2)
            gold = skt.recv(2)
            room = skt.recv(2)

            descLen = skt.recv(2)
            descLen = int.from_bytes(descLen, 'little')

            description = skt.recv(descLen)
            description = description.decode('utf-8')

            if name in self.players:
                error = self.sendError(2)
                skt.send(error)
                skt.close()

            if attack + defense + regen > self.initialPoints:
                print("hello")
                error = self.sendError(4)
                skt.send(error)
                # skt.close()

            else:
                with self.lock:
                    print("Inside player def")
                    roomN = self.initialRoom
                    player = Player(skt, name, attack, defense, regen, description)
                    print(player.name)
                    print(player.attack)
                    print(player.defense)
                    print(player.regen)
                    print(player.health)
                    print(player.description)
                    player.setRoom(roomN)
                    self.players[name] = player
                    playerReady = True

                    print("hi")

                    skt.send(self.acceptType(10))
                self.playGame(player)

    def acceptType(self, typeA):
        pkt = bytearray()
        Type = (8).to_bytes(1, 'little')
        typeAccepted = typeA.to_bytes(1, 'little')
        acceptMsg = [Type, typeAccepted]
        for i in acceptMsg:
            pkt += i
        
        return pkt

    def playGame(self, player):
        print("play game")
        while True:
            print("inside while loop")
           
            Type = player.recieveMessage(1)
            
            # data = skt.recv(1024*1024)
            
            # Type = data[0]
            # Type = 6
            print("recieved type") #This is where my current problem is
            print(Type)
            Type = int.from_bytes(Type, 'little')
            if Type == 1:
                print("Inside msg")
                msg = self.messageType(player)
                player.sendMessage(msg)
                print("msg sent")
            elif Type == 10:
                print("inside character type")
                player.sendMessage(characterType())
            elif Type == 6:
                print("start")
                self.startType(player)
            elif Type == 2:
                # print("inside change room type")
                if player.playing and player.alive:
                    # print("change room if")
                    roomNum = player.recieveMessage(2)
                    roomNum = int.from_bytes(roomNum, 'little')
                    self.changeRoomType(player, roomNum)
                elif player.playing == False or player.alive == False:
                    error = self.sendError(1)
                    player.sendMessage(error)
                else: 
                    error = self.sendError(5)
                    player.sendMessage(error)
            elif Type == 3:
                print("inside fight type")
                self.fightType(player)
            elif Type == 4:
                print("inside pvp")
                error = self.sendError(8)
                player.sendMessage(error)
            elif Type == 5:
                print("inside loot")
                lootTarget = player.recieveMessage(32)
                lootTarget = lootTarget.decode('utf-8')
                loot = self.lootType(player, lootTarget)
                if loot:
                    player.sendMessage(player.characterType)
                else:
                    error = self.sendError(6)
                    player.sendMessage(error)
            elif Type == 12:
                print("inside leave")
                player.sock.close()
            else:
                error = self.sendError(0)
                player.sendMessage(error)
        Type = 0

    def fightType(self, player):
        print("fight")
        with self.lock:
            if player.playing and player.alive:
                r = self.rooms.get(player.getRoomNum())
                r.fightMonster(player)
                playerInfo = player.characterType()
                player.sendMessage(playerInfo)
            else:
                error = self.sendError(7)
                player.sendMessage(error)


    def startType(self, player):
        # print("made it to start")
        player.sendMessage(self.acceptType(6))
        player.setPlaying(True)
        playerInfo = player.characterType()
        playerRoom = self.initialRoom
        player.sendMessage(playerInfo)

    
        allRoomInfo = playerRoom.roomDescription2()
        # print(allRoomInfo)
        player.sendMessage(allRoomInfo)

        # print("Sent room info")
        
        playerRoom.addPlayer(player)
        print("Player %s started playing" % player.getName())
        # self.playGame(player)
        return

    def messageType(self, player):
        print("msg")
        with self.lock:
            msgType = 1
            Type = msgType.to_bytes(1, 'little')
            msgLen = player.recieveMessage(2)
            recipient = player.recieveMessage(32)
            sender = player.recieveMessage(32)
            length = int.from_bytes(msgLen, 'little')
            msg = player.recieveMessage(length)

            pkt = bytearray()
            sendMsg = [Type, msgLen, recipient, sender, msg]

            for i in sendMsg:
                pkt += i

            print(pkt)
            return pkt
            # player.sendMessage(pkt)
            
            player.sendMessage(self.acceptType(1))

    def lootType(self, player, target):
        print("loot")
        target = self.players[target]
        if not target.alive:
            player.gold += target.getGold()
            return True
        else: 
            return False
    
    def changeRoomType(self, player, r):
        # print("changeroom")
        print(r)
        # print('djkdjd')
        with self.lock:
            room = player.getRoom()
            print(room)
            self.rooms[room].removePlayer(player)
            self.rooms[r].addPlayer(player)
            # room.addPlayer(player)
            player.changeRoom(r)
            roomInfo = self.rooms[r].roomDescription2()
            # print(roomInfo)
            player.sendMessage(roomInfo)
            # print("Room info sent")
            print(player.getRoom())
            # for i in roomInfo:
            #     player.sendMessage(i)

    def gameInfo(self):
        print("gameInfo")

        self.errors[0] = "Other (not covered by any below error code)"
        self.errors[1] = "Bad room. Attempt to change to an inappropriate room"
        self.errors[2] = "Player Exists. Attempt to create a player that already exists."
        self.errors[3] = "Bad Monster. Attempt to loot a nonexistent or not present monster."
        self.errors[4] = "Stat error. Caused by setting inappropriate player stats."
        self.errors[5] = "Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER."
        self.errors[6] = "No target. Sent in response to attempts to loot nonexistent players, fight players in different rooms, etc."
        self.errors[7] = "No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)"
        self.errors[8] = "No player vs. player combat on the server. Servers do not have to support player-vs-player combat."
    
        theGreatHall = Room(1, "The Great Hall", "Welcome to the Greate Hall! The ceiling has been enchanted to look like the sky, while hundreds of lit candles float above the students seated at four long tables (one for each house). The room is especially beautiful when it appears to be snowing inside. But, the best part: unlimited amounts of food can instantly materialize on the tables.")
        library = Room(2, "Library", "You have entered the library. Make sure to stay out of the restricted section if you want to stay alive!")
        restrictedSection = Room(3, "Restricted Section", "I see you didn't listen to my warning. Good luck.")
        darkArtsClassroom = Room(4, "Dark Arts Classroom", "You have entered the Defense Against The Dark Arts Classroom. If you can leave with your life you have passed your first lesson.")
        astronomyRoom = Room(5, "The Astronomy Room", "Welcome to the tallest tower at Hogwarts, The Astronomy Room. The Astronomy room itself is gorgeous, adorned by planetary models of spun glass that circle one another. Unfortunately, the beauty of this room is tainted by the awful fate of Dumbledore")
        commonRoom = Room(6, "Gryffindor Common Room", "Themes of red and gold persist throughout the room, with a portrait of a lion hanging above the large stone fireplace that keeps the room warm, but don't get to comfortable.")
        bathroom = Room(7, "Prefect's Bathroom", "You have entered the luxury bathroom with a ridiculously massive in-ground swimming pool surrounded by many golden taps in various shapes and sizes, each providing a different scented soap. Check the stalls for ghosts before you hop in the bath.")
        snapesOffice = Room(8, "Snape's Office", "Snape's the type of guy to prefer having his office in the dungeons. It has that dimly-lit, creepy vibe, augmented by the hundreds of slimy things floating inside various vials on the shelves.")
        headmastersOffice = Room(9, "The Headmaster's Office", "The headmaster's office is the crowning jewel of all the rooms in the Hogwarts castle. It's located in the Headmaster's tower, comprised of three consecutive turret towers resting one on another. But the weirdness only starts there. Don't worry this is the one place you are truly safe.")
        chamberOfSecrets = Room(10, "The Chamber of Secrets", "There is no room in Hogwarts that is as eerie as the Chamber of Secrets. The fate of Hogwarts is in your hands!")
        roomList = [theGreatHall, library, restrictedSection, darkArtsClassroom, astronomyRoom, commonRoom, bathroom, snapesOffice, headmastersOffice, chamberOfSecrets]
    
        for room in roomList:
            self.rooms[room.getRoomNum()] = room

        self.initialRoom = theGreatHall

        chamberOfSecrets.addMonster(Monster(10, "Basalisk",  200, 150, 50, "These giant, bright green serpents can instantly kill anyone who looks into their eyes. They have armored skin that can deflect spells and venomous fangs."))
        darkArtsClassroom.addMonster(Monster(4, "Pixie", 5, 25, 10, "These electric blue mischief-makers love playing tricks."))
        commonRoom.addMonster(Monster(6, "Boggart", 25, 150, 50, "Boggarts lurk in cupboards and when confronted, take the form of your worst fears. "))
        bathroom.addMonster(Monster(7, "Moaning Myrtle", 5, 100, 100, "She is a squat ghost with lank hair, pimples, and thick glasses. She seldom smiles and takes offense at the least excuse, crying rivers of tears and wailing."))
        restrictedSection.addMonster(Monster(3, "Acromantula", 300, 200, 100, "A giant spider, the size of a small elephant, with a black and grey hairy body, eight milky-white eyes and valuable venom."))
        snapesOffice.addMonster(Monster(8, "Dementor", 100, 50, 50, "These creatures are the guards of Azkaban. They feed on human happiness and can extract souls with their Dementor's Kiss."))
        


        theGreatHall.addConnection(library)
        theGreatHall.addConnection(darkArtsClassroom)
        theGreatHall.addConnection(headmastersOffice)
        theGreatHall.addConnection(commonRoom)

        library.addConnection(theGreatHall)
        library.addConnection(restrictedSection)

        restrictedSection.addConnection(library)

        darkArtsClassroom.addConnection(theGreatHall)
        darkArtsClassroom.addConnection(snapesOffice)

        snapesOffice.addConnection(darkArtsClassroom)
        snapesOffice.addConnection(commonRoom)

        headmastersOffice.addConnection(theGreatHall)
        headmastersOffice.addConnection(astronomyRoom)

        astronomyRoom.addConnection(headmastersOffice)

        commonRoom.addConnection(theGreatHall)
        commonRoom.addConnection(bathroom)

        bathroom.addConnection(commonRoom)
        bathroom.addConnection(chamberOfSecrets)

        chamberOfSecrets.addConnection(bathroom)



    

    
      
       