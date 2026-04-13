"""
Définition et exécution des outils MCP pour l'agent Mesoutils.
Chaque outil est défini au format OpenAI function-calling et possède
un exécuteur Python correspondant.
"""
import os
import json
import requests
from datetime import datetime

PAPPERS_API_KEY = os.getenv("PAPPERS_API_KEY", "")
PAPPERS_BASE_URL = "https://api.pappers.fr/v2"


# ---------------------------------------------------------------------------
# Définitions des outils (format OpenAI tool/function calling)
# ---------------------------------------------------------------------------

TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "pappers_rechercher_entreprise",
            "description": (
                "Recherche des entreprises françaises par nom, SIREN ou SIRET via l'API Pappers. "
                "Retourne la liste des résultats avec raison sociale, SIREN, forme juridique, "
                "adresse, code NAF et statut."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Terme de recherche : nom d'entreprise, SIREN (9 chiffres) ou SIRET (14 chiffres)."
                    },
                    "par_page": {
                        "type": "integer",
                        "description": "Nombre de résultats par page (défaut : 5, max : 20).",
                        "default": 5
                    }
                },
                "required": ["q"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pappers_fiche_entreprise",
            "description": (
                "Récupère la fiche complète d'une entreprise française à partir de son SIREN. "
                "Retourne les informations détaillées : dirigeants, établissements, capital social, "
                "bénéficiaires effectifs, procédures collectives et données financières publiques."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "siren": {
                        "type": "string",
                        "description": "Numéro SIREN de l'entreprise (9 chiffres, sans espaces)."
                    }
                },
                "required": ["siren"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pappers_dirigeants",
            "description": (
                "Récupère la liste des dirigeants actuels et anciens d'une entreprise via son SIREN. "
                "Inclut nom, prénom, fonction, date de naissance et mandats."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "siren": {
                        "type": "string",
                        "description": "Numéro SIREN de l'entreprise (9 chiffres)."
                    }
                },
                "required": ["siren"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pappers_comptes_annuels",
            "description": (
                "Récupère les comptes annuels déposés publiquement pour une entreprise (SIREN). "
                "Retourne les bilans, comptes de résultat et annexes disponibles avec leurs dates de dépôt."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "siren": {
                        "type": "string",
                        "description": "Numéro SIREN de l'entreprise (9 chiffres)."
                    }
                },
                "required": ["siren"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_tva",
            "description": (
                "Calcule la TVA sur un montant HT ou TTC. "
                "Supporte les taux français standards (20%, 10%, 5.5%, 2.1%)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "montant": {
                        "type": "number",
                        "description": "Montant sur lequel calculer la TVA."
                    },
                    "taux": {
                        "type": "number",
                        "description": "Taux de TVA en pourcentage (ex: 20 pour 20%). Défaut : 20.",
                        "default": 20
                    },
                    "sens": {
                        "type": "string",
                        "enum": ["ht_vers_ttc", "ttc_vers_ht"],
                        "description": "Direction du calcul : 'ht_vers_ttc' (défaut) ou 'ttc_vers_ht'.",
                        "default": "ht_vers_ttc"
                    }
                },
                "required": ["montant"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_is",
            "description": (
                "Calcule l'Impôt sur les Sociétés (IS) estimé selon le barème français en vigueur. "
                "Taux réduit PME à 15% jusqu'à 42 500€, puis 25% au-delà."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "resultat_fiscal": {
                        "type": "number",
                        "description": "Résultat fiscal imposable en euros."
                    },
                    "est_pme": {
                        "type": "boolean",
                        "description": "True si l'entreprise qualifie comme PME pour le taux réduit (CA < 10M€, capital détenu à 75% par des personnes physiques). Défaut : True.",
                        "default": True
                    }
                },
                "required": ["resultat_fiscal"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "info_date_echeance",
            "description": (
                "Donne les prochaines échéances fiscales et sociales importantes pour une entreprise française. "
                "Utile pour planifier les déclarations TVA, IS, cotisations URSSAF, DSN, etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "regime_tva": {
                        "type": "string",
                        "enum": ["reel_normal", "reel_simplifie", "franchise"],
                        "description": "Régime TVA de l'entreprise. Défaut : reel_normal.",
                        "default": "reel_normal"
                    },
                    "forme_juridique": {
                        "type": "string",
                        "description": "Forme juridique de l'entreprise (ex: SAS, SARL, SA, EI). Défaut : SAS.",
                        "default": "SAS"
                    }
                },
                "required": []
            }
        }
    }
]


# ---------------------------------------------------------------------------
# Exécuteurs des outils
# ---------------------------------------------------------------------------

def _pappers_get(endpoint: str, params: dict) -> dict:
    """Helper pour appeler l'API Pappers avec gestion d'erreurs."""
    if not PAPPERS_API_KEY:
        return {"erreur": "Clé API Pappers non configurée (variable PAPPERS_API_KEY manquante)."}
    params["api_token"] = PAPPERS_API_KEY
    try:
        response = requests.get(
            f"{PAPPERS_BASE_URL}/{endpoint}",
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"erreur": "Clé API Pappers invalide ou expirée."}
        elif response.status_code == 429:
            return {"erreur": "Quota API Pappers dépassé. Réessayez plus tard."}
        else:
            return {"erreur": f"Erreur API Pappers : statut HTTP {response.status_code}", "détail": response.text[:200]}
    except requests.exceptions.Timeout:
        return {"erreur": "Timeout lors de l'appel à l'API Pappers (>10s)."}
    except Exception as e:
        return {"erreur": f"Erreur inattendue lors de l'appel à Pappers : {str(e)}"}


def exec_pappers_rechercher_entreprise(q: str, par_page: int = 5) -> dict:
    par_page = min(max(1, par_page), 20)
    result = _pappers_get("recherche", {"q": q, "par_page": par_page})
    if "erreur" in result:
        return result
    entreprises = result.get("resultats", [])
    simplifie = []
    for e in entreprises:
        simplifie.append({
            "siren": e.get("siren"),
            "siret_siege": e.get("siret_siege"),
            "raison_sociale": e.get("nom_entreprise") or e.get("denomination"),
            "forme_juridique": e.get("forme_juridique"),
            "code_naf": e.get("code_naf"),
            "libelle_naf": e.get("libelle_code_naf"),
            "adresse": e.get("siege", {}).get("adresse_ligne_1"),
            "ville": e.get("siege", {}).get("ville"),
            "code_postal": e.get("siege", {}).get("code_postal"),
            "statut": "Actif" if not e.get("date_radiation") else f"Radié le {e.get('date_radiation')}",
            "date_creation": e.get("date_creation"),
            "capital": e.get("capital"),
            "devise_capital": e.get("devise_capital"),
        })
    return {
        "total": result.get("total", len(simplifie)),
        "page": result.get("page", 1),
        "resultats": simplifie
    }


def exec_pappers_fiche_entreprise(siren: str) -> dict:
    siren = siren.replace(" ", "").replace("-", "")
    result = _pappers_get("entreprise", {
        "siren": siren,
        "extrait_court": True,
        "dirigeants": True,
        "beneficiaires": True,
        "finances": True,
        "procedures_collectives": True,
    })
    if "erreur" in result:
        return result
    return {
        "siren": result.get("siren"),
        "denomination": result.get("denomination") or result.get("nom_entreprise"),
        "forme_juridique": result.get("forme_juridique"),
        "capital_social": result.get("capital"),
        "devise_capital": result.get("devise_capital"),
        "date_creation": result.get("date_creation"),
        "date_radiation": result.get("date_radiation"),
        "statut": "Actif" if not result.get("date_radiation") else f"Radié le {result.get('date_radiation')}",
        "code_naf": result.get("code_naf"),
        "libelle_naf": result.get("libelle_code_naf"),
        "tranche_effectif": result.get("tranche_effectif"),
        "adresse_siege": {
            "adresse": result.get("siege", {}).get("adresse_ligne_1"),
            "code_postal": result.get("siege", {}).get("code_postal"),
            "ville": result.get("siege", {}).get("ville"),
        },
        "nombre_etablissements_ouverts": result.get("nombre_etablissements_ouverts"),
        "dirigeants": [
            {
                "nom": d.get("nom"),
                "prenom": d.get("prenom"),
                "fonction": d.get("qualite"),
                "date_naissance": d.get("date_naissance_formate"),
            }
            for d in result.get("dirigeants", [])[:10]
        ],
        "beneficiaires_effectifs": [
            {
                "nom": b.get("nom"),
                "prenom": b.get("prenom"),
                "pourcentage_parts": b.get("pourcentage_parts"),
            }
            for b in result.get("beneficiaires_effectifs", [])
        ],
        "procedures_collectives": result.get("procedures_collectives", []),
        "chiffre_affaires_dernier": (
            result.get("finances", [{}])[0].get("chiffre_affaires")
            if result.get("finances") else None
        ),
        "resultat_dernier": (
            result.get("finances", [{}])[0].get("resultat")
            if result.get("finances") else None
        ),
        "annee_finances": (
            result.get("finances", [{}])[0].get("annee")
            if result.get("finances") else None
        ),
    }


def exec_pappers_dirigeants(siren: str) -> dict:
    siren = siren.replace(" ", "").replace("-", "")
    result = _pappers_get("entreprise", {"siren": siren, "dirigeants": True})
    if "erreur" in result:
        return result
    return {
        "siren": siren,
        "denomination": result.get("denomination") or result.get("nom_entreprise"),
        "dirigeants": result.get("dirigeants", [])
    }


def exec_pappers_comptes_annuels(siren: str) -> dict:
    siren = siren.replace(" ", "").replace("-", "")
    result = _pappers_get("entreprise", {"siren": siren, "finances": True, "comptes_annuels": True})
    if "erreur" in result:
        return result
    return {
        "siren": siren,
        "denomination": result.get("denomination") or result.get("nom_entreprise"),
        "finances": result.get("finances", []),
        "comptes_annuels": result.get("comptes_annuels", [])
    }


def exec_calculer_tva(montant: float, taux: float = 20.0, sens: str = "ht_vers_ttc") -> dict:
    taux_decimal = taux / 100.0
    if sens == "ht_vers_ttc":
        tva = montant * taux_decimal
        ttc = montant + tva
        return {
            "montant_ht": round(montant, 2),
            "taux_tva": f"{taux}%",
            "montant_tva": round(tva, 2),
            "montant_ttc": round(ttc, 2),
            "formule": f"{montant} HT × {1 + taux_decimal} = {round(ttc, 2)} TTC"
        }
    else:
        ht = montant / (1 + taux_decimal)
        tva = montant - ht
        return {
            "montant_ttc": round(montant, 2),
            "taux_tva": f"{taux}%",
            "montant_tva": round(tva, 2),
            "montant_ht": round(ht, 2),
            "formule": f"{montant} TTC ÷ {1 + taux_decimal} = {round(ht, 2)} HT"
        }


def exec_calculer_is(resultat_fiscal: float, est_pme: bool = True) -> dict:
    if resultat_fiscal <= 0:
        return {
            "resultat_fiscal": round(resultat_fiscal, 2),
            "is_estime": 0.0,
            "detail": "Pas d'IS dû (résultat fiscal nul ou déficitaire).",
            "report_deficit": round(abs(resultat_fiscal), 2) if resultat_fiscal < 0 else 0
        }

    SEUIL_PME = 42500.0
    TAUX_REDUIT = 0.15
    TAUX_NORMAL = 0.25

    if est_pme and resultat_fiscal <= SEUIL_PME:
        is_calcule = resultat_fiscal * TAUX_REDUIT
        detail = f"{resultat_fiscal:,.2f}€ × 15% (taux réduit PME) = {is_calcule:,.2f}€"
    elif est_pme and resultat_fiscal > SEUIL_PME:
        is_tranche1 = SEUIL_PME * TAUX_REDUIT
        is_tranche2 = (resultat_fiscal - SEUIL_PME) * TAUX_NORMAL
        is_calcule = is_tranche1 + is_tranche2
        detail = (
            f"Tranche 1 : 42 500€ × 15% = {is_tranche1:,.2f}€\n"
            f"Tranche 2 : {(resultat_fiscal - SEUIL_PME):,.2f}€ × 25% = {is_tranche2:,.2f}€\n"
            f"Total IS : {is_calcule:,.2f}€"
        )
    else:
        is_calcule = resultat_fiscal * TAUX_NORMAL
        detail = f"{resultat_fiscal:,.2f}€ × 25% (taux normal) = {is_calcule:,.2f}€"

    return {
        "resultat_fiscal": round(resultat_fiscal, 2),
        "is_estime": round(is_calcule, 2),
        "taux_effectif": round(is_calcule / resultat_fiscal * 100, 2),
        "detail": detail,
        "resultat_net_apres_is": round(resultat_fiscal - is_calcule, 2),
        "note": "Estimation basée sur le barème IS 2024-2026. Consultez un expert-comptable pour validation."
    }


def exec_info_date_echeance(regime_tva: str = "reel_normal", forme_juridique: str = "SAS") -> dict:
    today = datetime.now()
    month = today.month
    year = today.year

    echeances = {
        "date_actuelle": today.strftime("%d/%m/%Y"),
        "regime_tva": regime_tva,
        "forme_juridique": forme_juridique,
        "prochaines_echeances": []
    }

    if regime_tva == "reel_normal":
        echeances["prochaines_echeances"].append({
            "libelle": "Déclaration TVA CA3 mensuelle",
            "periodicite": "Mensuelle (au plus tard le 19 ou 24 du mois suivant)",
            "description": "Déclaration et paiement de la TVA collectée moins TVA déductible."
        })
    elif regime_tva == "reel_simplifie":
        echeances["prochaines_echeances"].append({
            "libelle": "Acomptes TVA CA12",
            "periodicite": "Semestriel (55% en juillet, 40% en décembre)",
            "description": "Acomptes basés sur la TVA due l'année précédente."
        })

    echeances["prochaines_echeances"].extend([
        {
            "libelle": "Déclaration IS (formulaire 2065)",
            "periodicite": "Annuelle - dans les 3 mois suivant la clôture (ou 2e jour ouvré de mai si clôture 31/12)",
            "description": "Déclaration du résultat fiscal et calcul de l'IS dû."
        },
        {
            "libelle": "Acomptes IS",
            "periodicite": "Trimestriel (15 mars, 15 juin, 15 sept., 15 déc.)",
            "description": "4 acomptes de 25% chacun basés sur l'IS de l'exercice précédent (si IS > 3 000€)."
        },
        {
            "libelle": "DSN (Déclaration Sociale Nominative)",
            "periodicite": "Mensuelle (5 ou 15 du mois M+1 selon effectif)",
            "description": "Déclaration des données sociales des salariés à l'URSSAF."
        },
        {
            "libelle": "Dépôt des comptes annuels au greffe",
            "periodicite": f"Dans les 6 mois suivant la clôture de l'exercice (pour {forme_juridique})",
            "description": "Dépôt du bilan, compte de résultat et annexe au Tribunal de Commerce."
        },
        {
            "libelle": "CFE (Cotisation Foncière des Entreprises)",
            "periodicite": "Annuelle - 15 décembre (ou mensuel si > 3 000€)",
            "description": "Impôt local basé sur la valeur locative des biens utilisés."
        }
    ])

    return echeances


# ---------------------------------------------------------------------------
# Registre des exécuteurs
# ---------------------------------------------------------------------------

TOOL_EXECUTORS = {
    "pappers_rechercher_entreprise": lambda args: exec_pappers_rechercher_entreprise(
        q=args["q"], par_page=args.get("par_page", 5)
    ),
    "pappers_fiche_entreprise": lambda args: exec_pappers_fiche_entreprise(
        siren=args["siren"]
    ),
    "pappers_dirigeants": lambda args: exec_pappers_dirigeants(
        siren=args["siren"]
    ),
    "pappers_comptes_annuels": lambda args: exec_pappers_comptes_annuels(
        siren=args["siren"]
    ),
    "calculer_tva": lambda args: exec_calculer_tva(
        montant=args["montant"],
        taux=args.get("taux", 20.0),
        sens=args.get("sens", "ht_vers_ttc")
    ),
    "calculer_is": lambda args: exec_calculer_is(
        resultat_fiscal=args["resultat_fiscal"],
        est_pme=args.get("est_pme", True)
    ),
    "info_date_echeance": lambda args: exec_info_date_echeance(
        regime_tva=args.get("regime_tva", "reel_normal"),
        forme_juridique=args.get("forme_juridique", "SAS")
    ),
}


def execute_tool(name: str, arguments: dict) -> dict:
    """Exécute un outil par son nom et retourne le résultat."""
    executor = TOOL_EXECUTORS.get(name)
    if not executor:
        return {"erreur": f"Outil inconnu : {name}"}
    try:
        return executor(arguments)
    except Exception as e:
        return {"erreur": f"Erreur lors de l'exécution de l'outil {name} : {str(e)}"}
