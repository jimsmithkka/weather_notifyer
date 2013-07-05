weather_notifyer
================

Web CGI and SMS notifyer script for checking/alerting people of weather advisories in county/regions they specify


Need to add a tie between User Auth name with listed zones, and associated sms numbers (could use a data-dumper for initial creation)

Proposed data structure is :

uid1 {
    location1 {
              number1,
              number2,
              numberN,
    },
    location2 {
              number1,
              number2,
              numberN,
    },
    location3 {
              number1,
              number2,
              numberN,
    },
},
uid2 {
    location1 {
              number1,
              number2,
              numberN,
    },
    location2 {
              number1,
              number2,
              numberN,
    },
    location3 {
              number1,
              number2,
              numberN,
    },
},
