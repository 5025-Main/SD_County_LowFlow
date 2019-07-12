# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 18:27:57 2019

@author: alex.messina
"""


def hover_points(line,display_text, fig, ax):
    annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)
    def update_annot(ind):
        x,y = line[0].get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), " ".join([display_text[n].strftime('%m/%d/%y %H:%M') for n in ind["ind"]]))
        #print text
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)
    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = line[0].contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()
            
    
    fig.canvas.mpl_connect("motion_notify_event", hover)
    
    plt.show()
    return