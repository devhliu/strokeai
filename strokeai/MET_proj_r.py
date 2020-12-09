
import os

import six

import radiomics
from radiomics import featureextractor, getFeatureClasses

import pandas as pd

proj_root = 'E:\\DicomDB\\MET_Proj'

# Get the location of the example settings file
paramsFile = os.path.join(proj_root, 'radiomics_params.yaml')

# Initialize feature extractor using the settings file
extractor = featureextractor.RadiomicsFeatureExtractor(paramsFile)
featureClasses = getFeatureClasses()

print("Active features:")
for cls, features in six.iteritems(extractor.enabledFeatures):
  if features is None or len(features) == 0:
    features = [f for f, deprecated in six.iteritems(featureClasses[cls].getFeatureNames()) if not deprecated]
  #for f in features:
  #  print(f)
  #  print(getattr(featureClasses[cls], 'get%sFeatureValue' % f).__doc__)

print("Calculating features")
pd_data = pd.read_csv(os.path.join(proj_root, 'radiomics.csv'))
IDs = pd_data['ID'].values
imageNames = pd_data['Image'].values
maskNames = pd_data['Mask'].values
Types = pd_data['Type'].values

results_vectors = []
for ID, imagename, maskname, typei in zip(IDs, imageNames, maskNames, Types):
    featureVector = extractor.execute(imagename, maskname)
    featureVector['ID'] = ID
    featureVector['Type'] = typei
    results_vectors.append(featureVector)
    print(ID, typei)


df = pd.DataFrame(results_vectors)
df.to_csv(os.path.join(proj_root, 'radiomics_output_v3.csv'))