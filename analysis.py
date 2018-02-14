import sqlite3
import pandas as pd
import math
import os

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

    results_df = win_df.merge(loss_df, on=["Election_id"], suffixes=("_win", "_loss"), how="outer")
    # results_df = results_df.loc[results_df["Votes_loss"] != 0]

    return results_df


def get_efficiency_gap(win, loss):

    results = compare_wl(win, loss)

    results["wasted_wins"] = results["Votes_win"] - (((results["Votes_win"] + results["Votes_loss"])*.5) + 1).apply(math.floor)
    results = results.loc[results["Votes_loss"] != 0]
    results["total_votes"] = results["Votes_win"] + results["Votes_loss"]

    total_votes = results[["State", "Year", "total_votes"]].groupby(["State", "Year"], as_index=False).sum()

    wasted_votes_loss = results.groupby(["State", "Year", "Party_loss"], as_index=False)["Votes_loss"].sum()
    wasted_votes_wins = results.groupby(["State", "Year", "Party_win"], as_index=False)["wasted_wins"].sum()

    wasted_df = wasted_votes_loss.merge(wasted_votes_wins, left_on=["State", "Year", "Party_loss"],
                                        right_on=["State", "Year", "Party_win"], how="outer")
    wasted_df.fillna(0, inplace=True)

    wasted_df.loc[(wasted_df["Party_loss"] != 0) & (wasted_df["Party_win"] != 0), "Party"] = wasted_df["Party_win"]
    wasted_df.loc[(wasted_df["Party_loss"] == 0) & (wasted_df["Party_win"] != 0), "Party"] = wasted_df["Party_win"]
    wasted_df.loc[(wasted_df["Party_loss"] != 0) & (wasted_df["Party_win"] == 0), "Party"] = wasted_df["Party_loss"]

    wasted_df.drop(["Party_win", "Party_loss"], axis=1, inplace=True)

    wasted_df["wasted_votes"] = wasted_df["wasted_wins"] + wasted_df["Votes_loss"]

    wasted_df_dem = wasted_df.loc[wasted_df["Party"] == "Democrat"]
    wasted_df_rep = wasted_df.loc[wasted_df["Party"] == "Republican"]

    efficency_df = pd.merge(wasted_df_dem[["State", "Year", "wasted_votes"]],
                            wasted_df_rep[["State", "Year", "wasted_votes"]],
                            on=["State", "Year"], suffixes=["_dem", "_rep"])

    efficency_df = pd.merge(efficency_df, total_votes, on=["State", "Year"])
    efficency_df["gap"] = (efficency_df["wasted_votes_dem"] - efficency_df["wasted_votes_rep"])/efficency_df["total_votes"]

    return efficency_df


if __name__ == '__main__':

    win = get_winner()
    loss = get_loser()
    efficency_df = get_efficiency_gap(win, loss)
    efficency_df.to_csv("test.csv")
    os.system("xdg-open test.csv")