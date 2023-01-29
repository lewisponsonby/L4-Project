import uuid, base64
from .models import *
from io import BytesIO
from matplotlib import pyplot as plt
import matplotlib
from collections import Counter
import numpy as np
from matplotlib import pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import matplotlib.colors as mcolors

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img = buffer.getvalue()
    graph = base64.b64encode(img)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_wordcloud(topics):
    cols = [color for name, color in list(mcolors.CSS4_COLORS.items())[22:38]]

    cloud = WordCloud(background_color='white',
                      width=2500,
                      height=2500,
                      max_words=20,
                      colormap='tab10',
                      color_func=lambda *args, **kwargs: cols[i],
                      prefer_horizontal=1.0)

    fig, axes = plt.subplots(4, 2, figsize=(12, 12), sharex=True, sharey=True)

    for i, ax in enumerate(axes.flatten()):
        fig.add_subplot(ax)
        topic_words = dict(topics[i][1])
        cloud.generate_from_frequencies(topic_words, max_font_size=300)
        plt.gca().imshow(cloud)
        plt.gca().set_title('Topic ' + str(i+1), fontdict=dict(size=16))
        plt.gca().axis('off')

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.axis('off')
    plt.margins(x=0, y=0)
    plt.tight_layout()
    chart = get_graph()
    return chart



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
    plt.title('Most Frequent Entities')
    plt.ylabel('Frequency')
    plt.tight_layout()
    chart = get_graph()
    return chart
