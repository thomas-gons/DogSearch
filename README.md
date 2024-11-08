# Projet de Génération et Recherche d'Images par Similarité

Ce projet est une application pratique qui combine les concepts de *Deep Learning*, *Image-Based Processing*, et *Natural Language Processing (NLP)* dans le cadre d'une solution intégrée, développée par des étudiants en ingénierie spécialisée en Intelligence Artificielle à CY TECH.

## Objectifs du Projet

L'objectif de ce projet est de créer une interface interactive qui permet :

- **Génération de descriptions d'images** : Utilisation de modèles avancés tels que [CLIP](https://github.com/openai/CLIP) ou [InternVL](https://github.com/microsoft/InternImage) pour produire des descriptions détaillées à partir d'images fournies par l'utilisateur.
- **Recherche d'images similaires** : Proposition d'images similaires à celle fournie, basées sur des représentations de similarité dans l'espace vectoriel.
- **Recherche d'images par requête textuelle** : Une fonctionnalité de recherche par texte permettant de trouver des images correspondant à des descriptions textuelles. Cette recherche est optimisée par [Faiss](https://github.com/facebookresearch/faiss), une librairie de Facebook spécialisée dans les recherches de similarité rapides et efficaces.

## Technologies Utilisées

- **Modèles de Vision et Langage** : CLIP et InternVL pour la génération de descriptions et la correspondance d'images à partir de descriptions textuelles.
- **Faiss** : Accélération des recherches de similarité pour une expérience utilisateur rapide.
- **Interface Utilisateur** : Développement d'une interface intuitive pour faciliter l'utilisation des différentes fonctionnalités proposées.

## Structure du Projet

1. **Extraction et traitement des caractéristiques d'image** : Les images sont traitées pour extraire des vecteurs de caractéristiques à l'aide de modèles de vision.
2. **Génération de description textuelle** : À partir des vecteurs extraits, des descriptions sont générées.
3. **Système de recherche par similarité** : Faiss est utilisé pour accélérer les correspondances entre vecteurs d'images et requêtes textuelles, optimisant ainsi la recherche d'images similaires.

## Membres de l'Équipe

- **Louis-Alexandre LAGUET** - Étudiant en 3ème année de cycle ingénieur, CY TECH - IA
- **Thomas GONS** - Étudiant en 3ème année de cycle ingénieur, CY TECH - IA

## Objectifs Pédagogiques

Ce projet vise à appliquer de manière pratique les concepts de *Deep Learning*, *Image-Based Processing*, et *NLP*, en utilisant des outils et techniques modernes dans un cadre d'application concret. Ce projet permet également d'acquérir de l'expérience en développement de systèmes d'intelligence artificielle complets, de la manipulation de données multimodales (texte et image) à la construction d'une interface utilisateur performante.

## Commandes pour lancer le projet

### Frontend
```shell
npm i
npm run dev
```

### Backend
```shell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
