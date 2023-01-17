from pymongo import MongoClient
import certifi
ca = certifi.where()
mongo = MongoClient("MONGO-DB-CONNECT-LINK", tlsCAFile=ca)