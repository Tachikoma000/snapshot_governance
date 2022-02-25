from datetime import datetime

import dash
from dash import html

from subgrounds.dash_wrappers import Graph
from subgrounds.plotly_wrappers import Figure, Scatter, Indicator
from subgrounds.schema import TypeRef
from subgrounds.subgraph import SyntheticField, FieldPath
from subgrounds.subgrounds import Subgrounds


sg = Subgrounds()
olympusDAO = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/drondin/olympus-protocol-metrics')

def immediate(sg: Subgrounds, fpath: FieldPath):
  data = sg.execute(sg.mk_request([fpath]))
  return fpath.extract_data(data)[0]

# Define useful synthetic fields
olympusDAO.ProtocolMetric.datetime = SyntheticField(
  lambda timestamp: str(datetime.fromtimestamp(timestamp)),
  SyntheticField.STRING,
  olympusDAO.ProtocolMetric.timestamp,
)

# olympusDAO.ProtocolMetric.staked_supply_percent = 100 * olympusDAO.ProtocolMetric.sOhmCirculatingSupply / olympusDAO.ProtocolMetric.totalSupply
olympusDAO.ProtocolMetric.staked_supply_percent = SyntheticField(
  lambda sohm_supply, total_supply: 100 * sohm_supply / total_supply,
  SyntheticField.FLOAT,
  [
    olympusDAO.ProtocolMetric.sOhmCirculatingSupply,
    olympusDAO.ProtocolMetric.totalSupply
  ],
  default=100.0
)

olympusDAO.ProtocolMetric.unstaked_supply_percent = 100 - olympusDAO.ProtocolMetric.staked_supply_percent

# Treasury RFV per OHM and ratio
olympusDAO.ProtocolMetric.rfv_per_ohm = SyntheticField(
  lambda treasury_rfv, total_supply: treasury_rfv / total_supply if treasury_rfv / total_supply > 1 else 0,
  SyntheticField.FLOAT,
  [
    olympusDAO.ProtocolMetric.treasuryRiskFreeValue,
    olympusDAO.ProtocolMetric.totalSupply
  ]
)

olympusDAO.ProtocolMetric.price_rfv_ratio = 100 * olympusDAO.ProtocolMetric.ohmPrice / olympusDAO.ProtocolMetric.rfv_per_ohm

# Treasury market value per OHM and ratio
olympusDAO.ProtocolMetric.tmv_per_ohm = olympusDAO.ProtocolMetric.treasuryMarketValue / olympusDAO.ProtocolMetric.totalSupply
olympusDAO.ProtocolMetric.price_tmv_ratio = 100 * olympusDAO.ProtocolMetric.ohmPrice / olympusDAO.ProtocolMetric.tmv_per_ohm

protocol_metrics_1year = olympusDAO.Query.protocolMetrics(
  orderBy=olympusDAO.ProtocolMetric.timestamp,
  orderDirection='desc',
  first=365
)

last_metric = olympusDAO.Query.protocolMetrics(
  orderBy=olympusDAO.ProtocolMetric.timestamp,
  orderDirection='desc',
  first=1
)

# ================================================================
# Snapshot data
# ================================================================

snapshot = sg.load_subgraph('https://hub.snapshot.org/graphql')

snapshot.Proposal.datetime = SyntheticField(
  lambda timestamp: str(datetime.fromtimestamp(timestamp)),
  SyntheticField.STRING,
  snapshot.Proposal.end,
)

def fmt_summary(title, choices, scores):
  total_vote = sum(scores)
  vote_string = '<br>'.join(f'{choice}: {100*score/total_vote:.2f}%' for choice, score in zip(choices, scores))
  return f'{title}<br>{vote_string}'

snapshot.Proposal.summary = SyntheticField(
  fmt_summary,
  SyntheticField.STRING,
  [
    snapshot.Proposal.title,
    snapshot.Proposal.choices,
    snapshot.Proposal.scores
  ],
)

proposals = snapshot.Query.proposals(
  orderBy='created',
  orderDirection='desc',
  first=100,
  where=[
    snapshot.Proposal.space == 'olympusdao.eth',
    snapshot.Proposal.state == 'closed',
  ]
)
