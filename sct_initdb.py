#!/usr/bin/python
# by: Mohammad Riftadi <riftadi@jawdat.com>
# Testing Database instance for CPE Manager

from pymongo import MongoClient
import hashlib

client = MongoClient('mongodb://localhost:27017/')
dbh = client.jawdat_internal

#drop if collections exists
dbh.drop_collection("resetpass")

#drop if collections exists
dbh.drop_collection("employees")

eh = dbh.employees
ne = [
      {
          "username" : "tedhi@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
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
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
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
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "004",
          "roles" : ["accounting", "hrd"],
          "fullname" : "Afilia Ratna",
          "position" : "HRD Manager",
          "division" : "hrd",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "afilia.jpg",
      },

      {
          "username" : "bagus@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "005",
          "roles" : ["staff"],
          "fullname" : "Handoko Baguswasito",
          "position" : "Consulting Engineer",
          "division" : "delivery",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "ary@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "010",
          "roles" : ["staff"],
          "fullname" : "Ary Rahmadian Thala",
          "position" : "Solutions Architect",
          "division" : "delivery",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "riftadi@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "012",
          "roles" : ["staff", "admin"],
          "fullname" : "Mohammad Riftadi",
          "position" : "Solutions Manager",
          "division" : "solutions",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "riftadi.jpg",
      },

      {
          "username" : "ericson.pasaribu@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "016",
          "roles" : ["staff"],
          "fullname" : "Ericson Ferdinand Pasaribu",
          "position" : "Engineering Manager",
          "division" : "engineering",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "ericson.pasaribu.jpg",
      },

      {
          "username" : "nugroho@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "020",
          "roles" : ["staff"],
          "fullname" : "Nugroho Dwi Prasetyo",
          "position" : "Business Analyst",
          "division" : "external",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "panji.harimurti@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "023",
          "roles" : ["staff"],
          "fullname" : "Panji Harimurti",
          "position" : "Tax and Accounting Staff",
          "division" : "finance",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "munandar.rahman@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "031",
          "roles" : ["staff"],
          "fullname" : "Munandar Rahman",
          "position" : "Office Assistant",
          "division" : "ga",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "danav.pratama@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "032",
          "roles" : ["staff"],
          "fullname" : "Danav Pratama",
          "position" : "Office Assistant",
          "division" : "ga",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "tri.karamoy@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "024",
          "roles" : ["staff"],
          "fullname" : "Tri Primandra Karamoy",
          "position" : "Product Manager",
          "division" : "solutions",
          "supervisor" : "tedhi@jawdat.com",
          "profpic" : "tri.karamoy.jpg",
      },

      {
          "username" : "firza.wiratama@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "025",
          "roles" : ["staff"],
          "fullname" : "Firza Agusta Wiratama",
          "position" : "SDN Engineer",
          "division" : "engineering",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "lisa.anggrainy@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "026",
          "roles" : ["staff"],
          "fullname" : "Lisa Anggrainy",
          "position" : "Business Analyst",
          "division" : "external",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "faisal.sonjaya@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "027",
          "roles" : ["staff"],
          "fullname" : "Moh. Faisal Sonjaya",
          "position" : "Asst. PM",
          "division" : "external",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "doni.siringoringo@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "028",
          "roles" : ["staff"],
          "fullname" : "Doni Marlon Siringoringo",
          "position" : "Asst. PM",
          "division" : "external",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "dimas.nugroho@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "029",
          "roles" : ["staff"],
          "fullname" : "Dimas Pandu Nugroho",
          "position" : "UI/UX Developer",
          "division" : "engineering",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "fikri.rahman@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "030",
          "roles" : ["staff"],
          "fullname" : "M. Fikri Ali Rahman",
          "position" : "UI/UX Developer",
          "division" : "engineering",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "febrian.rendak@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "033",
          "roles" : ["staff"],
          "fullname" : "Febrian Rendak",
          "position" : "SDN Engineer",
          "division" : "engineering",
          "supervisor" : "tedhi@jawdat.com",
      },

      {
          "username" : "raisha.nizami@jawdat.com",
          "secret" : hashlib.md5("J@wdat12345").hexdigest(),
          "first_login" : True,
          "jawdat_id" : "034",
          "roles" : ["staff"],
          "fullname" : "Raisha Syifa Nizami",
          "position" : "Asst. PM",
          "division" : "external",
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
          "costcenter_name" : "Operational Expense",
          "costcenter_budget" : 500000000,
          "costcenter_category" : "internal",
          "costcenter_status" : "active"
      },

      {
          "costcenter_id" : "presales", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Presales General",
          "costcenter_budget" : 1000000000,
          "costcenter_category" : "presales",
          "costcenter_status" : "active"
      },

      {
          "costcenter_id" : "pro-tsra-cpe", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Project Telkomtelstra CPE",
          "costcenter_budget" : 500000000,
          "costcenter_category" : "project",
          "costcenter_status" : "active"
      },

      {
          "costcenter_id" : "pro-tsel-eol", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Project Telkomsel EoL",
          "costcenter_budget" : 500000000,
          "costcenter_category" : "project",
          "costcenter_status" : "active"
      },

      {
          "costcenter_id" : "sup-lintas-sdh", # pre -> presales phase, pro->project phase, sup->support phase, should be unique
          "costcenter_name" : "Support Lintasarta SDH",
          "costcenter_budget" : 200000000,
          "costcenter_category" : "support",
          "costcenter_status" : "active"
      },
]

print cch.insert(ncc)

#drop if collections exists
dbh.drop_collection("settings")

sh = dbh.settings
ns = { "setting_name" : "mail", "email_notifications" : "off" }

print sh.insert(ns)

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
