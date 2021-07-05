# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
from rake_nltk import Rake

class ActionSearchName(Action):
    def name(self) -> Text:
        return "action_product_details_response"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        a = tracker.latest_message['text'].lower()

        rake_nltk_var = Rake()
        df = pd.read_excel("Product Description.xlsx")
        df.fillna(0, inplace=True)

        extracted_keyword_prod_desc_list = list()

        for index, row in df.iterrows():
            rake_nltk_var.extract_keywords_from_text(row['Short method description'])
            keyword_extracted = rake_nltk_var.get_ranked_phrases()
            extracted_keyword_prod_desc_list.append(keyword_extracted)

        df['Short method description keyword'] = extracted_keyword_prod_desc_list

        rake_nltk_var.extract_keywords_from_text(a)
        keyword_extracted = rake_nltk_var.get_ranked_phrases()
        extracted_keyword_prod_desc_list.append(keyword_extracted)

        tools = list()
        contact_person = list()
        flag = 0
        for index, row in df.iterrows():
            if keyword_extracted == row['Short method description keyword']:
                tools.append(df['Tool'][index])
                contact_person.append(df['Contact person'][index])
                flag = 1
                break

        count = 0
        if flag == 0:
            for index, row in df.iterrows():
                if not set(keyword_extracted).isdisjoint(row['Short method description keyword']):
                    tools.append(df['Tool'][index])
                    contact_person.append(df['Contact person'][index])
                else:
                    count += 1

        def listToString(s):
            if type(s[0]) == float:
                str1 = ""
                str2 = str1.join("xyz")
            else:
                str1 = ","
                str2 = str1.join(s)
            return str2

        if count == df.shape[0]:
            message = "please enter the details again as the bot didn’t find anything."
            dispatcher.utter_message(text=message)
        else:
            if contact_person[0] == 0 and len(tools)>1:
                message = "\"The most suitable tool are " + listToString(tools) + ". Click here for more details https://www.google.com/. There is no contact person for this tool.\"\nIs this what you are looking for?"
                buttons = []
                buttons.append({"title": "Yes", "payload": "/Yes_verify"})
                buttons.append({"title": "No", "payload": "/No_verify"})
                dispatcher.utter_message(text=message, buttons=buttons)
            elif contact_person[0] == 0 and len(tools) == 1:
                message = "\"The most suitable tool is " + listToString(tools) + ". Click here for more details https://www.google.com/. There is no contact person for this tool.\"\nIs this what you are looking for?"
                buttons = []
                buttons.append({"title": "Yes", "payload": "/Yes_verify"})
                buttons.append({"title": "No", "payload": "/No_verify"})
                dispatcher.utter_message(text=message, buttons=buttons)
            elif contact_person[0] != 0 and len(tools)>1:
                message = "\"The most suitable tool are "+ listToString(tools)+". Click here for more details https://www.google.com/ and please contact to "+ listToString(list(set(contact_person)))+" for further information.\"\nIs this what you are looking for?"
                buttons = []
                buttons.append({"title": "Yes", "payload": "/Yes_verify"})
                buttons.append({"title": "No", "payload": "/No_verify"})
                dispatcher.utter_message(text=message, buttons=buttons)
            else:
                message = "\"The most suitable tool is " + listToString(tools) + ". Click here for more details https://www.google.com/ and please contact to " + listToString(list(set(contact_person))) + " for further information.\"\nIs this what you are looking for? "
                buttons = []
                buttons.append({"title": "Yes", "payload": "/Yes_verify"})
                buttons.append({"title": "No", "payload": "/No_verify"})
                dispatcher.utter_message(text=message, buttons=buttons)

        return []
