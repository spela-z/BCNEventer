import pandas as pd
import argparse
import numpy as np
from sklearn.cluster import KMeans
from sklearn.model_selection import cross_val_score
import sys
sys.path.append('../scripts/')
import user_generator as gen

EVENT = 'Events'
AV_RATE = "Average rating"
COUNTS = "Counts"
SIMILARITY = "similarity"
RATES = 'Rates'

pd.options.mode.chained_assignment = None  # default='warn'

class Event_DB():
    
    def __init__(self, df):
        self.df = df
        df["Average rating"] = df.drop([EVENT], axis=1).mean(axis=1)
        df["Counts"] = [df[df[EVENT] == event].drop([EVENT, AV_RATE], axis=1).dropna().shape[1] for event in df[EVENT]]
        
    def retrieve_votes(self, event):
        return self.df[self.df[EVENT] == event].drop([EVENT, AV_RATE, COUNTS], axis=1).shape[1]
    
    def retrieve_mean(self, event):
        return self.df[self.df[EVENT] == event].drop([EVENT, AV_RATE, COUNTS], axis=1).mean(axis=1).values
    
    def retrieve_similar_events(self, event, number):
        general_df  = self.df[self.df[EVENT] != "Improv Jam and Improv Show!"]
        event_to_compare = self.df[self.df[EVENT] == "Improv Jam and Improv Show!"].drop([EVENT, AV_RATE, COUNTS], axis=1)
        rest_events = self.df[self.df[EVENT] != "Improv Jam and Improv Show!"].drop([EVENT, AV_RATE, COUNTS], axis=1)
        correlation = [event_to_compare.corrwith(rest_events.loc[ix], axis=1).values[0] for ix in rest_events.index]
        general_df[SIMILARITY] = correlation
        similars = general_df.nlargest(10, [SIMILARITY])[EVENT].tolist()[0:number]
        return similars

    def retrieve_similar_users(self, user):
        users = self.df.drop([EVENT, AV_RATE, COUNTS], axis=1).transpose()
        clf = KMeans(n_clusters=100, random_state=0).fit(users)
        users["cluster"] = clf.labels_
        user_cluster = clf.predict(user.retrieve_df().drop(EVENT, axis=1)[RATES].values.reshape(1,-1))
        return (users[users["cluster"] == user_cluster[0]].index.values)


    def retrieve_events(self):
        return self.df[EVENT]

def parse_args():
    parser = argparse.ArgumentParser(description="Recommend n similar events")
    parser.add_argument("event", type=str, nargs='+', help="Reference event to look for similar ones")
    parser.add_argument("-n", "--number", type=int, help="Number of similar events to retrieve", default=1)
    args = parser.parse_args()
    args.event = " ".join(args.event)

    return args
 


if __name__ == "__main__":
    args = parse_args()
    event_db = Event_DB(pd.read_csv("random_users.csv"))
    similar_events = event_db.retrieve_similar_events(args.event, args.number)
    print("The list of {} similars events to {} is:".format(args.number, args.event))
    print("\n".join(similar_events))
    user = gen.create_user("Dani", event_db.retrieve_events())
    similar_users = event_db.retrieve_similar_users(user)
    print("\nThe next users are similar to {}:".format(user.name))
    print("\n".join(similar_users))

