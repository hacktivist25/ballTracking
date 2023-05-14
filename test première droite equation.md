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
L'algorithme la transforme en noir et blanc et prend les contours avec un seuillage automatique sur un filtre de canny :

![ligne NB](https://github.com/hacktivist25/ballTracking/assets/125929174/13e767e5-f338-47de-9625-d04c508b7a22)



Une fois la transformée de Hough faite, on obtient rho et theta comme suit : en traçant un plan de hough qui utilise l'équation suivante :

<img width="508" alt="Principe hough" src="https://github.com/hacktivist25/ballTracking/assets/125929174/1620bebb-d5fd-447a-9c3f-de50598e0162">

nous utilisons cela dans l'équation y = -cos(theta)/sin(theta) x + rho / sin(theta), on on trouve l'équation de la droite ainsi :

Voici quelques tests : tout d'abord avec une résolution en distance de 1 pour 1, et une résolution angulaire d'1° :
![plan de hough reperage max](https://github.com/hacktivist25/ballTracking/assets/125929174/ea53bd0a-e7a0-49d4-a89d-3df8f85f1ae4)
![droite reconnue](https://github.com/hacktivist25/ballTracking/assets/125929174/471c3aa3-9360-4df5-bec8-a7f5736f51d5)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/57457367-89e9-4559-89e3-f6f84e3c0057)

Cette fois : distance 4 pour 1, 0.1° de résolution angulaire :
![plan hough reperage max](https://github.com/hacktivist25/ballTracking/assets/125929174/abf96d39-29aa-4e34-9c9f-fe83391898e9)
![droite reconnue](https://github.com/hacktivist25/ballTracking/assets/125929174/d6f479f2-f502-495a-932a-5499355673af)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/c39291bd-f4bf-42b2-b30d-efc9aacf663b)

puis 4 pour 1 en distance, 1° en résolution angulaire :
![plan de hough avec reperage du max](https://github.com/hacktivist25/ballTracking/assets/125929174/ff90890d-186d-4668-a735-19fd0c0504c8)
![droite trouvee](https://github.com/hacktivist25/ballTracking/assets/125929174/2b132c6e-0ece-405e-ae71-e7fe169b12e0)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/e37097dd-0618-4c10-994e-d0e6efec54b2)




