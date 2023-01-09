# Pokemon_Sounds
A proposal on a sound-based pokemon classification : is it possible to identify similar "species" like in real life

Idea : Clusterise pokemons based on their cries, compare the clusters to the official EGG GROUPS which define pokemons that can reproduche with each other (similar to a group of species)

Method used: time series clusterization (DWT , SBD metrics), spectrogram clusterization with CNN , using data augmentation based on SpecAugment

1) Get the audio files, turn them into CSV for the time serie part
2) For CNN  : turn the audio files into spectrogramm, for each spectrogramm create 5 augmented ones
3) Use a pretrained Resnet0 model
4) Extract the features of the model
5) Use clusterization methods on the features : Kmeans, PAM, HCA, SVM ?
6) Compare the clusters to the official groups :
  - We define a a metric of "MISPLACES NEIGHBOURS" For an element = Nb elements that should be in the same clusters but are not + Nb of elements that should not be in the same clusters but are / Nb of unique elements  in cluster + Egg group to which the element belongs

First results : Kmean is not able to distinguish the clusters at all, maybe use methods which are more adapted to high number of variables like SVM ? 

