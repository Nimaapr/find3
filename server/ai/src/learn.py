#!/usr/bin/python3

# Logging: The script starts by setting up a logger named "learn" which writes log messages to both a file named 'learn.log' and to the console. This will be used throughout the script to log important information and errors.
# Decorators: It then defines a decorator timeout which wraps a function in such a way that if the function does not complete within a specified time (in seconds), it raises an exception.

# AI class: Then it defines a class AI. This class appears to be an artificial intelligence model manager with several methods:
# __init__: Initializes the AI object with basic properties and a logger.
# classify: Classifies given sensor data using different algorithms stored in the AI object and returns a payload with the predictions of each algorithm.
# do_classification: Helper function to classify a reshaped sensor data using a specific algorithm. The results are stored in a class variable.
# train: Uses a classifier to train a model on given data. This method is decorated with the timeout decorator.
# learn: Loads data from a CSV file, prepares the data, then trains several different models on that data.
# save and load: Save and load the AI's state (header, naming, algorithms, and family) to/from a gzipped file.

# Cluster Analysis: The do function which loads an AI instance and then applies various clustering algorithms to its data. It also captures warnings to prevent them from being printed to the console. It then checks the results of the clustering algorithms by comparing the predicted groups (clusters) to known groups.





import json
import csv
from random import shuffle
import warnings
import pickle
import gzip
import operator
import time
import logging
import math
from threading import Thread
import functools
import multiprocessing
import pandas as pd



logger = logging.getLogger('learn')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('learn.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - [%(name)s/%(funcName)s] - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

import numpy
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn import cluster, mixture
from sklearn.neighbors import kneighbors_graph
from naive_bayes import ExtendedNaiveBayes
from naive_bayes2 import ExtendedNaiveBayes2
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics import confusion_matrix


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (
                func.__name__, timeout))]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco


class AI(object):

    def __init__(self, family, path_to_data):
        self.logger = logging.getLogger('learn.AI')
        self.naming = {'from': {}, 'to': {}}
        self.family = family
        self.path_to_data = path_to_data

    def classify(self, sensor_data):
        header = self.header[1:]
        is_unknown = True
        # self.logger.debug(f"sensor data in classify: {sensor_data}")
        # self.logger.debug(f"header in classify: {self.header}")
        csv_data = numpy.zeros(len(header))
        for sensorType in sensor_data['s']:
            for sensor in sensor_data['s'][sensorType]:
                sensorName = sensorType + "-" + sensor
                if sensorName in header:
                    is_unknown = False
                    csv_data[header.index(sensorName)] = sensor_data[
                        's'][sensorType][sensor]
        self.headerClassify = header
        self.csv_dataClassify = csv_data.reshape(1, -1)
        payload = {'location_names': self.naming['to'], 'predictions': []}

        threads = [None]*len(self.algorithms)
        self.results = [None]*len(self.algorithms)

        for i, alg in enumerate(self.algorithms.keys()):
            threads[i] = Thread(target=self.do_classification, args=(i, alg))
            threads[i].start()

        for i, _ in enumerate(self.algorithms.keys()):
            threads[i].join()

        for result in self.results:
            if result != None:
                payload['predictions'].append(result)
        payload['is_unknown'] = is_unknown
        return payload

    def do_classification(self, index, name):
        """
        header = ['wifi-a', 'wifi-b']
        csv_data = [-67 0]
        """
        if name == 'Gaussian Process':
            return

        t = time.time()
        try:
            prediction = self.algorithms[
                name].predict_proba(self.csv_dataClassify)
        except Exception as e:
            logger.error(self.csv_dataClassify)
            logger.error(str(e))
            return
        predict = {}
        for i, pred in enumerate(prediction[0]):
            predict[i] = pred
        predict_payload = {'name': name,
                           'locations': [], 'probabilities': []}
        badValue = False
        for tup in sorted(predict.items(), key=operator.itemgetter(1), reverse=True):
            predict_payload['locations'].append(str(tup[0]))
            predict_payload['probabilities'].append(
                round(float(tup[1]), 2))
            if math.isnan(tup[1]):
                badValue = True
                break
        if badValue:
            return

        self.results[index] = predict_payload

    def fill_missing_with_window(self, df, window_size=15):
        """
        This function fills missing RSSI values in a DataFrame using a sliding window approach.

        Parameters:
            df (pd.DataFrame): The DataFrame containing the RSSI readings.
            window_size (int): The size of the sliding window.

        Returns:
            pd.DataFrame: The DataFrame with missing RSSI values filled.
        """
        # The RSSI column names
        rssi_columns = [col for col in df.columns if col.startswith("bluetooth-")]

        # Group by location
        grouped = df.groupby("location")

        # Create an empty list to store the processed groups
        df_list = []

        # For each group
        for name, group in grouped:
            # For each RSSI column
            for rssi_col in rssi_columns:
                try:
                    # Replace empty strings with NaN
                    group[rssi_col] = group[rssi_col].replace(0.0, numpy.nan)
                    # Fill missing values using a forward and backward rolling window
                    group[rssi_col] = group[rssi_col].fillna(group[rssi_col].rolling(window_size, min_periods=1).mean())
                    group[rssi_col] = group[rssi_col].fillna(group[rssi_col].rolling(window_size, min_periods=1).mean()[::-1])
                    # If the above line doesn't fill all NaN values, repeat the process again
                    group[rssi_col] = group[rssi_col].fillna(group[rssi_col].rolling(window_size, min_periods=1).mean())
                    # Replace any remaining NaNs back to 0.0
                    group[rssi_col] = group[rssi_col].replace(numpy.nan, 0)
                except Exception as e:
                    self.logger.debug(f"Error: {e}")

            # Add the processed group to the list
            df_list.append(group)

        # Concatenate the groups back into a single DataFrame
        try:
            df_filled = pd.concat(df_list)
            # self.logger.debug(f"new df: {df_filled}")
        except Exception as e:
            self.logger.debug(f"Error in concat: {e}")

        return df_filled

    @timeout(100)
    def train(self, clf, x, y):
        return clf.fit(x, y)

    def learn(self, fname):
        t = time.time()
        # self.logger.debug(f"csv folder: {fname}")
        # load CSV file
        self.header = []
        rows = []
        naming_num = 0
        with open(fname, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for i, row in enumerate(reader):
                self.logger.debug(row)
                if i == 0:
                    self.header = row
                else:
                    for j, val in enumerate(row):
                        if j == 0:
                            # this is a name of the location
                            if val not in self.naming['from']:
                                self.naming['from'][val] = naming_num
                                self.naming['to'][naming_num] = val
                                naming_num += 1
                            row[j] = self.naming['from'][val]
                            continue
                        if val == '':
                            row[j] = 0
                            continue
                        try:
                            row[j] = float(val)
                        except:
                            self.logger.error(
                                "problem parsing value " + str(val))
                    # self.logger.debug(f"type of row[0] before appending: {type(row[0])}")
                    rows.append(row)


        # Convert rows into a DataFrame
        df = pd.DataFrame(rows, columns=self.header)

        # Fill missing values using the sliding window approach
        df = self.fill_missing_with_window(df)
        # Convert the 'location' column back to integer
        df['location'] = df['location'].astype(int)

        # Convert the DataFrame back into rows
        rows = df.values.tolist()
        # Iterate over the rows
        for i, row in enumerate(rows):
            # Iterate over the items in each row
            for j, item in enumerate(row):
                # If the item is 0.0, change it to 0
                if item == 0.0:
                    rows[i][j] = 0

        # first column in row is the classification, Y
        y = numpy.zeros(len(rows))
        x = numpy.zeros((len(rows), len(rows[0]) - 1))

        # shuffle it up for training
        record_range = list(range(len(rows)))
        shuffle(record_range)
        for i in record_range:
            y[i] = rows[i][0]
            x[i, :] = numpy.array(rows[i][1:])

        names = [
            "Nearest Neighbors",
            "Linear SVM",
            "RBF SVM",
            # "Gaussian Process",
            "Decision Tree",
            "Random Forest",
            "Neural Net",
            "AdaBoost",
            "Naive Bayes",
            "QDA",
            "Gradient Boosting"]
        classifiers = [
            KNeighborsClassifier(3),
            SVC(kernel="linear", C=0.025, probability=True),
            SVC(gamma=2, C=1, probability=True),
            # GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True),
            DecisionTreeClassifier(max_depth=5),
            RandomForestClassifier(
                max_depth=5, n_estimators=10, max_features=1),
            MLPClassifier(alpha=1, early_stopping=True),
            AdaBoostClassifier(),
            GaussianNB(),
            QuadraticDiscriminantAnalysis(),
            GradientBoostingClassifier()]
        self.algorithms = {}

        hyperparameters = {
            "Nearest Neighbors": {
                'n_neighbors': [3, 5, 7, 9],
                'weights': ['uniform', 'distance'],
                'metric': ['euclidean', 'manhattan']
            },
            "Linear SVM": {
                'C': [0.001, 0.01, 0.1, 1, 10],
                'kernel': ['linear', 'rbf'],
                'gamma': [0.1, 1, 10, 100]
            },
            "RBF SVM": {
                'C': [0.001, 0.01, 0.1, 1, 10],
                'gamma': [0.1, 1, 10, 100]
            },
            "Decision Tree": {
                'max_depth': [None, 5, 10, 15, 20],
                'min_samples_split': [2, 5, 10]
            },
            "Random Forest": {
                'n_estimators': [10, 50, 100, 200],
                'max_depth': [None, 5, 10, 15, 20],
                'min_samples_split': [2, 5, 10]
            },
            "Neural Net": {
                'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)],
                'activation': ['tanh', 'relu'],
                'solver': ['sgd', 'adam'],
                'alpha': [0.0001, 0.001, 0.05],
                'learning_rate': ['constant','adaptive'],
            },
            "AdaBoost": {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.05, 0.1, 0.5, 1]
            },
            "Naive Bayes": {},  # GaussianNB doesn't really have hyperparameters to tune
            "QDA": {
                'reg_param': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
            },
            "Gradient Boosting":{
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.1, 1.0],
                'subsample' : [0.5, 0.7, 1.0],
                'max_depth': [3, 7, 9],
            }
        }

        # split_for_learning = int(0.70 * len(y))
        for name, clf in zip(names, classifiers):
            t2 = time.time()
            self.logger.debug("learning {}".format(name))
            try:
                # perform grid search with cross-validation
                grid_search = RandomizedSearchCV(
                    clf, 
                    hyperparameters[name], 
                    cv=StratifiedKFold(n_splits=5),  # 5-fold stratified cross-validation
                    verbose=0, 
                    n_jobs=-1  # use all processors
                )
                self.algorithms[name] = self.train(grid_search, x, y)
                score = self.algorithms[name].score(x,y)
                # self.logger.debug(name, score)
                self.logger.debug("name {}: score {}".format(name, str(score)))
                # log best parameters found by grid search
                self.logger.debug(
                    "Best parameters for {}: {}".format(
                        name, 
                        self.algorithms[name].best_params_
                    )
                )

                # Log feature importance for tree-based models
                if name in ["Decision Tree", "Random Forest", "Gradient Boosting"]:
                    feature_importances = self.algorithms[name].best_estimator_.feature_importances_
                    self.logger.debug("Feature importances for {}: {}".format(name, feature_importances))

                # Log confusion matrix
                y_pred = self.algorithms[name].predict(x)
                cm = confusion_matrix(y, y_pred)
                self.logger.debug("Confusion matrix for {}: {}".format(name, cm))

                # Log cross-validation results
                cv_results = self.algorithms[name].cv_results_
                self.logger.debug("Cross-validation results for {}: {}".format(name, cv_results))

                self.logger.debug("learned {}, {:d} ms".format(
                    name, int(1000 * (t2 - time.time()))))
            except Exception as e:
                self.logger.error("{} {}".format(name, str(e)))

        self.logger.debug("{:d} ms".format(int(1000 * (t - time.time()))))

    def save(self, save_file):
        t = time.time()
        f = gzip.open(save_file, 'wb')
        pickle.dump(self.header, f)
        pickle.dump(self.naming, f)
        pickle.dump(self.algorithms, f)
        pickle.dump(self.family, f)
        f.close()
        self.logger.debug("{:d} ms".format(int(1000 * (t - time.time()))))

    def load(self, save_file):
        t = time.time()
        f = gzip.open(save_file, 'rb')
        self.header = pickle.load(f)
        self.naming = pickle.load(f)
        self.algorithms = pickle.load(f)
        self.family = pickle.load(f)
        f.close()
        self.logger.debug("{:d} ms".format(int(1000 * (t - time.time()))))


def do():
    ai = AI()
    ai.load()
    # ai.learn()
    params = {'quantile': .3,
              'eps': .3,
              'damping': .9,
              'preference': -200,
              'n_neighbors': 10,
              'n_clusters': 3}
    bandwidth = cluster.estimate_bandwidth(ai.x, quantile=params['quantile'])
    connectivity = kneighbors_graph(
        ai.x, n_neighbors=params['n_neighbors'], include_self=False)
    # make connectivity symmetric
    connectivity = 0.5 * (connectivity + connectivity.T)
    ms = cluster.MeanShift(bandwidth=bandwidth, bin_seeding=True)
    two_means = cluster.MiniBatchKMeans(n_clusters=params['n_clusters'])
    ward = cluster.AgglomerativeClustering(
        n_clusters=params['n_clusters'], linkage='ward',
        connectivity=connectivity)
    spectral = cluster.SpectralClustering(
        n_clusters=params['n_clusters'], eigen_solver='arpack',
        affinity="nearest_neighbors")
    dbscan = cluster.DBSCAN(eps=params['eps'])
    affinity_propagation = cluster.AffinityPropagation(
        damping=params['damping'], preference=params['preference'])
    average_linkage = cluster.AgglomerativeClustering(
        linkage="average", affinity="cityblock",
        n_clusters=params['n_clusters'], connectivity=connectivity)
    birch = cluster.Birch(n_clusters=params['n_clusters'])
    gmm = mixture.GaussianMixture(
        n_components=params['n_clusters'], covariance_type='full')
    clustering_algorithms = (
        ('MiniBatchKMeans', two_means),
        ('AffinityPropagation', affinity_propagation),
        ('MeanShift', ms),
        ('SpectralClustering', spectral),
        ('Ward', ward),
        ('AgglomerativeClustering', average_linkage),
        ('DBSCAN', dbscan),
        ('Birch', birch),
        ('GaussianMixture', gmm)
    )

    for name, algorithm in clustering_algorithms:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="the number of connected components of the " +
                "connectivity matrix is [0-9]{1,2}" +
                " > 1. Completing it to avoid stopping the tree early.",
                category=UserWarning)
            warnings.filterwarnings(
                "ignore",
                message="Graph is not fully connected, spectral embedding" +
                " may not work as expected.",
                category=UserWarning)
            try:
                algorithm.fit(ai.x)
            except:
                continue

        if hasattr(algorithm, 'labels_'):
            y_pred = algorithm.labels_.astype(numpy.int)
        else:
            y_pred = algorithm.predict(ai.x)
        # Compute the Adjusted Rand Index
        ari = adjusted_rand_score(ai.y, y_pred)
        # log the ARI
        self.logger.debug(f"Adjusted Rand Index of {name}: {ari:.2f}")


        if max(y_pred) > 3:
            continue
        known_groups = {}
        for i, group in enumerate(ai.y):
            group = int(group)
            if group not in known_groups:
                known_groups[group] = []
            known_groups[group].append(i)
        guessed_groups = {}
        for i, group in enumerate(y_pred):
            if group not in guessed_groups:
                guessed_groups[group] = []
            guessed_groups[group].append(i)
        for k in known_groups:
            for g in guessed_groups:
                print(
                    k, g, len(set(known_groups[k]).intersection(guessed_groups[g])))

