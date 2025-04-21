import torch
import torch.nn.functional as F
import requests
from collections import defaultdict
from .citationFraudDetector import CitationFraudDetector

class CitationGraphEvaluator:
  def __init__(self, model_path):
    self.model_path = model_path
    self.model = CitationFraudDetector(in_channels=3, hidden_channels=128)
    self.model.load_state_dict(torch.load(model_path))
    self.model.eval()

  # Compute the features of the graph used to predict fraud
  def __compute_author_context_features(self, metadata, edge_index, seed_index: int = 0):
    author_stats = defaultdict(lambda: {'papers': 0, 'citations': 0, 'self_cites': 0})

    # Tally paper counts per author
    for i, meta in enumerate(metadata):
      for a in meta['authors']:
        author_stats[a]['papers'] += 1

    # Tally citations and self-citations
    for src, dst in edge_index.t().tolist():
      citing_authors = set(metadata[src]['authors'])
      cited_authors = set(metadata[dst]['authors'])
      for a in cited_authors:
        author_stats[a]['citations'] += 1
      if citing_authors & cited_authors:
        for a in citing_authors & cited_authors:
          author_stats[a]['self_cites'] += 1

    # Compute context features for seed paper's authors
    seed_authors = set(metadata[seed_index]['authors'])

    new_x = []
    for meta in metadata:
      if seed_authors:
        num_citations = sum(author_stats[a]['citations'] for a in seed_authors) / len(seed_authors)
        num_papers = sum(author_stats[a]['papers'] for a in seed_authors) / len(seed_authors)
        num_selfcites = sum(author_stats[a]['self_cites'] for a in seed_authors) / len(seed_authors)
        selfcite_ratio = num_selfcites / num_citations if num_citations > 0 else 0.0
      else:
        num_citations = num_papers = selfcite_ratio = 0.0
      new_x.append(torch.tensor([num_citations, num_papers, selfcite_ratio], dtype=torch.float))

    x = torch.stack(new_x)

    return {
      'edge_index': edge_index,
      'x': x,
      'metadata': metadata
    }

  # get data on several papers at once from Semantic Scholar API
  def __fetch_paper_data(self, paper_ids):
    url = f"https://api.semanticscholar.org/graph/v1/paper/batch"
    response = requests.post(url, params={'fields': 'authors,title,references.paperId'}, json={"ids": paper_ids})
    if response.status_code == 200:
      return response.json()
    else:
      print(f"Failed to fetch data for {paper_ids}")
      return None

  # update necessary lists and dicts used while creating the graph for each paper
  def __create_node(self, current_id, depth, cited_by_id, current_title, authors, references, queue, node_map, edge_index, papers):
    node_idx = len(node_map)
    node_map[current_id] = node_idx
    if(cited_by_id):
      # add edge from paper that cites this paper
      edge_index.append([node_map[cited_by_id], node_map[current_id]])

    papers.append({
      'title': current_title,
      'authors': authors
    })

    for reference in references:
      cited_id = reference
      if cited_id:
        queue.append((cited_id, depth + 1, current_id))

    return queue, node_map, edge_index, papers

  # create a citation graph around the paper based on its references
  # paperDetails: {
  #    title: "...", 
  #    authors: ["...", "...", ...],
  #    references: [paperId, paperId, paperId, ...] (can be in various formats, such as ARXIV, DOI, etc.)
  # }
  def __create_subgraph(self, paperDetails, k=2):
    visited = {}
    node_map = {}
    papers = []
    edge_index = []
    queue = []

    queue, node_map, edge_index, papers = \
      self.__create_node("", 0, None, paperDetails['title'], paperDetails['authors'], \
                            paperDetails['references'], queue, node_map, edge_index, papers)

    while queue:
      current_id, depth, cited_by_id = queue.pop(0)
      print(depth, cited_by_id)
      if depth > k:
        continue
      if current_id in node_map and cited_by_id:
        edge_index.append([node_map[cited_by_id], node_map[current_id]])
        continue

      current_ids = [current_id]
      print("    ", current_ids[-1])
      while(queue and queue[0][2] == cited_by_id):
        current_ids.append(queue.pop(0)[0])
        print("    ", current_ids[-1])
      if current_ids:
        data = self.__fetch_paper_data(current_ids)

      if not data:
        print(f"Failed to fetch data for references of {cited_by_id}")
        continue

      for id, d in zip(current_ids, data):
        if not d:
          continue
          
        visited[d.get('title','Unknown')] = id

        title = d.get('title', '')
        authors = [a['name'] for a in d.get('authors', [])]
        references = [r['paperId'] for r in d.get('references', [])]

        queue, node_map, edge_index, papers = \
          self.__create_node(id, depth, cited_by_id, title, authors, \
                                references, queue, node_map, edge_index, papers)

    if len(papers) == 0 or len(edge_index) == 0:
      return None

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()

    return self.__compute_author_context_features(papers, edge_index)

  # Produce a percentage score of how likely a graph is to have committed citation fraud
  def evaluateGraph(self, paperDetails):

    graph_data = self.__create_subgraph(paperDetails, k=2)
    if not graph_data:
      return None
    self.model.eval()
    output = self.model(graph_data['x'], graph_data['edge_index'], torch.zeros(graph_data['x'].shape[0], dtype=torch.long))
    prob = F.softmax(output, dim=1)
    return prob[0][1].item()
