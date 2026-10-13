import re


# ======================================
# REPLACE OCR
# ======================================

replace_dict = {
    "1NF":"INF",
    "1F":"INF",
    "IXF":"INF",
    "[F":"INF",
    "1XF":"INF",
    "INFG":"INF",
    "INE":"INF",
    "INP":"INF",
    "1NE":"INF",
    "INR":"INF",
    "[NF":"INF",
    "[NP":"INF",
    "UN1":"UNI",
    "0NI":"UNI",
    "0N1":"UNI",
    "JNI":"UNI",
    "NF":"INF",
    "IF":"INF",
    "F620":"INF620",
    "INF62O":"INF620",
    "INF620O":"INF6200",
    "UNI620l":"UNI6201",
    "INF620l":"INF6201",
}

def clean_text(text):

    if text is None:

        return ""

    text = str(text)

    for salah, benar in replace_dict.items():

        text = text.replace(

            salah,

            benar

        )

    text = re.sub(

        r'((?:INF|UNI)\d{5})I\b',

        r'\g<1>1',

        text

    )

    text = re.sub(

        r'((?:INF|UNI)\d{5})O\b',

        r'\g<1>0',

        text

    )

    return text

import pandas as pd

def clean_dataframe(df):

    df = df.copy()

    df["TEXT"] = df["TEXT"].apply(

        clean_text

    )

    return df