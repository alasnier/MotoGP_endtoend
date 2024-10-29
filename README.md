# MotoGP End-to-End : From Scraping to Dashboard

Bienvenue dans mon projet personnel **MotoGP End-to-End : From Scraping to Dashboard** ! Ce projet fait partie de mon portfolio en tant que data engineer, et il couvre toutes les étapes d'un workflow de données complet, de l'extraction des données jusqu'à leur visualisation.

## 🏍️ Objectif

L'objectif de ce projet est de :
1. Récupérer des données de statistiques MotoGP mises à jour chaque semaine.
2. Traiter, stocker et visualiser ces données dans un tableau de bord actualisé tous les lundis.

## 🛠️ Stack Technique

- **Langage** : Python (Pandas)
- **Outils** :
  - **Scraping** : `requests` library
  - **Pipeline de données** : Docker, Apache Airflow, Google BigQuery
  - **Visualisation** : Looker Studio

## 📋 Étapes du Projet

1. **Extraction des données** :
   - Scraping des saisons et de leurs IDs
   - Scraping des catégories de MotoGP et de leurs IDs
   - Scraping des événements (nom, ID, circuit, pays, date)
   - Scraping des coordonnées des circuits
   - Scraping des résultats des courses

2. **Stockage** :
   - Chargement des données dans **Google BigQuery**

3. **Automatisation** :
   - Création de fichiers `Dockerfile`
   - Développement de DAGs dans **Apache Airflow** pour :
     - Un DAG local
     - Un DAG Dockerisé

4. **Tableau de bord** :
   - Création d’un dashboard avec Looker Studio pour visualiser les résultats (lien : [Looker Studio Dashboard](https://lookerstudio.google.com/s/unJ9m98Qefg) - Mis hors ligne pour des raisons de coûts d’hébergement)

---

Ce projet met en pratique mes compétences en **Data Engineering**, en intégrant des workflows de données modernes et des technologies de pointe. 

## 🔄 Mises à Jour

Le projet est actualisé chaque lundi pour intégrer les nouvelles statistiques de MotoGP.
