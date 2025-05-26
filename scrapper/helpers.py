from bs4 import NavigableString
from constants import *

def traverseTree(node, data):
  if(isinstance(node, NavigableString)):
     content = f"{node}".strip().strip(":")
     if content:
      data.append(content)
     return
  for child in node.children:
    traverseTree(child, data)

def listToJSON(lst, result_dict):
  for key in COMPANY_FIELDS:
    if key in lst:
      result_dict[key].append(lst[lst.index(key)+1])
    else:
      result_dict[key].append("")
