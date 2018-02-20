import sqlite3
import pandas as pd
import math
import os

cnxn = sqlite3.connect("house_elections.db")
cn = cnxn.cursor()


def get_winner(election_type):

    if election_type:

        cn.execute("SELECT e.election_id, e.state, e.year, r.votes, r.party FROM elections e "
                   "LEFT OUTER JOIN results r ON r.election_id = e.election_id "
                   "INNER JOIN (SELECT r2.election_id, MAX(r2.votes) as Votes FROM results r2 "
                   "GROUP BY r2.election_id) b ON r.Election_Id=b.election_id AND b.votes=r.votes "
                   "WHERE r.party IN ('Democrat', 'Republican') AND e.Federal=?", (election_type,))

    else:

        cn.execute("SELECT e.election_id, e.state, e.year, r.votes, r.party FROM elections e "
                   "LEFT OUTER JOIN results r ON r.election_id = e.election_id "
                   "INNER JOIN (SELECT r2.election_id, MAX(r2.votes) as Votes FROM results r2 "
                   "GROUP BY r2.election_id) b ON r.Election_Id=b.election_id AND b.votes=r.votes "
                   "WHERE r.party IN ('Democrat', 'Republican')")

    return cn.fetchall()


def get_losers(election_type):

    if election_type:

        cn.execute("SELECT e.election_id, r.votes, r.party FROM elections e "
                   "LEFT OUTER JOIN results r ON r.election_id = e.election_id "
                   "INNER JOIN (SELECT r2.election_id, MAX(r2.votes) as Votes FROM results r2 "
                   "GROUP BY r2.election_id) b ON r.Election_Id=b.election_id AND b.votes<>r.votes "
                   "WHERE r.party IN ('Democrat', 'Republican') AND e.Federal=? AND r.votes > 0", (election_type,))

    else:
        cn.execute("SELECT e.election_id, r.votes, r.party FROM elections e "
                   "LEFT OUTER JOIN results r ON r.election_id = e.election_id "
                   "INNER JOIN (SELECT r2.election_id, MAX(r2.votes) as Votes FROM results r2 "
                   "GROUP BY r2.election_id) b ON r.Election_Id=b.election_id AND b.votes<>r.votes "
                   "WHERE r.party IN ('Democrat', 'Republican')  AND r.votes > 0")

    return cn.fetchall()


def get_total_votes(election_type):

    if election_type:

        cn.execute("SELECT e.election_id, SUM(r.votes) "
                   "FROM elections e "
                   "INNER JOIN results r ON r.election_id=e.election_id "
                   "WHERE e.Federal=? "
                   "GROUP BY e.election_id", (election_type,))

    else:

        cn.execute("SELECT e.election_id, SUM(r.votes) "
                   "FROM elections e "
                   "INNER JOIN results r ON r.election_id=e.election_id "
                   "GROUP BY e.election_id")

    return cn.fetchall()


def compare_wl(election_type):
    win_df = pd.DataFrame(get_winner(election_type), columns=["Election_id", "State", "Year", "Votes", "Party"])
    loss_df = pd.DataFrame(get_losers(election_type), columns=["Election_id", "Votes", "Party"])
    total_votes = pd.DataFrame(get_total_votes(election_type), columns=["Election_id", "TotalVotes"])

    results_df = win_df.merge(loss_df, on=["Election_id"], suffixes=("_win", "_loss"), how="inner")
    results_df = results_df.merge(total_votes, on=["Election_id"], how="inner")

    return results_df


def get_efficiency_gap(election_type):

    if election_type.lower() not in ("federal", "state", "all"):

        raise TypeError("Type is not correctly supplied.")

    if election_type.lower() == "federal":

        fed_bool = 1

    elif election_type.lower() == "all":

        fed_bool = 1

    else:

        fed_bool = None

    results = compare_wl(fed_bool)

    results["wasted_wins"] = results["Votes_win"] - (((results["TotalVotes"]) * .5) + 1).apply(
        math.floor)
    results = results.loc[results["Votes_loss"] != 0]
    results["total_votes"] = results["Votes_win"] + results["Votes_loss"]

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

    efficiency_df = pd.merge(wasted_df_dem[["State", "Year", "wasted_votes"]],
                            wasted_df_rep[["State", "Year", "wasted_votes"]],
                            on=["State", "Year"], suffixes=["_dem", "_rep"])

    total_votes = results.groupby(["State", "Year"], as_index=False)["TotalVotes"].sum()

    efficiency_df = pd.merge(efficiency_df, total_votes, on=["State", "Year"])
    efficiency_df["gap"] = (efficiency_df["wasted_votes_dem"] - efficiency_df["wasted_votes_rep"]) / efficiency_df[
        "TotalVotes"]

    # efficiency_df = efficiency_df.loc[(efficiency_df.Year >= 2000) & (efficiency_df.Year <= 2010)]
    #
    # efficiency_df = efficiency_df.groupby(["State"], as_index=False)["gap"].mean()

    # print(efficiency_df)

    return efficiency_df


def simulate_elections(win, loss):
    cn.execute("SELECT e.election_id, e.state, e.year, r.votes, r.party FROM elections e "
               "LEFT OUTER JOIN results r ON r.election_id = e.election_id")
    print(cn.fetchall())
    # print(compare_wl(win, loss))


if __name__ == '__main__':
    # print(get_dems())
    # print(get_rep())
    # print(get_other())
    # win = get_winner()
    # print(win)
    # loss = get_loser()
    # compare_wl()
    efficiency_gap = get_efficiency_gap("federal")
    efficiency_gap.to_csv("test.csv")
    os.system("xdg-open test.csv")
    # simulate_elections(win, loss)
