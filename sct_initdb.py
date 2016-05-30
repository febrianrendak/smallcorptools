#!/usr/bin/python
# Testing Database instance for CPE Manager

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
dbh = client.jawdat_internal

#drop if collections exists
dbh.drop_collection("employees")

eh = dbh.employees
ne = [
      {
          "username" : "riftadi@jawdat.com",
          "jawdat_id" : "012",
          "role" : ["staff"],
          "fullname" : "Mohammad Riftadi",
          "position" : "Solutions Manager",
          "division" : "presales",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "tedhi@jawdat.com",
          "jawdat_id" : "001",
          "role" : ["manager"],
          "fullname" : "Tedhi Achdiana",
          "position" : "Managing Director",
          "division" : "bod",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "afilia@jawdat.com",
          "jawdat_id" : "004",
          "role" : ["accounting"],
          "fullname" : "Afilia Ratna",
          "position" : "Managing Director",
          "division" : "bod",
          "supervisor" : "tedhi@jawdat.com",
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
