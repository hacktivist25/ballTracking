# ballTracking
ball tracking with a raspbery pi model 4B and its' camera, done by Hough Transform

====PREMIERE SEANCE 02/20/2023====
dégrossissage du projet : MindMap des étapes en gros, que l'on va dégrossir de notre côté : 
![mindmap initiale](https://user-images.githubusercontent.com/125929174/221438325-de05e4b7-b414-42c5-928b-45e290be5663.jpg)


Premier réflexe : prendre connaissance de l'outil de travail principal : la transformée de Hough
On comprend que c'est un changement de repère représentant une droite par un point dans l'espace de Hought (r,Theta)
Elle consiste a tracer une courbe représentant l'ensemble des paramètres (r,theta) de droites passant par un point (x,y) :
Voir : icnisnlycee.free.fr : tap Hough : premier article (le seul)

CONSEIL DU PROFESSEUR :
La problématique est trop complexe a analyser d'un bloc :
Commencer par :
- initialiser le raspberrypi avec raspberry pi imager, et le charger sur la carte via microSD
- prendre une image simple (une ligne tracée sur un papier, une séparation au sol) et trouver l'horizon


// Pour initialiser raspberry
// https://www.tomshardware.com/how-to/set-up-raspberry-pi
// Il faut raspberryPi Imager

// idée des specs raspberryPi

<img width="404" alt="apercu specs RaspBerryPi 4B" src="https://user-images.githubusercontent.com/125929174/221440740-82a2a363-295b-4e3e-8376-e7a1f152652a.png">

-----documentation raspberry-----
https://www.raspberrypi.com/documentation/



Cela va nous permettre de comprendre l'outil de travail principal

Pour la prochaine fois, il faudra maîtriser le concept de l'espace de Hough, comprendre la théorie derrière (matrices accumulatrices, représentations d'une droite, d'un cercle dans cet espace
Il faudra pouvoir mettre en oeuvre aisément la solution pour trouver un horizon
Ppour cela :
- voir le format de l'image du raspberry
- voir les protocoles de transmission de données (qu'est ce qui fera le traitement d'image, le raspberry ou un ordinateur tierce ?)
- poids d'une image (RGB vs noir et blan)
- temps de traitement (caractérisation vitesse du processeur)
- média pour visualiser les données

A LA FIN : on doit avoir une idée des différentes problématiques sous-jacentes à ce traitement d'image, il faudra pouvoir élaborer un cahier des charges, ou à minima une feuille de route assez détaillée sur les étapes, qui permettront d'étoffer un cahier des charges construit au fur et à mesure

Avant la séance n°2 du 27 février, écumage des articles suivants :
- https://towardsdatascience.com/lines-detection-with-hough-transform-84020b3b1549
  Donne un code déjà tout fait et expliqué sur la transformée d hough et son utilisation sur la reconnaissance de lignes droites : il utilise uniquement les modules numpy et matplotlib, deux modules bien connus. la notion de matrice accumulatrice est expliquée, et la quantification des données est évoquée
<img width="508" alt="Principe hough" src="https://user-images.githubusercontent.com/125929174/221435980-d601a1cd-9358-4c37-b273-7a885e83e502.png">
il suffit de prendre en input une image, faire la détextion de bord (filtre de Canny par exemple, ou méthode des gradients, qui permet en plus d'optimiser l'algorithme, Roberts Cross, Sobel), et boucler pour chaque edge point sur les angles theta, remplir la matrice accumulatrice, et les maxima locaux de cette matrice accumulatrice représenteront des droites probables

- https://homepages.inf.ed.ac.uk/rbf/HIPR2/hough.htm
idem, mais aborde le fait que pour une détection de cerle, dont l'équation serait : <img width="168" alt="équation cercle" src="https://user-images.githubusercontent.com/125929174/221437115-ea9d1250-0f87-4447-a062-ae465496a613.png">
avec (a,b) coordonnées du centre du cerle, r son rayon, la matrice accumulatrice est désormais en 3 dimensions
il propose également une série d'exercices pour prendre en main la transformée de hought sur des figures simples, puis des cercles

- https://sbme-tutorials.github.io/2021/cv/notes/4_week4.html
<img width="339" alt="principe" src="https://user-images.githubusercontent.com/125929174/221437736-a7ab1999-426d-4f61-91de-2b3ba449cbb5.png">
rien de neuf, juste un énième exemple

- https://www.sciencedirect.com/topics/computer-science/hough-transforms
- recueil d'articles scientifiques pour la transformée de hought de haut niveau (optimisation temps de calcul, ect :  à utiliser en fin de projet

- https://www.uio.no/studier/emner/matnat/ifi/INF4300/h09/undervisningsmateriale/hough09.pdf
- énième exemple

===DEUXIEME SEANCE 27/02/23===
on va avoir besoin peut-être de ça : https://roboticsbackend.com/raspberry-pi-run-python-script-in-the-terminal/
et des documents au dessus pour le programme
et les documents au début sur le site oficiel de raspberrypi pour avoir les modules caméra, ect

Objectifs de la séance :
IL faut pouvoir avoir python, et deux modules numpy et et matplotlib s'ils n'y sont pas nativement
On va donc effectuer la transformée de hought d'une simple ligne tracée quelquepart : il faut prendre en main le module caméra, transmettre l'image, la traiter, et faire la transformée
On s'occupera plus tard des spécifications sur la mémoire vive disponible, le temps de calcul, les liaisons caméra/processeur, les protocoles de communication, ect
Pour le moment, on manipule bêtement pour savoir comment marche le matériel, ensuite le reste roulera tout seul



pour la caméra, son initialisation :
- https://raspberry-lab.fr/Composants/Utilisation-Camera-sur-Raspberry-Pi-Francais/
pour rpendre en main l'IDE
- https://realpython.com/python-raspberry-pi/#getting-to-know-the-raspberry-p

====TRAVAIL ACCOMPI====
reconfiguraiton de la carte SD
Chargement des modules utiles sur le raspberry : IDE Mü, qui contient déjà toutes les bibliopthèques que l'on souhaite (matplotlob.pyplot, numpy, picamera, math)
configuration VNC
Configuration WIFI
Configuration Caméra (détection par le module, utilisabilité)
Prise en main du module picamera : codage d'une fonction takePhoto, ave la qualité que l'on veut
Prise d'une photo ENFIN CORRECTE d'une ligne sur du papier blanc
Transformation de celle-ci en noir et blanc : parfait

====PENDANT CE TEMPS LA A POUDLARD (chez moi)====
compréhension de la transformé de hough sur une ligne : manipulation de matrices accumulatrices, utilisation des deux formules du dessus rhp = xcostheta+ysintheta et la transformée inverse pour vérifier que cela marchait bien
https://github.com/hacktivist25/ballTracking/blob/838cb90465e8612091c43e116d69d6bc55a47782/test%20premi%C3%A8re%20droite%20equation

===POUR LA PROCHAINE FOIS===
Se renseigner sur la transformée de hough en cercle
Voir le filtre de Canny ou autres (lequel prend le moins de temps, bruite le moins, pour notre usage)
un peu de specs sur le matériel utilisé et les process effectués

========TROISIEME SEANCE du 06/03/2023======
on a élaboré correctement l'algorithme de transformation de hough, obtenu cette image de la transformée, et repéré le maximum, et tracé la droite reconnue : ça marche...
pas plus de choses à dire, ça a été long mais efficace, pas de sources supplémentaires

===pendant ce temps à poudlard===
mise sous forme correcte de l'algorithme, des graphes, pour bien séquencer la chose et la rendre limpide

======QUATRIEME SEANCE du 13/03/2023======
finissage de l'algorithme de détection d'horizon, condensage sous un script qui "fait tout" : prise de photo, demande de treshold, ect... rine à dire sur cette séance, juste du codage et du test à profusion
 ===pendant ce temps à poudlard===
 automatiser le threshold, rendre le code beaucoup plus simple, y ajouter des modulation de résolution de distance, angulaire, pour moduler la vitesse de traitement et la précision
 
 =====CINQUIEME SEANCE DU 21/03/2023=====
 Malheureusement, l'automatisation du treshold laisse à désirer, mais la vitesse de l'algorithme en changeant la résolution en distance et angulaire est folle, de l'ordre de 2 ou 3 secondes pour faire le traitement complet
