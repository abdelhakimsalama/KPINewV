# 01.01 — Prérequis techniques, licences et accès

## Objectif du fichier

- **À quoi sert ce fichier** : réunir tout ce qui doit être vrai **avant** de créer l'agent, pour ne pas se retrouver bloqué au milieu de l'étape 03.
- **Étape du développement** : étape 01, prérequis.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : vous vérifiez des accès et des réglages d'environnement ; vous ne créez encore rien.
- **Résultat attendu avant de passer à l'étape suivante** : toutes les cases de la section « Critères de fin d'étape » sont cochées, ou la case non cochée est explicitement acceptée comme risque.

---

## 1. Accès dont vous avez besoin

| Accès | Pourquoi | Comment vérifier |
|---|---|---|
| Rôle **Maker** dans l'environnement Power Platform cible | Créer l'agent | `copilotstudio.microsoft.com` s'ouvre et le bouton **New agent** est actif |
| **Lecture** sur la liste SharePoint `KPIDictionary` du site `ReportingTower10` | Brancher le Knowledge | Ouvrez la liste dans le navigateur : elle s'affiche |
| Droit d'installer/valider une **connexion SharePoint** | L'agent lit la liste avec les droits de l'utilisateur | À confirmer avec votre administrateur Power Platform |
| Accès **Power Platform admin center** (ou un interlocuteur qui l'a) | Poser les garde-fous de crédits (fichier `08_02`) | `admin.powerplatform.microsoft.com` s'ouvre |

## 2. Réglages d'environnement à vérifier

**Recherche Dataverse activée** — c'est le prérequis le plus souvent oublié. Une liste SharePoint utilisée comme source de Knowledge s'appuie sur la recherche Dataverse de l'environnement. Si elle est désactivée, la source se connectera mais ne rendra rien, et le symptôme ressemblera à une erreur de configuration de l'agent. **[À VÉRIFIER]**

> Power Platform admin center > **Environnements** > votre environnement > **Paramètres** > **Produit** > **Fonctionnalités** > vérifier que la **recherche Dataverse** est activée.

**Modèles disponibles** — la sélection de modèle se fait par agent. Ce projet exclut les modèles Anthropic **[CHOIX PROJET]** ; vous n'aurez donc besoin d'aucune activation de locataire particulière. Vérifiez simplement que des modèles OpenAI/Microsoft apparaissent dans le sélecteur à l'étape 02.

**Environnement de développement séparé** — ne construisez pas dans l'environnement qui héberge l'agent actuellement en service. L'agent actuel doit continuer à tourner pendant toute la construction ; la bascule est traitée à l'étape 07.

## 3. Facturation : à lire avant de commencer, pas après

Les agents propulsés par le harness GitHub Copilot sont facturés **à l'usage, en Copilot Credits**, et cette facturation **commence dès la construction** : chaque test dans l'onglet Preview et chaque exécution d'évaluation consomme des crédits, **même si votre organisation dispose de licences Microsoft 365 Copilot**. **[OFFICIEL]**

Conséquences pratiques :

- Prévoyez l'allocation de crédits **avant** l'étape 02, sinon vous serez bloqué en plein développement.
- Les tests répétés de l'étape 06 (évaluation) sont la principale source de consommation en phase de projet.
- Le détail de la gouvernance est dans `08_02_gouvernance-des-credits.md`. Vous pouvez ne le lire qu'à l'étape 08, mais **l'allocation doit exister maintenant**.

## 4. Ce que vous devez récupérer sur l'existant

Vous n'avez pas besoin de migrer quoi que ce soit — le nouvel agent se construit à neuf, et aucune conversion entre expériences n'existe dans un sens ni dans l'autre **[OFFICIEL]**. Vous avez seulement besoin de trois informations :

1. **L'URL exacte de la liste** `KPIDictionary` (site `ReportingTower10`).
2. **Les libellés exacts des 12 colonnes métier**, y compris `MyBI  Field name - EN` qui contient un **double espace** dans son libellé. Ce détail compte pour l'étape 03.
3. **Les cas de test métier** que l'agent actuel réussit, pour ne pas régresser. Ils sont déjà repris dans `06_02`.

Tout le reste de l'agent actuel — instructions, description d'outil, flux, topics — n'est **pas** à reprendre. C'est un choix : reproduire l'ancienne architecture sous une autre forme est précisément ce que ce projet évite.

## 5. Ce qui n'est PAS un prérequis

Pour éviter les préparatifs inutiles : ni licence Power Automate, ni connecteur personnalisé, ni serveur MCP, ni environnement Azure, ni compétence Python. Cette architecture n'en utilise aucun.

## Critères de fin d'étape

- [ ] J'accède à Copilot Studio dans l'environnement cible avec le rôle Maker.
- [ ] J'ouvre la liste `KPIDictionary` dans SharePoint.
- [ ] La recherche Dataverse est activée sur l'environnement (ou son activation est demandée).
- [ ] Une allocation de Copilot Credits existe pour cet environnement.
- [ ] J'ai noté l'URL de la liste et les libellés exacts des colonnes.
