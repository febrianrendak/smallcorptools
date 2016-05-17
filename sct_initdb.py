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

# rch = dbh.reimburse_claims
nrc = [
        {
            "username" : "riftadi@jawdat.com",
            "month_year" : "0516", # may (05) 2016 (16)
            # "date_submitted" : datetime.now(),
            "approved_by" : "tedhi@jawdat.com",
            "status" : "submitted", # submitted, approved, rejected
            # "status_desc" : "OK",
            # "approval_date" : datetime.now(),
            "expense_list" : [
                {
                    "name" : "Beli Modem",
                    "type" : "logistic",
                    "value" : 300000 # in IDR
                },

                {
                    "name" : "Parkir",
                    "type" : "transportation",
                    "value" : 256000
                },

                {
                    "name" : "Langganan Internet",
                    "type" : "telecommunication",
                    "value" : 300000
                },
            ]
        },
]
