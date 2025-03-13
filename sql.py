from asyncore import write
from re import T
import sqlite3
from tkinter.tix import Tree
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from binascii import b2a_hex, a2b_hex
import secrets
# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase(): 
    '''
        Our SQL Database

    '''
    running = None

    # Get the database running
    def __init__(self, database_arg=":memory:"):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()
        SQLDatabase.running = self

    # ONly one statement, can defend sql injection,output error message to outerr
    def execute(self, sql_string,para=()):
        out = None
        try:
            out = self.cur.execute(sql_string,para)
        except Exception as s:
            f = open("outerr","a")
            f.write(str(s)+"\n")
            f.write(sql_string)
            f.close()
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.execute("DROP TABLE IF EXISTS Messages")
        self.execute("DROP TABLE IF EXISTS FriendPairs")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            username TEXT PRIMARY KEY,  
            password TEXT,
            salt TEXT,
            iv TEXT,
            plain_pub_key TEXT,
            chipter_pri_key TEXT,
            admin INTEGER DEFAULT 0
        )""")

        self.execute("""CREATE TABLE Messages(
            sender TEXT,
            receiver TEXT,
            message TEXT,
            signature TEXT,
            encrypted_AES_key TEXT,
            iv TEXT,
            date TEXT
            )""")
        self.execute("""CREATE TABLE FriendPairs(
            USER1 TEXT,
            USER2 TEXT
            )""")
        self.commit()

        # Add our admin user
        #self.add_user('admin', admin_password, admin=1)

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------
    def slowHash(text):
        for _ in range(10000):
            hashObj  = SHA512.new()
            hashObj.update(bytes(text, encoding="utf-8"))
            text = hashObj.hexdigest()
        return text
    # Add a user to the database
    def add_user(self, username, password, iv,aes_pri_key,pub_key, admin=0):
        if len(username) > 20:
            return None
        sql_query = """
                SELECT * 
                FROM Users
                WHERE username = ?
            """
        self.execute(sql_query,[username])
        res = self.cur.fetchone()
        if res is not None:
            return False
        salt = secrets.token_urlsafe(32)
        sql_cmd = """
                INSERT INTO Users 
                VALUES(?,?,?,?,?,?,?)
            """
        # use sha-512 ** 10000 to hash
        self.execute(sql_cmd,[username, SQLDatabase.slowHash(password + salt) , salt,iv, pub_key,  aes_pri_key,admin])
        res = self.cur.fetchone()
        self.commit()
        return True

    #-----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT password,salt 
                FROM Users
                WHERE username = ?
            """

        # If our query returns
        self.execute(sql_query,[username])
        res = self.cur.fetchone()
        if res is None:
            return False
        salt = res[1]
        hashcode = res[0]
        if SQLDatabase.slowHash(password + salt) == hashcode:
            return True
        else:
            return False
    def check_exists(*users):
        return True
    #-----------------------------------------------------------------------------
    # ask for the public key of the user
    def getPubKey(self,aim_user):
        sql_query = """
                SELECT plain_pub_key 
                FROM Users
                WHERE username = ?
            """
        self.execute(sql_query,[aim_user])
        res = self.cur.fetchone()
        if res is None:
            return False
        return res[0]
    #-----------------------------------------------------------------------------
    # ask for the encrypted private key of the user
    def getPrivateKey(self,aim_user,key):
        key = key + (32 - len(key) % 32) * '0'
        sql_query = """
                SELECT chipter_pri_key, iv
                FROM Users
                WHERE username = ?
            """
        self.execute(sql_query,[aim_user])
        res = self.cur.fetchone()
        if res is None:
            return False
        chipter_pri_key = res[0]
        iv = res[1]
        return chipter_pri_key,iv

    #-----------------------------------------------------------------------------
    # add messages to database
    def add_msg(self,text,sender,receiver):
        texts = text.split("\0")
        text = texts[0]
        key = texts[1]
        iv = texts[2]
        signature = texts[3]
        sql_cmd="""
                INSERT INTO Messages
                VALUES(?,?,?,?,?,?,(SELECT datetime('now')))"""
        self.execute(sql_cmd,[sender,receiver,text,signature,key,iv])
        self.commit()
        return True

    #-----------------------------------------------------------------------------
    # get messages from database
    def get_msg(self,receiver):
        sql_cmd = """
                SELECT sender, message, date,signature,encrypted_AES_key,iv FROM Messages
                WHERE receiver = ?
                """
        self.execute(sql_cmd,[receiver])
        l = [0,chr(0)]
        res = self.cur.fetchone()
        while res != None:
            text = res[1]
            sender = res[0]
            signature = res[3]
            AES_key = res[4]
            iv = res[5]
            l.append(sender)
            l.append(chr(0))
            l.append(text)
            l.append(chr(0))
            l.append(AES_key)
            l.append(chr(0))
            l.append(iv)
            l.append(chr(0))
            l.append(signature)
            l.append(chr(0))
            l[0] += 1
            res = self.cur.fetchone()
        return l
