# ballTracking
ball tracking with a raspbery pi model 4B and its' camera, done by Hough Transform

====FIRST SESSION 02/20/2023====
dégrossissage du projet : MindMap des étapes en gros, que l'on va dégrossir de notre côté : """"""""""""INSERER PHOTO MINDMAP INITIAL"""""""

Premier réflexe : prendre connaissance de l'outil de travail principal : la transformée de Hough
On comprend que c'est un changement de repère représentant une droite par un point dans l'espace de Hought (r,Theta)
Elle consiste a tracer une courbe représentant l'ensemble des paramètres (r,theta) de droites passant par un point (x,y) :
Voir : icnisnlycee.free.fr : tap Hough : premier article (le seul)

CONSEIL DU PROFESSEUR :
La problématique est trop complexe a analyser d'un bloc :
Commencer par :
- initialiser le raspberrypi avec raspberry pi imager, et le charger sur la carte via microSD
- prendre une image simple (une ligne tracée sur un papier, une séparation au sol) et trouver l'horizon

Cela va nous permettre de comprendre l'outil de travail principal

Pour la prochaine fois, il faudra maîtriser le concept de l'espace de Hough, comprendre la théorie derrière (matrices accumulatrices, représentations d'une droite, d'un cercle dans cet espace
Il faudra pouvoir mettre en oeuvre aisément la solution pour trouver un horizon
Ppour cela :
- voir le format de l'image du raspberry
- voir les protocoles de transmission de données (qu'est ce qui fera le traitement d'image, le raspberry ou un ordinateur tierce ?)
- poids d'une image (RGB vs noir et blan)
- temps de traitement (caractérisation vitesse du processeur)
- média pour visualiser les données

A LA FIN : on doit avoi une idée des différentes problématiques sous-jacentes à ce traitement d'image, il faudra pouvoir élaborer un cahier des charges, ou à minima une feuille de route assez détaillée sur les étapes, qui permettront d'étoffer un cahier des charges construit au fur et à mesure
