# A.L.I.C.E.
home automation A.I. project

History
=======
# 21 Nov 2017
- Created git project
- Update readme
- Add initial project description document (project_proposal.doc)

# 24 Nov 2017
- Created Vocabulary Handler class
- Created inpu commands corpus
- Updated readme

# 29 Nov 2017
- Enhanced Vocabulary Handler class
- Added training corpus encoding
- Expanded training corpus
- Updated readme

# 7 Dec 2017
- Added hardware topology visio drawing

# 10 Ian 2018
- Added software topology visio drawing
- Finished first draft of the project proposal documentation

# 7 Oct 2018
- Added initial tensorflow application test
- Created a tensorflow movie review sentiment analyzer

# 11 Oct 2018
- First run of digit classifier nn using tensorflow, on mnist dataset

# 21 Oct 2018
- added script for sentiment featureset creation and a nn to use them.
Also, the accuracy result was horrible

# 22 Oct 2018
- added OneHotEncoder class for training data and lexicon persistent generation
- added encode_sentence(sentence) method to be able to encode any arbitrary sentence

# 29 Oct 2018
- added first tensorflow neural network to actually work on the smart home training corpus

*NOTE: Seems very unlikely, but the loss converged to 0.0 (100% accuracy) in under 30 epochs*

# 5 Nov 2018
- added a second FFNN version using tensorflow
- added session saving and storing example

# 10 Nov 2018
- isolated all file specific operation into their own class (FileHandler)
- updated the OneHotEncoder startup flow
- extended the training corpus a little bit

# 11 Nov 2018
- separated neural network into its own class
- hooked up end to end dataflow from sentence input to classification output
- first running version of the FFNN classifier using one hot encoding
- removed old / unused files

# 19 Nov 2018
- added MQTT controller

# 20 Nov 2018
- added Zwave controller

# 24 Nov 2018
- implemented Zwave network handling

# 25 Nov 2018
- fully connected components

# 30 Nov 2018
- integrated the thermostat

# 2 Dec 2018
- extended Node-RED and MQTT handling
