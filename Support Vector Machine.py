# Import necessary dependencies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import model_evaluation_utils as meu
from sklearn.model_selection import train_test_split
from collections import Counter
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder

get_ipython().run_line_magic('matplotlib', 'inline')

# Load and merge datasets # white = control; red = stroke; wine = data
stroke_data = pd.read_csv('Stroke/Injure participants.csv', delim_whitespace=False)
control_data = pd.read_csv('Healthy Control participants.csv', delim_whitespace=False)

# Data type as an attribute
stroke_data['data_type'] = 'stroke'   
control_data['data_type'] = 'control'

# merge control and stroke data
datas = pd.concat([stroke_data, control_data])
datas = datas.sample(frac=1, random_state=42).reset_index(drop=True)

# understand dataset features and values
datas.head()
#stroke_data.head()
#control_data.head()


# Prepare Training and Testing Datasets
stp_features = datas.iloc[:,:-1]
stp_feature_names = stp_features.columns
stp_class_labels = np.array(datas['data_type'])

stp_train_X, stp_test_X, stp_train_y, stp_test_y = train_test_split(stp_features, stp_class_labels, 
                                                                    test_size=0.3, random_state=42)

print(Counter(stp_train_y), Counter(stp_test_y))
print('Features:', list(stp_feature_names))


# Feature Scaling
# Define the scaler 
stp_ss = StandardScaler().fit(stp_train_X)
#stp_ss = stp_train_X

# Scale the train set
stp_train_SX = stp_ss.transform(stp_train_X)
#stp_train_SX = stp_train_X

# Scale the test set
stp_test_SX = stp_ss.transform(stp_test_X)
#stp_test_SX = stp_test_X

# Encode Response class labels
le = LabelEncoder()
le.fit(stp_train_y)
# encode wine type labels
stp_train_ey = le.transform(stp_train_y)
stp_test_ey = le.transform(stp_test_y)

## SVM Classifier
from sklearn.svm import SVC
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from matplotlib import pyplot

stp_svm = SVC(random_state=42, probability=True)
stp_svm.fit(stp_train_SX, stp_train_y)

y_pred_svm = stp_svm.predict(stp_test_SX)
y_pred_prob_svm = stp_svm.predict_proba(stp_test_SX)[:,1]

fpr_svm, tpr_svm, thresholds_svm = roc_curve(stp_test_ey, y_pred_prob_svm)

# AUC value can also be calculated like this.
auc_svm = auc(fpr_svm, tpr_svm)
#print(auc_lr)

plt.figure(1)
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.plot([0, 1], [0, 1], 'k--')
plt.plot(fpr_svm, tpr_svm, label='SVM (area = {:.2f})'.format(auc_svm))
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('SVM ROC Curve')
plt.legend(loc='best')
plt.show()

# calculate precision and recall for each threshold
svm_precision, svm_recall, _ = precision_recall_curve(stp_test_ey, y_pred_prob_svm)
#print(lr_precision)
# calculate scores
#lr_f1, lr_auc = f1_score(wtp_test_ey, y_pred_prob_lr), auc(lr_recall, lr_precision)
plt.figure(2)
pyplot.plot(svm_recall, svm_precision, marker='.', label='svm')
# summarize scores
#print('Logistic: f1=%.3f auc=%.3f' % (lr_f1, lr_auc))
# axis labels
pyplot.title('SVM Precision-Recall Curve')
pyplot.xlabel('Recall')
pyplot.ylabel('Precision')
# show the legend
pyplot.legend()
# show the plot
pyplot.show()


# In[ ]:


# Model Interpretation
# View Feature importances
from skater.core.explanations import Interpretation
from skater.model import InMemoryModel

stp_interpreter = Interpretation(stp_test_SX, feature_names=stp_features.columns)
stp_im_model = InMemoryModel(stp_svm.predict_proba, examples=stp_train_SX, target_names=stp_svm.classes_)
plots = stp_interpreter.feature_importance.plot_feature_importance(stp_im_model, ascending=False)
plt.xlabel('Relative Importance Score')
plt.ylabel('Feature')
plt.title('Feature Importances for SVM')
fig = plt.figure(1)
#fig.savefig('LR Feature Importance.png', bbox_inches='tight')
