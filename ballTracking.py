##UTLILISE LE FILTRE DE CANNY
import time
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import VL53L0X

import picamera
import datetime

import numpy as np
from numpy import asarray
import matplotlib.pyplot as plt
from PIL import Image as img
import math as m
import cv2
#import cv2 as cv

#ouverture d'une image
#im=img.open("LIGNE_NB.jpg")
#il faudra ouvrir l'image de départ départ pour faire la mini démo

#sauvegarde : im.save(nom)

#diplay image
#im.show()
#plt.imshow(im)

#afficher un pixel de coordonnées x,y
#im.getpixel((200,350))

#le moyen unterne de conversion en noir et blanc
 #im2=im.convert("1")

#le moyen de modifier un pixel
 # im.putpixel((x,y),(R,G,B))


def capture(name,x=3280, y=1845):
    camera = picamera.PiCamera()
    camera.resolution = (x,y)
    camera.capture(name)
    imBrute = img.open(name)
    return (imBrute)

def determinist(imIntermediaire):
    tab=[(0) for k in range(256)]
    for x in range(int(imIntermediaire.width/4)):
        for y in range(int(imIntermediaire.height/4)):
            tab[imIntermediaire.getpixel((4*x,4*y))]+=1
    maxi=max(tab)
    for k in range(len(tab)):
        tab[k]/=maxi
    plt.plot([(k) for k in range (256)],tab)
    plt.show()
    q=0
    threshold=0
    while(q<0.09):
        q+=tab[threshold]
        threshold+=1
    print("threshold trouvé : ", threshold)
    return threshold

def traitementImage(imBrute): #conversion d'une image de format RGB en format N&B avec effaçage du petit bruit, empirique
    imIntermediaire=imBrute.convert("L")
    threshold=determinist(imIntermediaire)
    #threshold=90 est l'idéal pour l'image de base
#     imIntermediaire.show()
    imTraitee=imIntermediaire.point(lambda p:255 if p > threshold else 0)
    imTraitee.show()
    imTraitee=imTraitee.convert("1")
    imTraitee.show()
    return (imTraitee)
#on récupère une imTraitee

def traitementImageCanny(imBrute):
    imTraitement = cv2.imread(imBrute.filename)  # Read image

    #Setting parameter values
    t_lower = 80  # Lower Threshold
    t_upper = 110  # Upper threshold

    # Applying the Canny Edge filter
    edge = cv2.Canny(imTraitement, t_lower, t_upper)
    imTraitee=img.fromarray(edge)
    imTraitee.show()
    return (imTraitee)


def constructionMatriceAccumulatrice(imTraitee,resolutionAngulaire = 1, resolutionDistance=1):
    theta = [k for k in range(0,int(180/resolutionAngulaire),1)]
    distanceMax=int((((3280/resolutionDistance)**2)+((1845/resolutionDistance)**2))**(1/2))+1 #diagonale maximale
    matriceAccumulatrice = np.zeros((int(180/resolutionAngulaire),distanceMax)) #matrice qui permettra le dessin du plan de hough
    coord= []
    for x in range(int(3280/resolutionDistance)) :
        for y in range(int(1845/resolutionDistance)):
            if imTraitee.getpixel((x*resolutionDistance,y*resolutionDistance))==255:
                coord.append((x*resolutionDistance,y*resolutionDistance))
    #récupéré les coordonnées des points d'intérêt

    for a in coord :
        for T in theta:
            T=T*resolutionAngulaire
            x=a[0]
            y=a[1]
            r=((x/resolutionDistance)*m.cos((T*2*m.pi)/360))+((y/resolutionDistance)*m.sin((T*2*m.pi)/360))
            matriceAccumulatrice[int(T/resolutionAngulaire)][int(r)] +=1
    return ([matriceAccumulatrice, imTraitee])

def reconstructionDroite(matriceAccumulatrice,imBrute,resolutionAngulaire,resolutionDistance, nbligne):
    largeurX = len(matriceAccumulatrice[0])
    longueurY = len(matriceAccumulatrice[0][0])
    planDeHough = img.new("L",size=(largeurX,longueurY))
    for x in range(largeurX):
        for y in range (longueurY):
            planDeHough.putpixel((x,y),int(matriceAccumulatrice[0][x,y]))
    planDeHough.save("plan_de_hough.jpg")
    #on montre le plan de hough
    plt.imshow(planDeHough,cmap="binary_r")
    plt.xlabel("theta")
    plt.ylabel("rho")
    plt.suptitle("plan de hough")
    plt.show()

    #recherche du max
    max_index = np.unravel_index(matriceAccumulatrice[0].argmax(), matriceAccumulatrice[0].shape) #trouve l'index d'un max de la matrice
    m=matriceAccumulatrice[0][max_index]
    listMax=[max_index]
    valeurmax=matriceAccumulatrice[0][max_index]
    matriceAccumulatrice[0][max_index]=0
    nb=1;
    while (nb<nbligne):
        max_index = np.unravel_index(matriceAccumulatrice[0].argmax(), matriceAccumulatrice[0].shape)
        while ((((max_index[0]-listMax[0][0])**2)+((max_index[1]-listMax[0][1])**2))**(1/2) <=20):
            matriceAccumulatrice[0][max_index]=0
            max_index = np.unravel_index(matriceAccumulatrice[0].argmax(), matriceAccumulatrice[0].shape)

        listMax.append(max_index)
        nb+=1

    print("index du max et valeur :",max_index,valeurmax)

    #coloriage des max
    for z in listMax:
        x=z[0]
        y=z[1]
        for i in range(-1,2):
            for j in range(-1,2):
                if x+i >=0 and y+j >=0 and x+i<largeurX and y+j <longueurY  :
                    planDeHough.putpixel((x+i,y+j),190)
    plt.imshow(planDeHough,cmap="binary_r")
    plt.xlabel("theta")
    plt.ylabel("rho")
    plt.suptitle("plan de hough avec repérage des max")
    plt.show()

    print("ci joint la liste des maximas globaux de la matrice accumulatrice :")
    print(listMax)


    distanceMax=int(((3280**2)+(1845**2))**(1/2)+1) #diagonale maximale
    print ("distance max = ", distanceMax)
    stockEquation=[]
    for w in range(len(listMax)):
        thetaL=listMax[w][0]*resolutionAngulaire
        rhoL=listMax[w][1]*resolutionDistance
        print("thetaL=",thetaL,"rhoL =",rhoL)
        while (rhoL>=distanceMax/2) :
            print(rhoL, "  avant")
            rhoL =rhoL - distanceMax
            print(rhoL, "  après")


        #equation de la forme ax + b
        if (thetaL!=0):
            a1=-np.cos(thetaL*2*np.pi/360)/np.sin(thetaL*2*np.pi/360)
            b1=rhoL/np.sin(thetaL*2*np.pi/360)
            x=[k for k in range(3280)]
            y=[((a1*x[k])+b1) for k in x]
            print ("équation trouvée : ","y = ",a1,"x + ",b1)
            stockEquation.append([x,y])
        else :
            x=[rhoL for k in range(3280)]
            y=[k for k in range(3280)]
            stockEquation.append([x,y])

        for k in range(len(x)):
            if y[k]>=0 and y[k]<1845:
                imBrute.putpixel((x[k],int(y[k])),150)
            if y[k]>=0 and y[k]+1<1845:
                imBrute.putpixel((x[k],int(y[k]+1)),150)
            if y[k]>=0 and y[k]-1<1845:
                imBrute.putpixel((x[k],int(y[k]-1)),150)
            if y[k]>=0 and y[k]<1845 and x[k]+1<3280:
                imBrute.putpixel((x[k]+1,int(y[k])),150)
            if y[k]>=0 and y[k]<1845 and x[k]-1>=0:
                imBrute.putpixel((x[k]-1,int(y[k])),150)


        #tracage du centre
        for u in range(-1,2):
            for i in range(-10,11):
                if 1640+u+i >= 0 and 1640 + u +i <3280 and 922+u+i>=0 and 922+u+i<1845:
                    imBrute.putpixel((1640+u+i,922+u),150)
                    imBrute.putpixel((1640+u,922+i+u),150)
    imBrute.show()

    return stockEquation

def Horizon(imageBrute,resolutionAngulaire,resolutionDistance, nbligne):
    stockEquation=reconstructionDroite(constructionMatriceAccumulatrice(traitementImageCanny(imageBrute),resolutionAngulaire,resolutionDistance),imageBrute,resolutionAngulaire,resolutionDistance, nbligne)
    return stockEquation



#Horizon(img.open("ligne.jpg"),1,4,1)

### cercle dont on connait le rayon

def coordCercleRayonEstime(a,b,rayonEstime,matrice,resolutionDistance, resolutionAngulaireCercleInter):#a et b coordonnnées réelles de son centre en pixels, resol détermine le nombre de points du cercle
    theta=0
    pasAngulaire=(2*m.pi)/resolutionAngulaireCercleInter
    while(theta<2*m.pi):
        x=int(rayonEstime*m.cos(theta)+a)
        y=int(rayonEstime*m.sin(theta)+b)
        theta+=pasAngulaire
        if ((x<3280) and (y<1845) and (x>=0) and (y>=0)):
            matrice[int(x/resolutionDistance)][int(y/resolutionDistance)]+=1

def constructionMatriceAccumulatriceCercleConnu(imTraitee,rayonEstime, resolutionAngulaire = 1, resolutionDistance=1, resolutionAngulaireCercleInter=32):

    matriceAccumulatriceCercleConnu = np.zeros((int(3280/resolutionAngulaire)+1,int(1845/resolutionDistance)+1)) #matrice qui permettra le dessin du plan de hough
    coord= [] #rassemble les points d'intérêt, i.e ceux qui sont un contour
    for x in range(int(3280/resolutionDistance)) :
        for y in range(int(1845/resolutionDistance)):
            if imTraitee.getpixel((x*resolutionDistance,y*resolutionDistance))==255:
                coordCercleRayonEstime(x*resolutionDistance,y*resolutionDistance,rayonEstime,matriceAccumulatriceCercleConnu,resolutionDistance,resolutionAngulaireCercleInter)
    #récupéré les coordonnées des points d'intérêt, en pixels de l'image, sans les considérations de résolution
    return matriceAccumulatriceCercleConnu

def reconstructionCercle(matriceAccumulatriceCercleConnu,imBrute,rayonEstime,resolutionAngulaire=1,resolutionDistance=1,resolutionAngulaireCercleInter=32):
    largeurX = len(matriceAccumulatriceCercleConnu)
    longueurY = len(matriceAccumulatriceCercleConnu[0])
    planDeHoughCercle = img.new("L",size=(largeurX,longueurY))
    for x in range(largeurX):
        for y in range (longueurY):
            planDeHoughCercle.putpixel((x,y),int(matriceAccumulatriceCercleConnu[x,y]))
    planDeHoughCercle.save("plan_de_hough.jpg")
    #on montre le plan de hough
    plt.imshow(planDeHoughCercle,cmap="binary_r")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.suptitle("plan de hough")
    plt.show()

    #recherche du max
    max_index = np.unravel_index(matriceAccumulatriceCercleConnu.argmax(), matriceAccumulatriceCercleConnu.shape) #trouve l'index d'un max de la matrice
    m=matriceAccumulatriceCercleConnu[max_index]
    matriceAccumulatriceCercleConnu[max_index]=0
    listMax=[max_index]
    print("index du max et valeur :",max_index,m)
    while (matriceAccumulatriceCercleConnu[np.unravel_index(matriceAccumulatriceCercleConnu.argmax(), matriceAccumulatriceCercleConnu.shape)]==m):
        listMax.append(np.unravel_index(matriceAccumulatriceCercleConnu.argmax(), matriceAccumulatriceCercleConnu.shape))
        matriceAccumulatriceCercleConnu[np.unravel_index(matriceAccumulatriceCercleConnu.argmax(), matriceAccumulatriceCercleConnu.shape)]=0

    #coloriage des max
    for z in listMax:
        x=z[0]
        y=z[1]
        for i in range(-2,3):
            for j in range(-2,3):
                if (x+i<int(3280/resolutionDistance)) and (x+i >0) and (y+i<int(1845/resolutionDistance)) and (y+i >0):
                    planDeHoughCercle.putpixel((x+i,y+j),210)
    plt.imshow(planDeHoughCercle,cmap="binary_r")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.suptitle("plan de hough avec repérage du max")
    plt.show()

    print("ci joint la liste des maximas globaux de la matrice accumulatrice :")
    print(listMax)
    aCentre=listMax[0][0]*resolutionDistance
    bCentre=listMax[0][1]*resolutionDistance

    print("aCentre=",aCentre,"bCentre =",bCentre)

    #determination des coordonnees du cercle determiné pour le tracer sur l'image brute
    theta=0
    coordCercle=[]
    pasAngulaire=(2*np.pi)/(resolutionAngulaireCercleInter*20) #le coef multiplicatif est là pour traçer plus de points du cercle
    while (theta<2*np.pi):
        coordCercle.append((int(rayonEstime*np.cos(theta)+aCentre),int(rayonEstime*np.sin(theta)+bCentre)))
        theta+=pasAngulaire

    print("quelques coordonnées du cercle et la longueur de la liste : ", len(coordCercle),"  ", coordCercle[0],"   ", coordCercle[-1])
    for c in coordCercle:
        for k in range(-3,4):
            for j in range(-3,4):
                if ((c[0]+k<3280) and (c[1]+j<1845) and (c[0]+k>=0) and (c[1]+j>=0)):
                    imBrute.putpixel((c[0]+k,c[1]+j),120)
    for k in range(-3,4):
            for j in range(-3,4):
                if ((aCentre+k<3280) and (bCentre+j<1845) and (aCentre+k>=0) and (bCentre+j>=0)):
                    imBrute.putpixel((aCentre+k,bCentre+j),120)
    plt.imshow(imBrute)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.suptitle("image brute avec le cercle trouvé")
    plt.show()

def reconnaissanceCercleRayonConnu(imageBrute,rayonEstime,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter):
    reconstructionCercle(constructionMatriceAccumulatriceCercleConnu(traitementImageCanny(imageBrute), rayonEstime,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter),imageBrute, rayonEstime,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter)

#reconnaissanceCercleRayonConnu(img.open("cercle.jpg"),494,1,1,32)

#sur cerlce.pnj : centre : 1737,1014
#rayon : 1523-535/2 and 2228-1242/2 DONNANT (494 ET 496) : GG A TOUS !


###Cercle de rayon inconnu

def coordCercleRayonR(a,b,r,matrice,pasDeRayon,resolutionDistance, resolutionAngulaireCercleInter):#a et b coordonnnées réelles de son centre en pixels, resol détermine le nombre de points du cercle
    theta=0
    pasAngulaire=(2*m.pi)/resolutionAngulaireCercleInter
    while(theta<2*m.pi):
        x=int(r*m.cos(theta)+a)
        y=int(r*m.sin(theta)+b)
        theta+=pasAngulaire
        if ((x<3280) and (y<1845) and (x>=0) and (y>=0)):
            matrice[int(r/pasDeRayon)][int(x/resolutionDistance)][int(y/resolutionDistance)]+=50

def traitementImageCannyGradient(imBrute, stockEquation=[]):
    imTraitement = cv2.imread(imBrute.filename)  # Read image

    #Setting parameter values
    t_lower = 60  # Lower Threshold
    t_upper = 110  # Upper threshold

    # Applying the Canny Edge filter
    imTraitee = cv2.Canny(imTraitement, t_lower, t_upper)

    #effaçage des droites trouvées pour ne pas perturber la détection de cercle sur l'image NB de canny

    for k in range(len(stockEquation)):
        x=stockEquation[k][0]
        y=stockEquation[k][1]
        for l in range(len(x)):
            for i in range(-15,16):
                for j in range(-15,16):
                    if round(x[l])+i < 3280 and round(x[l])+i >=0:
                        if round(y[l])+j>=0 and round(y[l])+j <1845:
                            if imTraitee[round(y[l])+j][round(x[l])+i] >10:
                                imTraitee[round(y[l])+j][round(x[l])+i]=0

    apercu=img.fromarray(imTraitee)
    apercu.show()
    return (imTraitee)

def constructionMatriceAccumulatriceCercleInconnu(imTraitee,pasDeRayon=10, rayonMini=25 ,resolutionAngulaire = 1, resolutionDistance=1, resolutionAngulaireCercleInter=32):
    #matrices de convolution
    Gx=np.array(([-1,0,1],[-2,0,2],[-1,0,1]))
    Gy=np.array(([-1,-2,-1],[0,0,0],[1,2,1]))
    distanceMax=round(1845/2)
    #on considère que le rayon du cercle que l'on vera a un rayon minimal et un rayon maximal
    matriceAccumulatriceCercleInconnu=np.zeros((((distanceMax-rayonMini)//pasDeRayon)+2,round(1845/resolutionDistance)+2,round(3280/resolutionDistance)+1))
    CXY=[] #liste des coordonnées des points du cercle de la matrice accumulatrice
    for x in range(round(3280/resolutionDistance)) :
        for y in range(round(1845/resolutionDistance)):
            if imTraitee[y*resolutionDistance,x*resolutionDistance]==255:
                matriceAccumulatriceCercleInconnu[len(matriceAccumulatriceCercleInconnu)-1,y,x]=1
                CXY.append([[x,y]])#faux pixels
    for i in range(len(CXY)):
        x=CXY[i][0][0]*resolutionDistance #conversion en vrais pixels
        y=CXY[i][0][1]*resolutionDistance #conversion en vrais pixels
        if x>=1 and y>=1 and x<3279 and y<1844 :
            A=np.array(([imTraitee[y-1,x-1],imTraitee[y-1,x],imTraitee[y-1,x+1]],[imTraitee[y,x-1],imTraitee[y,x],imTraitee[y,x+1]],[imTraitee[y+1,x-1],imTraitee[y+1,x],imTraitee[y+1,x+1]])) #matrice 3x3 autour du point du cercle considéré
            CXY[i].append(m.atan2((((Gy*A).sum())/9),(((Gx*A).sum())/9)))
            for r in range(rayonMini,distanceMax,pasDeRayon):
                theta=CXY[i][1]*360/(2*np.pi)
                U=np.arange(theta-25,theta+25,1)
                x=CXY[i][0][0]
                y=CXY[i][0][1]
                for T in U:
                    a=round(r*m.cos(T*2*np.pi/360)+x)
                    b=round(r*m.sin(T*2*np.pi/360)+y)
                    if (a>=0) and (a<round(3280/resolutionDistance)) and (b>=0) and (b<round(1845/resolutionDistance)):
                        matriceAccumulatriceCercleInconnu[((r-rayonMini)//pasDeRayon),b,a]+=1
                    a=round(-r*m.cos(-T*2*np.pi/360)+x)
                    b=round(-r*m.sin(-T*2*np.pi/360)+y)
                    if (a>=0) and (a<round(3280/resolutionDistance)) and (b>=0) and (b<round(1845/resolutionDistance)):
                        matriceAccumulatriceCercleInconnu[((r-rayonMini)//pasDeRayon),b,a]+=1
    plt.imshow(matriceAccumulatriceCercleInconnu[len(matriceAccumulatriceCercleInconnu)-1])
    plt.show()
    return matriceAccumulatriceCercleInconnu

#reconnaissanceCercleRayonInconnu(img.open("cercle.jpg"),20,50,1,1,128)

def reconstructionCercleInconnu(matriceAccumulatriceCercleInconnu,imBrute,pasDeRayon=10,rayonMini=25,resolutionAngulaire=1,resolutionDistance=1,resolutionAngulaireCercleInter=32):
    #recherche du max
    max_index = np.unravel_index(matriceAccumulatriceCercleInconnu.argmax(), matriceAccumulatriceCercleInconnu.shape) #trouve l'index d'un max de la matrice
    m=matriceAccumulatriceCercleInconnu[max_index]
    matriceAccumulatriceCercleInconnu[max_index]=0
    listMax=[max_index]
    print("index du max et valeur :",max_index,m)
    while (matriceAccumulatriceCercleInconnu[np.unravel_index(matriceAccumulatriceCercleInconnu.argmax(), matriceAccumulatriceCercleInconnu.shape)]==m):
        listMax.append(np.unravel_index(matriceAccumulatriceCercleInconnu.argmax(), matriceAccumulatriceCercleInconnu.shape))
        matriceAccumulatriceCercleInconnu[np.unravel_index(matriceAccumulatriceCercleInconnu.argmax(), matriceAccumulatriceCercleInconnu.shape)]=0
    print("longueur liste des maxima : ", len(listMax), "      coordonnées : ", listMax)
    #AAA=img.fromarray(matriceAccumulatriceCercleInconnu)
    #coloriage des max
    #for z in listMax:
    #    y=z[0]
    #    x=z[1]
    #    for i in range(-2,3):
    #        for j in range(-2,3):
    #            AAA.putpixel((x+i,y+j),210)
    #AAA.show()

    bCentre=listMax[0][1]*resolutionDistance
    aCentre=listMax[0][2]*resolutionDistance
    rayon=((listMax[0][0]*pasDeRayon)+rayonMini)*resolutionDistance

    plt.imshow(matriceAccumulatriceCercleInconnu[listMax[0][0]])
    plt.show()

    for i in range(-3,4):
        for j in range(-3,4):
            imBrute.putpixel((int(aCentre)+i,int(bCentre)+j),180)
    #imBrute.show()


    print("aCentre=",aCentre,"   bCentre =",bCentre,"   rayon =",rayon)

    #determination des coordonnees du cercle determiné pour le tracer sur l'image brute
    theta=0
    coordCercle=[]
    pasAngulaire=(2*np.pi)/(resolutionAngulaireCercleInter*20) #le coef multiplicatif est là pour traçer plus de points du cercle
    while (theta<2*np.pi):
        coordCercle.append((int(rayon*np.cos(theta)+aCentre),int(rayon*np.sin(theta)+bCentre)))
        theta+=pasAngulaire

    for c in coordCercle:
        for k in range(-3,4):
            for j in range(-3,4):
                if ((c[0]+k<3280) and (c[1]+j<1845) and (c[0]+k>=0) and (c[1]+j>=0)):
                    imBrute.putpixel((c[0]+k,c[1]+j),120)
    for k in range(-3,4):
            for j in range(-3,4):
                if ((aCentre+k<3280) and (bCentre+j<1845) and (aCentre+k>=0) and (bCentre+j>=0)):
                    imBrute.putpixel((aCentre+k,bCentre+j),120)
    #centre du cercle
    for u in range(-1,2):
            for i in range(-10,11):
                if aCentre+u+i >= 0 and aCentre + u +i <3280 and bCentre+u+i>=0 and bCentre+u+i<1845:
                    imBrute.putpixel((aCentre+u+i,bCentre+u),150)
                    imBrute.putpixel((aCentre+u,bCentre+i+u),150)

    plt.imshow(imBrute)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.suptitle("image brute avec le cercle trouvé")
    plt.show()
    return  [imBrute,aCentre,bCentre]

def reconnaissanceCercleRayonInconnu(imageBrute,pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter):
    reconstructionCercleInconnu(constructionMatriceAccumulatriceCercleInconnu(traitementImageCannyGradient(imageBrute), pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter),imageBrute, pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter)

#reconnaissanceCercleRayonInconnu(img.open("cercle.jpg"),20,50,4,4,128)
#circles = cv2.HoughCircles(traitementImageCannyGradient(img.open("cercle.jpg")), cv2.HOUGH_GRADIENT, 1.2,100)

def MatriceDistances (distance, angle=0, FOVX=62, FOVY=49, resol=20):
    matriceDist=np.zeros((2,int(1845/resol)+1,int(3280/resol) +1))
    for x in range(0,1640,resol):
        for y in range(0,922,resol):
            thetaX=(FOVX/2)*(x/1640)
            thetaY=(FOVY/2)*(y/922)
            dx=m.tan(thetaX*m.pi/180)*distance
            dy=m.tan(thetaY*m.pi/180)*distance
            matriceDist[0][(int(1845/(2*resol)))+int(y/resol)][(int(3280/(2*resol)))+int(x/resol)]=dx
            matriceDist[0][(int(1845/(2*resol)))+int(y/resol)][(int(3280/(2*resol)))-int(x/resol)]=dx
            matriceDist[0][(int(1845/(2*resol)))-int(y/resol)][(int(3280/(2*resol)))+int(x/resol)]=dx
            matriceDist[0][(int(1845/(2*resol)))-int(y/resol)][(int(3280/(2*resol)))-int(x/resol)]=dx
            matriceDist[1][(int(1845/(2*resol)))+int(y/resol)][(int(3280/(2*resol)))+int(x/resol)]=dy
            matriceDist[1][(int(1845/(2*resol)))+int(y/resol)][(int(3280/(2*resol)))-int(x/resol)]=dy
            matriceDist[1][(int(1845/(2*resol)))-int(y/resol)][(int(3280/(2*resol)))+int(x/resol)]=dy
            matriceDist[1][(int(1845/(2*resol)))-int(y/resol)][(int(3280/(2*resol)))-int(x/resol)]=dy
    return matriceDist





def total(imBrute,pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter, nblignes):

    stockEquation=Horizon(imBrute,resolutionAngulaire,resolutionDistance,nblignes)
    [imBrute,aCentre,bCentre]=reconstructionCercleInconnu(constructionMatriceAccumulatriceCercleInconnu(traitementImageCannyGradient(imBrute, stockEquation), pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter),imBrute, pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter)
    distance=21
    A=MatriceDistances(distance)
    print("coordonnées par rapport au centre de l image (centre optique) : ", A[0][round(bCentre/20)][round(aCentre/20)], A[1][round(bCentre/20)][round(aCentre/20)])
#total(img.open("blablabla.jpg"),5,50,1,4,128,2)

def totalCam(nom,pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter, nblignes):
    [imBrute,distance,angleHorizontal]=captureEcranData(nom)
    stockEquation=Horizon(imBrute,resolutionAngulaire,resolutionDistance,nblignes)
    [imBrute,aCentre,bCentre]=reconstructionCercleInconnu(constructionMatriceAccumulatriceCercleInconnu(traitementImageCannyGradient(imBrute, stockEquation), pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter),imBrute, pasDeRayon,rayonMini,resolutionAngulaire,resolutionDistance,resolutionAngulaireCercleInter)
    A=MatriceDistances(distance)
    print("coordonnées par rapport au centre de l image (centre optique) : ", A[0][round(bCentre/20)][round(aCentre/20)], A[1][round(bCentre/20)][round(aCentre/20)])


#totalCam("blablabla3.jpg",5,50,1,4,128,2)


# def a():
    image = cv2.imread("cercle.jpg")
    image=cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    #th,image=cv2.threshold(image,90,255,cv2.THRESH_BINARY)
    th,image = cv2.threshold(image, 128,192,cv2.THRESH_OTSU)
    image = cv2.medianBlur(image,5)
    cv2.namedWindow("detected circles", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("detected circles", 300, 700)
    cv2.imshow('detected circles',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cimg = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    circles = cv2.HoughCircles(image,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=10,maxRadius=500)
    circles = np.uint16(np.around(circles))
    for i in circles[0]:
        # draw the outer circle
        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

    cv2.namedWindow("detected circles", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("detected circles", 300, 700)
    cv2.imshow('detected circles',cimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    ### Concerne les capteurs de distance et gyromètre


### gyromètre
mpu = MPU9250(
    address_ak=AK8963_ADDRESS,
    address_mpu_master=MPU9050_ADDRESS_68, # Master has 0x68 Address
    address_mpu_slave=MPU9050_ADDRESS_68, # Slave has 0x68 Address
    bus=1,
    gfs=GFS_1000,
    afs=AFS_8G,
    mfs=AK8963_BIT_16,
    mode=AK8963_MODE_C100HZ)

mpu.configure() # Apply the settings to the registers.

def captureAngle(mpu=mpu):
    accelerationX = mpu.readAccelerometerMaster()[0]
    accelerationY = mpu.readAccelerometerMaster()[1]
    accelerationZ = mpu.readAccelerometerMaster()[2]
    pitch = 180 * m.atan (accelerationX/m.sqrt(accelerationY*accelerationY + accelerationZ*accelerationZ))/m.pi;
    print("angle : ", pitch)

    ### Capteur de distance

#Create a VL53L0X object

def captureDistance():
    tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)

    tof.open()
    # Start ranging
    tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)


    distance = tof.get_distance()
    if distance > 0:
        print("%d mm, %d cm, %d" % (distance, (distance/10),1))

    tof.stop_ranging()
    tof.close()
    return distance/10 #renvoie la valeur en millimètres


###capture d'écran + données !

def captureEcranData(name):
    imBrute = capture(name,x=3280, y=1845)
    angleHorizontal=captureAngle()
    distance=captureDistance()
    print("angleHorizontal = ", angleHorizontal, "    distance = ", distance )
    return [imBrute,distance,angleHorizontal]
