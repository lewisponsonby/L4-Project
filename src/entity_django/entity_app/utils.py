import uuid, base64
from .models import *
from io import BytesIO
from matplotlib import pyplot as plt
import matplotlib
from collections import Counter
import numpy as np

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img = buffer.getvalue()
    graph = base64.b64encode(img)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_chart(docid):
    instances = Instance.objects.filter(documentID=docid)
    entities=[]
    for instance in instances:
        entities.append(str(instance.entityID).split(" ")[2].replace('http://dbpedia.org/resource/','').replace('(','').replace(')','').replace('_','\n'))
    counter=dict(Counter(entities).most_common(5))
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(5,4))
    plt.bar(counter.keys(),counter.values(), color=['#442288', '#FED23F', '#EB7D5B', '#6CA2EA','#B5D33D'])
    plt.xticks(rotation=45)
    plt.title('Most Common Entities')
    plt.ylabel('Frequency')
    plt.tight_layout()
    chart = get_graph()
    return chart
