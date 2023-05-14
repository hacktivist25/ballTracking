On ouvre la photo LIGNE_NB sur paint pour avoir ses coordonnées en pixel, et on calcule nous-même à la main l'équation de la droite dans le repère de l'image
Le but est de connaître le résultat pour voir si l'algorithme ne fait pas n'importe quoi


===============================================
NOTE IMPORTANTE :
Le repère : x vers la droite, y vers le bas, les repères d'images sur python et image sont les mêmes
===============================================
![ligne](https://github.com/hacktivist25/ballTracking/assets/125929174/8ee5481b-38cc-4e5d-a863-20aced7b4acb)
pixels des extrémités :
- Un pixel en   (1036 ; 896)
- l'autre en    (2790 ; 938)

a= \frac{ y2-y1 }{ x2-x1 }
 = \frac{ 938 - 896 }/{ 2790 - 1036 }
 = 0,0239

b=y2-ax2
 = 938 - 0,0239*2790
 = 871,2

----------------------------------------------------------------
l'équation doit être 0.0239x + 871.2 dans le repère de l'image
----------------------------------------------------------------
on va voir ce que renvoie l'algorithme que l'on a élaboré pour différentes résolutions angulaires et de distance : 
Tout d'abord, l'image de base déjà montrée au dessus est soumis à l'algorithme.
L'algorithme la transforme en noir et blanc et prand les contours avec un seuillage automatique sur un filtre de canny :

IMAGE TRANSFO N&B

Une fois la transformée de Hough faite, on obtient rho et theta comme suit :
Voici ce que renvoie l'algorithme :

nous utilisons cela dans l'équation y = -cos(theta)/sin(theta) x + rho / sin(theta), on on trouve l'équation
