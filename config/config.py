# used for sorting report files by month
MONTH_TO_NUMBER = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

UNKNOWN_CATEGORY_NAME = "UNKNOWN"

# mapping of shops by type
SHOP_TYPES = {
    "GENERAL_SHOP": [
        "ROSSMANN",
        "DECATHLON",
        "DASFUTTERHAUS",
        "TKMaxx",
    ],
    "HEALTH": [
        "Apotheke",
        "AllDentZahnzentrum",
        "BFShealthfinance",
    ],
    "FOOD_SHOP": [
        "ALDI",
        "REWE",
        "Kaufland",
        "Edeka",
        "Metro",
        "kliver",
        "mixmarkt",
        "penny",
        "TEGUTSAGT",
        "lemberg",
        "ROSSMANN",
        "JACQUES",
        "E.LECLERC",
        "GLOBUS",
        "LIDLSAGTDANKE",
        "LidlsagtDanke",
        "AUCHAN",
    ],
    "CASH": [
        ".DEUTSCHE BANKAG",
    ],
    "RENT": [
        "NorbertBeran",
        "VATTENFALLE",
        "Vodafone",
        "Immobilien",
        "GCreGetsafe",
        "Rundfunk",
    ],
    "Education": [
        "Volkshochschule",
        "Linuxf",
        "Udemy",
    ],
    "CAFE": [
        "BAECKER"
        "Baecker ",
        "Backerei",
        "B.ckerei",
        "Kulturbrauerei",
        "Cafe",
        "KAMPS",
        "Restaurant",
        "Liebesbrot",
        "SCHROEER",
        "Espresso",
        "PIZZABOY",
        "DRIES",
    ],
    "TRAVEL": [
        "DBVertriebGmbH",
        "BerlinerVerkehrsbetriebe",
        "Booking",
        "AUSTRIAN",  # austrian airlines
        "RYANAIR",
        "MALLORCA",
        "TAXI",
        "Hotel",
        "Condor",
        "MERCURE",
        "AIRBNB",
    ],
    "Amazon": [
        "Amazon",
        "RivertyGmb",
    ],
    "InternetService": [
        "Spotify",
        "Blizzard",
    ],
    "EVENT": [
        "Eventim.Sports",
        "Kino",
    ]
}
