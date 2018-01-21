import sqlite3
import pandas as pd
import math

cnxn = sqlite3.connect("house_elections.db")
cn = cnxn.cursor()


def get_winner():

    cn.execute("SELECT e.election_id, e.state, e.year, r.votes, r.party FROM elections e "
               "LEFT OUTER JOIN results r ON r.election_id = e.election_id "
               "INNER JOIN ("
                        "SELECT e2.election_id, MAX(r2.votes) AS votes FROM elections e2 "
                        "LEFT OUTER JOIN results r2 ON r2.election_id = e2.election_id "
                        "GROUP BY e2.election_id) b ON r.votes = b.votes AND b.election_id=e.election_id")

    return cn.fetchall()


def get_loser():

    cn.execute("SELECT e.election_id, r.votes, r.party FROM elections e "
               "LEFT OUTER JOIN results r ON r.election_id = e.election_id "
               "INNER JOIN ("
                            "SELECT e2.election_id, MIN(r2.votes) AS votes FROM elections e2 "
                            "LEFT OUTER JOIN results r2 ON r2.election_id = e2.election_id "
                            "GROUP BY e2.election_id) b ON r.votes = b.votes AND b.election_id=e.election_id")

    return cn.fetchall()


def compare_wl(winners, losers):


    win_df = pd.DataFrame(winners, columns=["Election_id", "State", "Year", "Votes", "Party"])
    loss_df = pd.DataFrame(losers, columns=["Election_id", "Votes", "Party"])

    results_df = win_df.merge(loss_df, on=["Election_id"], suffixes=("_win", "_loss"))
    results_df = results_df.loc[results_df["Votes_loss"] != 0]

    return results_df

win = get_winner()
loss = get_loser()

results = compare_wl(win, loss)

print(results.groupby(["State", "Year", "Party_loss"])["Votes_loss"].sum())

print(results["Votes_win"] - (((results["Votes_win"] + results["Votes_loss"])*.5) + 1).apply(math.floor))