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
    colors={}
    for instance in instances:
        entity_name=str(instance.entityID).split(" ")[2].replace('http://dbpedia.org/resource/','').replace('(','').replace(')','').replace('_','\n')
        entities.append(entity_name)
        colors[entity_name]=instance.entityID.sensitivity


    counter=dict(Counter(entities).most_common(7))
    color = [colors[key] for key in counter.keys()]
    for i in range(len(color)):
        if color[i]==1:
            color[i]='#04BD00'

        if color[i]==2:
            color[i]='#FFC517'

        if color[i]==3:
            color[i]='#DF0000'
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(5,4))
    plt.bar(counter.keys(),counter.values(), color=color)
    plt.xticks(rotation=45)
    plt.title('Most Common Entities')
    plt.ylabel('Frequency')
    plt.tight_layout()
    chart = get_graph()
    return chart
