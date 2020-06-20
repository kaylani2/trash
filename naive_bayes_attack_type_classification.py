# Author: Kaylani Bochie
# github.com/kaylani2
# kaylani AT gta DOT ufrj DOT br

### K: Model: Naive Bayes
### K: From the article:
## "Finally, for classifying the type of attack, the final sample size was set
## to acquire a sample of 50,000 packets (10,000 packets per attack) from a
## total of 220,785 packets."

import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.io import arff


###############################################################################
## Define constants
###############################################################################
# Random state for reproducibility
STATE = 0
np.random.seed (STATE)
## Hard to not go over 80 columns
IOT_DIRECTORY = '../../../../datasets/cardiff/IoT-Arff-Datasets/'
IOT_ATTACK_TYPE_FILENAME = 'AttackTypeClassification.arff'
FILE_NAME = IOT_DIRECTORY + IOT_ATTACK_TYPE_FILENAME

###############################################################################
## Load dataset
###############################################################################
pd.set_option ('display.max_rows', None)
pd.set_option ('display.max_columns', 5)
data = arff.loadarff (FILE_NAME)
df = pd.DataFrame (data [0])
print ('Dataframe shape (lines, collumns):', df.shape, '\n')
print ('First 5 entries:\n', df [:5], '\n')

### Decode byte strings into ordinary strings:
print ('Decoding byte strings into ordinary strings.')
strings = df.select_dtypes ( [np.object])
strings = strings.stack ().str.decode ('utf-8').unstack ()
for column in strings:
  df [column] = strings [column]
print ('Done.\n')

###############################################################################
## Display generic (dataset independent) information
###############################################################################
print ('Dataframe shape (lines, collumns):', df.shape, '\n')
print ('First 5 entries:\n', df [:5], '\n')
df.info (verbose = False) # Make it true to find individual atribute types
#print (df.describe ()) # Brief statistical description on NUMERICAL atributes

print ('Dataframe contains NaN values:', df.isnull ().values.any ())
nanColumns = [i for i in df.columns if df [i].isnull ().any ()]
print ('Number of NaN columns:', len (nanColumns))
#print ('NaN columns:', nanColumns, '\n')


###############################################################################
## Display specific (dataset dependent) information
###############################################################################
print ('Label types:', df ['class_attack_type'].unique ())
print ('Label distribution:\n', df ['class_attack_type'].value_counts ())


###############################################################################
## Data pre-processing
###############################################################################
df.replace (['NaN', 'NaT'], np.nan, inplace = True)
df.replace ('?', np.nan, inplace = True)
df.replace ('Infinity', np.nan, inplace = True)

###############################################################################
### Remove columns with only one value
print ('\n\nColumn | # of different values')
print (df.nunique ())
print ('Removing attributes that have only one sampled value.')
nUniques = df.nunique ()
for column, nUnique in zip (df.columns, nUniques):
  if (nUnique == 1): # Only one value: DROP.
    df.drop (axis = 'columns', columns = column, inplace = True)

print ('\n\nColumn | # of different values')
print (df.nunique ())

###############################################################################
### Remove NaN columns (with a lot of NaN values)
print ('\n\nColumn | NaN values')
print (df.isnull ().sum ())
### K: 150k samples seems to be a fine cutting point for this dataset
print ('Removing attributes with more than half NaN and inf values.')
df = df.dropna (axis = 'columns', thresh = 150000)
print ('Dataframe contains NaN values:', df.isnull ().values.any ())
print ('\n\nColumn | NaN values (after dropping columns)')
print (df.isnull ().sum ())

### K: NOTE: Not a good idea to drop these samples since it reduces
### K: the number of available MITM samples by a lot.
### K: So this is not a good strategy...
#print ('Label distribution before dropping rows:')
#print (df ['class_attack_type'].value_counts ())
### K: This leaves us with the following attributes to encode:
### Attribute            NaN values
#   ip.hdr_len           7597
#   ip.dsfield.dscp      7597
#   ip.dsfield.ecn       7597
#   ip.len               7597
#   ip.flags             7597
#   ip.frag_offset       7597
#   ip.ttl               7597
#   ip.proto             7597
#   ip.checksum.status   7597
### K: Options: Remove these samples or handle them later.
### K: Removing them for now.
#print ('Removing samples with NaN values (not a lot of these).')
#df = df.dropna (axis = 'rows', thresh = df.shape [1])
#print ('Label distribution after dropping rows:')
#print (df ['class_attack_type'].value_counts ())
#print ('Column | NaN values (after dropping rows)')
#print (df.isnull ().sum ())
#print ('Dataframe contains NaN values:', df.isnull ().values.any ())

###############################################################################
### Input missing values
### K: Look into each attribute to define the best inputing strategy.
columsWithMissingValues = ['ip.hdr_len', 'ip.dsfield.dscp', 'ip.dsfield.ecn',
                           'ip.len', 'ip.flags', 'ip.frag_offset', 'ip.ttl',
                           'ip.proto', 'ip.checksum.status']
nUniques = df.nunique ()
for column, nUnique in zip (df.columns, nUniques):
  if (column in columsWithMissingValues ):
    print (column, df [column].unique ())


"""
###############################################################################
### Handle categorical values
### K: Look into each attribute to define the best encoding strategy.
df.info (verbose = False)
### K: dtypes: float64 (27), int64 (1), object (5)
#print (df.columns.to_series ().groupby (df.dtypes).groups, '\n\n')
print ('Objects:', list (df.select_dtypes ( ['object']).columns), '\n')
### K: Objects: [
# 'ip.flags.df', {0, 1}
# 'ip.flags.mf', {0, 1}
# 'packet_type', {in, out}
# LABELS:
# 'class_device_type',
# 'class_is_malicious' {0, 1}
#]

### K: NOTE: ip.flags.df and ip.flags.mf only have numerical values, but have
### been loaded as objects because (probably) of missing values, so we can
### just convert them instead of treating them as categorical.
print ('\nHandling categorical attributes (label encoding).')
print ('ip.flags.df and ip.flags.mf have been incorrectly read as objects.')
print ('Converting them to numeric.')
df ['ip.flags.df'] = pd.to_numeric (df ['ip.flags.df'])
df ['ip.flags.mf'] = pd.to_numeric (df ['ip.flags.mf'])

from sklearn.preprocessing import LabelEncoder
myLabelEncoder = LabelEncoder ()
df ['packet_type'] = myLabelEncoder.fit_transform (df ['packet_type'])

print ('Objects:', list (df.select_dtypes ( ['object']).columns), '\n')

### onehotencoder ta dando nan na saida, ajeitar isso ai
#from sklearn.preprocessing import OneHotEncoder
#enc = OneHotEncoder (handle_unknown = 'error')
#enc_df = pd.DataFrame (enc.fit_transform (df [ ['packet_type']]).toarray ())
#df = df.join (enc_df)
#df.drop (axis = 'columns', columns = 'packet_type', inplace = True)
#
#### K: NOTE: This transformed the dataframe in a way that the last column is
#### no longer the target. We have to fix that:
#cols_at_end = ['class_attack_type']
#df = df [ [c for c in df if c not in cols_at_end]
#        + [c for c in cols_at_end if c in df]]


###############################################################################
### Drop unused targets
### K: NOTE: class_is_malicious and class_device_type are labels for different
### applications, not attributes. They must not be used to aid classification.
print ('Dropping class_device_type and class_is_malicious.')
print ('These are labels for other scenarios.')
df.drop (axis = 'columns', columns = 'class_device_type', inplace = True)
df.drop (axis = 'columns', columns = 'class_is_malicious', inplace = True)


###############################################################################
## Encode Label
###############################################################################
print ('Enconding label.')
print ('Label types before conversion:', df ['class_attack_type'].unique ())
#df ['class_attack_type'] = df ['class_attack_type'].replace ('N/A', 0)
#df ['class_attack_type'] = df ['class_attack_type'].replace ('DoS', 1)
#df ['class_attack_type'] = df ['class_attack_type'].replace ('iot-toolkit', 2)
#df ['class_attack_type'] = df ['class_attack_type'].replace ('MITM', 3)
#df ['class_attack_type'] = df ['class_attack_type'].replace ('Scanning', 4)
print ('Label types after conversion:', df ['class_attack_type'].unique ())


###############################################################################
## Convert dataframe to a numpy array
###############################################################################
print ('\nConverting dataframe to numpy array.')
X = df.iloc [:, :-1].values
y = df.iloc [:, -1].values


###############################################################################
## Split dataset into train and test sets
###############################################################################
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split (X, y, test_size = 4/10,
                                                     random_state = STATE)
print ('X_train shape:', X_train.shape)
print ('y_train shape:', y_train.shape)
print ('X_test shape:', X_test.shape)
print ('y_test shape:', y_test.shape)


###############################################################################
## Handle imbalanced data (like the original author)
###############################################################################
print ('Handling imbalanced label distribution.')
print ('Label distribution:\n', df ['class_attack_type'].value_counts ())

sys.exit ()
###############################################################################
## Apply normalization
###############################################################################
print ('Applying normalization (standard)')
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler ()
scaler.fit (X_train)
#print ('Mean before scalling:', scaler.mean_)
X_train = scaler.transform (X_train)
scaler.fit (X_train)
#print ('Mean after scalling:', scaler.mean_)

scaler.fit (X_test)
X_test = scaler.transform (X_test)

#### K: One hot encode the output.
#import keras.utils
#from keras.utils import to_categorical
#numberOfClasses = len (df ['class_attack_type'].unique ())
#y_train = keras.utils.to_categorical (y_train, numberOfClasses)
#y_test = keras.utils.to_categorical (y_test, numberOfClasses)


###############################################################################
## Create learning model (Naive Bayes)
###############################################################################
print ('Creating learning model.')
from sklearn.naive_bayes import GaussianNB, CategoricalNB
model = GaussianNB ()
model.fit (X_train, y_train)


sys.exit ()
###############################################################################
## Analyze results
###############################################################################
### K: NOTE: Only look at test results when publishing...
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.metrics import f1_score, classification_report, accuracy_score
from sklearn.metrics import cohen_kappa_score
y_pred = model.predict (X_test)

print ('Confusion matrix:')
print (confusion_matrix (y_test, y_pred,
                         labels = df ['class_attack_type'].unique ()))

print ('Classification report:')
print (classification_report (y_test, y_pred,
                              labels = df ['class_attack_type'].unique (),
                              digits = 3))

print ('\n\n')
print ('Accuracy:', accuracy_score (y_test, y_pred))
print ('Precision:', precision_score (y_test, y_pred, average = 'macro'))
print ('Recall:', recall_score (y_test, y_pred, average = 'macro'))
print ('F1:', f1_score (y_test, y_pred, average = 'macro'))
print ('Cohen Kappa:', cohen_kappa_score (y_test, y_pred,
                       labels = df ['class_attack_type'].unique ()))

sys.exit ()
"""
