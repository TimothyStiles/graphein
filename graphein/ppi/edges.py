"""Functions for adding edges to a PPI Graph from parsed STRING & BIOGRID API call outputs"""
# %%
# Graphein
# Author: Arian Jamasb <arian@jamasb.io>, Ramon Vinas
# License: MIT
# Project Website: https://github.com/a-r-j/graphein
# Code Repository: https://github.com/a-r-j/graphein
import logging

import networkx as nx
import pandas as pd

from graphein.ppi.parse_biogrid import BIOGRID_df
from graphein.ppi.parse_stringdb import STRING_df

log = logging.getLogger(__name__)


def add_string_edges(G: nx.Graph, **kwargs) -> nx.Graph:
    """
    Adds edges from STRING PPI database to a PPI Graph

    :param G: Graph to edges to (populated with protein_id nodes)
    :type G: nx.Graph
    :param kwargs:  Additional parameters to pass to STRING API calls
    :return: PPI Graph with STRING interactions added as edges
    :rtype: nx.Graph
    """
    G.graph["sources"].append("string")
    G.graph["string_df"] = STRING_df(
        G.graph["protein_list"],
        ncbi_taxon_id=G.graph["ncbi_taxon_id"],
        kwargs=kwargs,
    )
    add_interacting_proteins(G, df=G.graph["string_df"], kind="string")

    return G


def add_biogrid_edges(G: nx.Graph, **kwargs) -> nx.Graph:
    """
    Adds edges from the BIOGRID database to PPI Graph

    :param G: Graph to edges to (populated with protein_id nodes)
    :type G: nx.Graph
    :param kwargs:  Additional parameters to pass to BIOGRID API calls
    :return: nx.Graph PPIGraph with BIOGRID interactions added as edges
    :rtype: nx.Graph
    """
    G.graph["sources"].append("biogrid")
    G.graph["biogrid_df"] = BIOGRID_df(
        G.graph["protein_list"],
        ncbi_taxon_id=G.graph["ncbi_taxon_id"],
        kwargs=kwargs,
    )
    add_interacting_proteins(G, df=G.graph["biogrid_df"], kind="biogrid")

    return G


def add_interacting_proteins(
    G: nx.Graph, df: pd.DataFrame, kind: str
) -> nx.Graph:
    """
    Generic function for adding interaction edges to PPIGraph

    :param G: PPI Graph to populate with edges
    :type G: nx.Graph
    :param df: Dataframe containing edgelist
    :type df: pd.DataFrame
    :param kind: name of interaction type
    :type kind: str
    :returns: PPI Graph with pre-computed edges added
    :rtype: nx.Graph
    """

    protein_1 = df["p1"].values
    protein_2 = df["p2"].values

    interacting_proteins = set(list(zip(protein_1, protein_2)))

    for p1, p2 in interacting_proteins:
        if G.has_edge(p1, p2):
            G.edges[p1, p2]["kind"].add(kind)
        else:
            G.add_edge(p1, p2, kind={kind})
    log.debug(f"Added {len(df)} {kind} interaction edges")

    return G
