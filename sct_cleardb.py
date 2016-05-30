#!/usr/bin/python
# Testing Database instance for CPE Manager

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
dbh = client.jawdat_internal

#drop if collections exists
dbh.drop_collection("employees")
dbh.drop_collection("reimburse_claims")
