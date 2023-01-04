from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import sys
import logging
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import fasttext

UPLOAD_FOLDER = '/static'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config['SECRET_KEY'] = '03c1f8ffe621d3e1563b76149ee33be51f98d6a8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

Points = pd.DataFrame([[0.7138961838770008, 0.14893617021276595,1],[0.5, 0, 0], [0.5,0.1, 0], [0.9, 0.9, 1] ,[0.9, 0.8, 1] , [0.9, 0.7, 1] ,[0.9, 0.6, 1], [0.9, 0.6, 1], [0.9, 0.6, 1], [0.8, 0.2, 1], [0.77, 0.3, 1], [0.5, 0.3, 0], [0.5,0.5, 0] ,[0.9, 0.5, 1] ,[0.9, 0.4, 1] ,[0.9, 0.3, 1] ,[0.9, 0.2, 1] ,[0.9, 0.1, 1], [0.8,0.2,1], [0.5076221384355012, 0.20833333333333334,0],[0.8861234069792462, 0.5806451612903226, 1], [0.7138961838770008,0.14893617021276595,1], [0.3040782960694573, 0.05714285714285714,0], [0.5534406393069357, 0.058823529411764705,0], [0.4659682365978739, 0.10416666666666667,0],[0.7221689226393052, 0.14285714285714285,0], [0.6777546323428283, 0.09375,0], [0.5076221384355012, 0.20833333333333334,0], [0.5203455480897098, 0.07894736842105263,0], [0.4821866413726838, 0.07692307692307693,0],[0.5602015605575558, 0.07407407407407407,0], [0.5054318342903031, 0.09375,0], [0.24251222782108417, 0.043478260869565216,0], [0.4769929492979544, 0.034482758620689655,0], [0.427614671241901, 0.08571428571428572,0], [0.4494006954537489, 0.038461538461538464,0], [0.9696565649389465, 0.7096774193548387,1], [0.8045103976170994, 0.22857142857142856,1], [0.824097147508412, 0.1951219512195122,1], [0.9078176337864982, 0.3170731707317073,1], [0.8794301215736592, 0.47058823529411764,1], [0.8774619952601843, 0.5294117647058824,1], [0.999999999, 1.0,1], [0.8987352268300897, 0.4594594594594595,1], [0.8530408187607739, 0.4782608695652174,1], [0.7741487164635636, 0.4482758620689655,1], [0.9081173483394802, 0.5454545454545454,1]], columns=['Cosine Similarity', 'Jaccard Similarity', 'Plagiarism'])
Points.to_csv('plagiarism.csv')
df = pd.read_csv('plagiarism.csv')
feature_cols = ["Cosine Similarity", "Jaccard Similarity"]
X = df[feature_cols]
y = df.Plagiarism
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.10, random_state=0)
logreg = LogisticRegression()
logreg.fit(X_train,y_train)

from serv import routes
