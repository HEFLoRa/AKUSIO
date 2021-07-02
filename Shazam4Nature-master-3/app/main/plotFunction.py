import matplotlib
import matplotlib.pyplot as plt
import datetime
import os
from flask import current_app

# Use AGG for better support on html
matplotlib.use('AGG')

def calcPlot(birdsData):
    # creating the label for x
    xlab = []
    xstart = datetime.datetime.utcnow().hour - 23

    for i in range(24):
        xlab.append(str((xstart + i) % 24))

    # creating y with values @ correct time
    y = [None] * 24

    for i in range(24):
        y[int(i)] = round(birdsData["per_hour"][xlab[i]])

    # creating plot
    plt.figure()
    plt.bar(range(24), y)
    plt.xlabel('Detection time')
    plt.ylabel('Amount')
    plt.title('Detected ' + birdsData["name"] + ' in the last 24 hours.')
    plt.xticks(range(24), xlab)
    plt.savefig(os.path.join(current_app.root_path, "static", "birds", "{}_plot.png".format(birdsData["file"])))
