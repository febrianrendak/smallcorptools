#!/usr/bin/python
# by: Mohammad Riftadi <riftadi@jawdat.com>
# Testing Database instance for CPE Manager

from pymongo import MongoClient
import hashlib

client = MongoClient('mongodb://localhost:27017/')
dbh = client.jawdat_internal

#drop if collections exists
dbh.drop_collection("employees")

eh = dbh.employees
ne = [
      {
          "username" : "riftadi@jawdat.com",
          "secret" : hashlib.md5("jawdat123").hexdigest(),
          "jawdat_id" : "012",
          "roles" : ["staff", "admin"],
          "fullname" : "Mohammad Riftadi",
          "position" : "Solutions Manager",
          "division" : "solutions",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "riftadi.jpg",
      },

      {
          "username" : "tedhi@jawdat.com",
          "secret" : hashlib.md5("jawdat123").hexdigest(),
          "jawdat_id" : "001",
          "roles" : ["manager", "director"],
          "fullname" : "Tedhi Achdiana",
          "position" : "Managing Director",
          "division" : "bod",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "tedhi.jpg",
      },

      {
          "username" : "himawan@jawdat.com",
          "secret" : hashlib.md5("jawdat123").hexdigest(),
          "jawdat_id" : "002",
          "roles" : ["manager", "director"],
          "fullname" : "Himawan Nugroho",
          "position" : "CEO",
          "division" : "bod",
          "supervisor" : "himawan@jawdat.com",
          "profpic" : "himawan.jpg",
      },

      {
          "username" : "afilia@jawdat.com",
          "secret" : hashlib.md5("jawdat123").hexdigest(),
          "jawdat_id" : "004",
          "roles" : ["accounting", "hrd"],
          "fullname" : "Afilia Ratna",
          "position" : "HRD Manager",
          "division" : "bod",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "afilia.jpg",
      },

      {
          "username" : "ericson@jawdat.com",
          "secret" : hashlib.md5("jawdat123").hexdigest(),
          "jawdat_id" : "016",
          "roles" : ["staff"],
          "fullname" : "Ericson Ferdinand P.",
          "position" : "Engineering Manager",
          "division" : "engineering",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "ericson.jpg",
      },

      {
          "username" : "tri.karamoy@jawdat.com",
          "secret" : hashlib.md5("jawdat123").hexdigest(),
          "jawdat_id" : "024",
          "roles" : ["staff"],
          "fullname" : "Tri Primandra Karamoy",
          "position" : "Product Manager",
          "division" : "solutions",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "tri.karamoy.jpg",
      },
]

print eh.insert(ne)

#drop if collections exists
dbh.drop_collection("costcenters")

cch = dbh.costcenters
ncc = [
      {
          "costcenter_id" : "opex", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Operational Expense Jawdat",
          "costcenter_budget" : 500000000,
          "costcenter_status" : "active"
      },

      {
          "costcenter_id" : "prelintasjah", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Presales Lintasarta Jatiluhur",
          "costcenter_budget" : 350000000,
          "costcenter_status" : "active"
      },

      {
          "costcenter_id" : "protlkstracpe", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Project Telkomtelstra CPE",
          "costcenter_budget" : 1000000000,
          "costcenter_status" : "active"
      },

      {
          "costcenter_id" : "suplintassdh", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Support Lintasarta SDH",
          "costcenter_budget" : 200000000,
          "costcenter_status" : "active"
      },
]

print cch.insert(ncc)

rch = dbh.reimburse_claims
nrc = [
        {
            "username" : "riftadi@jawdat.com",
            "fullname" : "Mohammad Riftadi",
            "period" : "0516", # may (05) 2016 (16)
            # "date_submitted" : datetime.now(),
            "approved_by" : "tedhi@jawdat.com",
            "status" : "submitted", # presubmitted, submitted, approved, rejected
            # "status_desc" : "OK",
            # "approval_date" : datetime.now(),
            "expense_list" : [
                {
                    "date" : "02/05/2016",
                    "description" : "Beli Modem",
                    "category" : "logistic",
                    "costcenter" : "opex",
                    "cost" : 300000 # in IDR
                },

                {
                    "date" : "02/05/2016",
                    "description" : "Parkir",
                    "category" : "parking",
                    "costcenter" : "opex",
                    "cost" : 150000 # in IDR
                },

                {
                    "date" : "02/05/2016",
                    "description" : "Makan Siang dengan Sisindokom",
                    "category" : "meal",
                    "costcenter" : "opex",
                    "cost" : 200000 # in IDR
                },
            ]
        },
]
