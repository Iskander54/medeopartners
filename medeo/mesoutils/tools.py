"""
Définition et exécution des outils MCP pour l'agent Mesoutils.
Chaque outil est défini au format OpenAI function-calling et possède
un exécuteur Python correspondant.
"""
import os
import json
import requests
from datetime import datetime

PAPPERS_API_KEY    = os.getenv("PAPPERS_API_KEY", "")
PAPPERS_BASE_URL   = "https://api.pappers.fr/v2"
ANNUAIRE_BASE_URL  = "https://recherche-entreprises.api.gouv.fr"
BODACC_API_URL     = "https://bodacc.fr/api/explore/v2.1/catalog/datasets/annonces-commerciales/records"
VIES_API_URL       = "https://ec.europa.eu/taxation_customs/vies/rest-api/check-vat-number"

# ---------------------------------------------------------------------------
# Barèmes fiscaux et sociaux 2025 / 2026
# Sources : DGFiP, URSSAF, Légifrance, Journal Officiel
# ---------------------------------------------------------------------------
BAREME = {
    # Plafond Annuel Sécurité Sociale
    "pass_2024": 46368,
    "pass_2025": 47100,
    # SMIC
    "smic_horaire_brut_2025": 11.88,
    "smic_mensuel_brut_2025": 1801.80,
    "smic_annuel_brut_2025": 21621.60,
    # Taux d'intérêt légal (Banque de France, art. L313-2 CMF)
    "taux_interet_legal_pro_s1_2025": 4.92,     # % professionnel S1 2025
    "taux_interet_legal_conso_s1_2025": 7.07,   # % consommateur S1 2025
    # Pénalités de retard B2B (art. L441-10 C.com.)
    "indemnite_forfaitaire_recouvrement": 40,    # € forfait
    # Plafonds régimes micro (CA HT annuel)
    "micro_bic_ventes_2025": 188700,
    "micro_bic_services_2025": 77700,
    "micro_bnc_2025": 77700,
    # Abattements micro
    "micro_bic_ventes_abattement": 71,    # %
    "micro_bic_services_abattement": 50,  # %
    "micro_bnc_abattement": 34,           # %
    # IS
    "is_taux_reduit_pct": 15,
    "is_seuil_taux_reduit": 42500,
    "is_taux_normal_pct": 25,
    # Tranches IR 2025 (revenus 2024)
    "ir_tranches": [
        {"min": 0,      "max": 11294,  "taux": 0},
        {"min": 11294,  "max": 28797,  "taux": 11},
        {"min": 28797,  "max": 82341,  "taux": 30},
        {"min": 82341,  "max": 177106, "taux": 41},
        {"min": 177106, "max": None,   "taux": 45},
    ],
    # Cotisations TNS (SSI / ex-RSI) — gérant majoritaire SARL / EI
    "tns_maladie_taux_1": 6.50,         # % sur totalité revenu
    "tns_ij_taux": 0.85,                # % plafonné à 1 PASS
    "tns_retraite_base_taux_1pass": 17.75,  # % jusqu'à 1 PASS
    "tns_retraite_base_taux_sup":   0.60,   # % au-delà de 1 PASS
    "tns_retraite_compl_taux_4pass": 7.00,  # % de 0 à 4 PASS
    "tns_retraite_compl_taux_8pass": 8.00,  # % de 4 à 8 PASS
    "tns_invalidite_deces_taux": 1.30,      # % plafonné à 1 PASS
    "tns_csg_crds_taux": 9.70,              # % sur assiette élargie
    "tns_formation_taux": 0.25,             # %
    "tns_assiette_minimale_annee": 4710,    # € (10% du PASS)
}


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
            "name": "bodacc_annonces",
            "description": (
                "Recherche les annonces légales publiées au BODACC (Bulletin Officiel des Annonces Civiles et Commerciales) "
                "pour une entreprise française. Permet de détecter les procédures collectives (redressement, liquidation), "
                "jugements, radiations, cessions de fonds de commerce et modifications importantes. "
                "Très utile pour la due diligence client avant toute mission."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "siren": {
                        "type": "string",
                        "description": "Numéro SIREN de l'entreprise (9 chiffres) ou raison sociale."
                    },
                    "nb_annonces": {
                        "type": "integer",
                        "description": "Nombre d'annonces à retourner (défaut : 5, max : 20).",
                        "default": 5
                    }
                },
                "required": ["siren"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "valider_tva_vies",
            "description": (
                "Valide un numéro de TVA intracommunautaire via le système VIES de la Commission Européenne. "
                "Retourne la validité du numéro, le nom et l'adresse de l'entreprise enregistrée. "
                "Indispensable avant toute facturation intra-UE en exonération de TVA."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code_pays": {
                        "type": "string",
                        "description": "Code pays ISO 2 lettres (ex: FR, DE, ES, IT, BE, NL...)."
                    },
                    "numero_tva": {
                        "type": "string",
                        "description": "Numéro TVA sans le code pays (ex: pour FR12345678901 → '12345678901')."
                    }
                },
                "required": ["code_pays", "numero_tva"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "baremes_fiscaux_sociaux",
            "description": (
                "Retourne les principaux barèmes fiscaux et sociaux français en vigueur (2025/2026) : "
                "PASS, SMIC, plafonds régimes micro (BIC/BNC), tranches IR, taux IS, "
                "taux d'intérêt légal, indemnité forfaitaire de recouvrement, taux cotisations TNS."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "categorie": {
                        "type": "string",
                        "enum": ["tout", "social", "fiscal", "micro", "taux"],
                        "description": "Filtrer par catégorie. 'tout' retourne toutes les données (défaut).",
                        "default": "tout"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_cotisations_tns",
            "description": (
                "Calcule les cotisations sociales obligatoires d'un travailleur non salarié (TNS) : "
                "gérant majoritaire de SARL, entrepreneur individuel, professionnel libéral affilié SSI. "
                "Inclut : maladie, retraite de base, retraite complémentaire, invalidité-décès, CSG/CRDS, formation. "
                "Résultat indicatif — à valider avec l'URSSAF et un expert-comptable."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "revenu_net": {
                        "type": "number",
                        "description": "Revenu professionnel net annuel en euros (avant cotisations sociales, hors CSG non déductible)."
                    },
                    "annee": {
                        "type": "integer",
                        "description": "Année de référence pour les barèmes (défaut : 2025).",
                        "default": 2025
                    }
                },
                "required": ["revenu_net"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_penalites_retard",
            "description": (
                "Calcule les pénalités de retard de paiement applicables entre professionnels (B2B) "
                "conformément à l'article L441-10 du Code de commerce. "
                "Inclut : pénalités au taux légal (minimum 3× taux BCE), indemnité forfaitaire de 40€, "
                "et le total réclamable. À mentionner sur les CGV et les factures."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "montant_ht": {
                        "type": "number",
                        "description": "Montant HT de la facture impayée en euros."
                    },
                    "date_echeance": {
                        "type": "string",
                        "description": "Date d'échéance de la facture au format YYYY-MM-DD ou DD/MM/YYYY."
                    },
                    "date_paiement": {
                        "type": "string",
                        "description": "Date de paiement réel (ou date du jour si toujours impayée) au format YYYY-MM-DD ou DD/MM/YYYY."
                    },
                    "taux_tva": {
                        "type": "number",
                        "description": "Taux de TVA applicable en % (défaut : 20).",
                        "default": 20
                    }
                },
                "required": ["montant_ht", "date_echeance", "date_paiement"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_tva_intracommunautaire",
            "description": (
                "Calcule le numéro de TVA intracommunautaire français d'une entreprise à partir de son SIREN. "
                "Formule officielle : FR + clé (2 chiffres) + SIREN (9 chiffres). "
                "Utilise cet outil dès qu'on te demande le numéro TVA d'une entreprise et que tu as son SIREN."
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

def _calculer_cle_tva(siren: str) -> str:
    """Calcule la clé de contrôle du numéro TVA intracommunautaire français."""
    cle = (12 + 3 * (int(siren) % 97)) % 97
    return f"{cle:02d}"


def _annuaire_rechercher(q: str, par_page: int = 5) -> dict:
    """
    Fallback gratuit : API Annuaire Entreprises (data.gouv.fr).
    Aucune clé API requise.
    """
    try:
        response = requests.get(
            f"{ANNUAIRE_BASE_URL}/search",
            params={"q": q, "per_page": min(par_page, 20)},
            timeout=10,
        )
        if response.status_code != 200:
            return {"erreur": f"API Annuaire Entreprises indisponible (HTTP {response.status_code})."}
        data = response.json()
        resultats = []
        for e in data.get("results", []):
            siege = e.get("siege", {})
            siren = e.get("siren", "")
            resultats.append({
                "siren": siren,
                "siret_siege": siege.get("siret"),
                "raison_sociale": e.get("nom_complet"),
                "forme_juridique": e.get("nature_juridique"),
                "code_naf": siege.get("activite_principale"),
                "adresse": siege.get("adresse"),
                "ville": siege.get("libelle_commune"),
                "code_postal": siege.get("code_postal"),
                "statut": "Actif" if e.get("etat_administratif") == "A" else "Cessé",
                "date_creation": e.get("date_creation"),
                "tva_intracommunautaire": (
                    f"FR{_calculer_cle_tva(siren)}{siren}" if siren else None
                ),
                "source": "annuaire-entreprises.data.gouv.fr",
            })
        return {
            "total": data.get("total_results", len(resultats)),
            "resultats": resultats,
            "source": "annuaire-entreprises.data.gouv.fr",
        }
    except requests.exceptions.Timeout:
        return {"erreur": "Timeout API Annuaire Entreprises (>10s)."}
    except Exception as e:
        return {"erreur": f"Erreur API Annuaire Entreprises : {str(e)}"}


def _annuaire_fiche(siren: str) -> dict:
    """Récupère la fiche d'une entreprise via l'API Annuaire Entreprises."""
    try:
        response = requests.get(
            f"{ANNUAIRE_BASE_URL}/search",
            params={"q": siren, "per_page": 1},
            timeout=10,
        )
        if response.status_code != 200:
            return {"erreur": f"API Annuaire Entreprises indisponible (HTTP {response.status_code})."}
        data = response.json()
        results = data.get("results", [])
        if not results:
            return {"erreur": f"Entreprise SIREN {siren} non trouvée dans l'Annuaire Entreprises."}
        e = results[0]
        siege = e.get("siege", {})
        siren_val = e.get("siren", siren)
        return {
            "siren": siren_val,
            "denomination": e.get("nom_complet"),
            "forme_juridique": e.get("nature_juridique"),
            "date_creation": e.get("date_creation"),
            "statut": "Actif" if e.get("etat_administratif") == "A" else "Cessé",
            "code_naf": siege.get("activite_principale"),
            "tranche_effectif": e.get("tranche_effectif_salarie"),
            "adresse_siege": {
                "adresse": siege.get("adresse"),
                "code_postal": siege.get("code_postal"),
                "ville": siege.get("libelle_commune"),
            },
            "tva_intracommunautaire": f"FR{_calculer_cle_tva(siren_val)}{siren_val}",
            "source": "annuaire-entreprises.data.gouv.fr",
        }
    except Exception as e:
        return {"erreur": f"Erreur API Annuaire Entreprises : {str(e)}"}


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
        # Fallback sur l'API Annuaire Entreprises (data.gouv.fr)
        fallback = _annuaire_rechercher(q, par_page)
        if "erreur" not in fallback:
            fallback["avertissement"] = f"Pappers indisponible ({result['erreur']}). Source : Annuaire Entreprises (data.gouv.fr)."
        return fallback

    entreprises = result.get("resultats", [])
    simplifie = []
    for e in entreprises:
        siren = e.get("siren", "")
        simplifie.append({
            "siren": siren,
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
            "tva_intracommunautaire": f"FR{_calculer_cle_tva(siren)}{siren}" if siren else None,
        })
    return {
        "total": result.get("total", len(simplifie)),
        "page": result.get("page", 1),
        "resultats": simplifie,
        "source": "pappers.fr",
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
        # Fallback sur l'API Annuaire Entreprises
        fallback = _annuaire_fiche(siren)
        if "erreur" not in fallback:
            fallback["avertissement"] = f"Pappers indisponible ({result['erreur']}). Source : Annuaire Entreprises (data.gouv.fr)."
        return fallback

    siren_val = result.get("siren", siren)
    return {
        "siren": siren_val,
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
        "tva_intracommunautaire": f"FR{_calculer_cle_tva(siren_val)}{siren_val}" if siren_val else None,
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
        "source": "pappers.fr",
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

def exec_bodacc_annonces(siren: str, nb_annonces: int = 5) -> dict:
    """Recherche les annonces BODACC pour un SIREN via l'API Opendatasoft."""
    nb_annonces = min(max(1, nb_annonces), 20)
    try:
        response = requests.get(
            BODACC_API_URL,
            params={
                "q": siren,
                "limit": nb_annonces,
                "order_by": "dateparution desc",
            },
            timeout=10,
        )
        if response.status_code != 200:
            return {"erreur": f"API BODACC indisponible (HTTP {response.status_code})."}

        data = response.json()
        records = data.get("results", [])
        if not records:
            return {
                "siren_recherche": siren,
                "total": 0,
                "annonces": [],
                "message": "Aucune annonce BODACC trouvée pour ce SIREN. L'entreprise n'a peut-être jamais publié au BODACC.",
            }

        annonces = []
        for r in records:
            contenu = r.get("contenu_blob") or {}
            if isinstance(contenu, str):
                try:
                    contenu = json.loads(contenu)
                except Exception:
                    contenu = {}
            annonces.append({
                "date_parution": r.get("dateparution"),
                "type_annonce": r.get("typeavis_lib"),
                "commercant": r.get("commercant"),
                "tribunal": r.get("tribunal"),
                "ville_rcs": r.get("ville"),
                "registre": r.get("registre"),
                "detail": contenu,
            })

        return {
            "siren_recherche": siren,
            "total_trouve": data.get("total_count", len(annonces)),
            "annonces": annonces,
            "source": "bodacc.fr",
        }
    except requests.exceptions.Timeout:
        return {"erreur": "Timeout API BODACC (>10s)."}
    except Exception as e:
        return {"erreur": f"Erreur API BODACC : {str(e)}"}


def exec_valider_tva_vies(code_pays: str, numero_tva: str) -> dict:
    """Valide un numéro TVA intracommunautaire via le système VIES (Commission Européenne)."""
    code_pays = code_pays.strip().upper()
    numero_tva = numero_tva.strip().upper().replace(" ", "")
    # Retirer le code pays si l'utilisateur l'a inclus dans le numéro
    if numero_tva.startswith(code_pays):
        numero_tva = numero_tva[len(code_pays):]
    try:
        response = requests.post(
            VIES_API_URL,
            json={"countryCode": code_pays, "vatNumber": numero_tva},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        if response.status_code != 200:
            return {
                "erreur": f"Service VIES indisponible (HTTP {response.status_code}). "
                          "Essayez sur https://ec.europa.eu/taxation_customs/vies/"
            }
        data = response.json()
        numero_complet = f"{code_pays}{numero_tva}"
        return {
            "numero_tva": numero_complet,
            "valide": data.get("valid", False),
            "nom_entreprise": data.get("traderName") or "(non communiqué par l'État membre)",
            "adresse": data.get("traderAddress") or "(non communiqué par l'État membre)",
            "pays": code_pays,
            "date_consultation": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "note": (
                "Numéro TVA valide — vous pouvez facturer en exonération de TVA (autoliquidation)."
                if data.get("valid")
                else "Numéro TVA invalide ou non enregistré dans VIES — appliquer la TVA du pays vendeur."
            ),
            "source": "VIES — Commission Européenne",
        }
    except requests.exceptions.Timeout:
        return {"erreur": "Timeout VIES (>15s). Le service peut être temporairement surchargé."}
    except Exception as e:
        return {"erreur": f"Erreur VIES : {str(e)}"}


def exec_baremes_fiscaux_sociaux(categorie: str = "tout") -> dict:
    """Retourne les barèmes fiscaux et sociaux 2025/2026."""
    social = {
        "PASS_2024": f"{BAREME['pass_2024']:,}€",
        "PASS_2025": f"{BAREME['pass_2025']:,}€",
        "SMIC_horaire_brut_2025": f"{BAREME['smic_horaire_brut_2025']}€",
        "SMIC_mensuel_brut_2025": f"{BAREME['smic_mensuel_brut_2025']}€",
        "SMIC_annuel_brut_2025": f"{BAREME['smic_annuel_brut_2025']:,}€",
        "taux_interet_legal_professionnel_S1_2025": f"{BAREME['taux_interet_legal_pro_s1_2025']}%",
        "taux_interet_legal_consommateur_S1_2025": f"{BAREME['taux_interet_legal_conso_s1_2025']}%",
        "indemnite_forfaitaire_recouvrement": f"{BAREME['indemnite_forfaitaire_recouvrement']}€",
    }
    fiscal = {
        "IS_taux_reduit_PME": f"{BAREME['is_taux_reduit_pct']}% (jusqu'à {BAREME['is_seuil_taux_reduit']:,}€)",
        "IS_taux_normal": f"{BAREME['is_taux_normal_pct']}%",
        "tranches_IR_2025": [
            f"{t['taux']}% de {t['min']:,}€ à {str(t['max']) + '€' if t['max'] else '∞'}"
            for t in BAREME["ir_tranches"]
        ],
    }
    micro = {
        "micro_BIC_ventes_plafond_2025": f"{BAREME['micro_bic_ventes_2025']:,}€ (abattement {BAREME['micro_bic_ventes_abattement']}%)",
        "micro_BIC_services_plafond_2025": f"{BAREME['micro_bic_services_2025']:,}€ (abattement {BAREME['micro_bic_services_abattement']}%)",
        "micro_BNC_plafond_2025": f"{BAREME['micro_bnc_2025']:,}€ (abattement {BAREME['micro_bnc_abattement']}%)",
    }
    taux_cotisations = {
        "maladie": f"{BAREME['tns_maladie_taux_1']}% (totalité revenu)",
        "indemnites_journalieres": f"{BAREME['tns_ij_taux']}% (plafonné à 1 PASS)",
        "retraite_base_jusqu_1pass": f"{BAREME['tns_retraite_base_taux_1pass']}%",
        "retraite_base_au_dela_1pass": f"{BAREME['tns_retraite_base_taux_sup']}%",
        "retraite_complementaire_0_4pass": f"{BAREME['tns_retraite_compl_taux_4pass']}%",
        "retraite_complementaire_4_8pass": f"{BAREME['tns_retraite_compl_taux_8pass']}%",
        "invalidite_deces": f"{BAREME['tns_invalidite_deces_taux']}% (plafonné à 1 PASS)",
        "CSG_CRDS": f"{BAREME['tns_csg_crds_taux']}% (assiette élargie)",
        "formation_professionnelle": f"{BAREME['tns_formation_taux']}%",
    }

    result: dict = {"annee_reference": "2025/2026", "source": "DGFiP, URSSAF, Légifrance"}
    if categorie in ("tout", "social"):
        result["social"] = social
    if categorie in ("tout", "fiscal"):
        result["fiscal"] = fiscal
    if categorie in ("tout", "micro"):
        result["regimes_micro"] = micro
    if categorie in ("tout", "taux"):
        result["taux_cotisations_tns"] = taux_cotisations
    return result


def exec_calculer_cotisations_tns(revenu_net: float, annee: int = 2025) -> dict:
    """
    Calcule les cotisations SSI (ex-RSI) pour un TNS (gérant majoritaire SARL ou EI).
    Méthode : cotisations calculées sur le revenu net (N-2 en régime définitif,
    approximation sur revenu N pour simulation).
    """
    pass_val = BAREME["pass_2025"] if annee >= 2025 else BAREME["pass_2024"]
    revenu = max(revenu_net, BAREME["tns_assiette_minimale_annee"])

    # Maladie-maternité
    maladie = revenu * BAREME["tns_maladie_taux_1"] / 100

    # Indemnités journalières
    assiette_ij = min(revenu, pass_val)
    ij = assiette_ij * BAREME["tns_ij_taux"] / 100

    # Retraite de base
    if revenu <= pass_val:
        retraite_base = revenu * BAREME["tns_retraite_base_taux_1pass"] / 100
    else:
        retraite_base = (
            pass_val * BAREME["tns_retraite_base_taux_1pass"] / 100
            + (revenu - pass_val) * BAREME["tns_retraite_base_taux_sup"] / 100
        )

    # Retraite complémentaire (en points, simplifié en €)
    if revenu <= 4 * pass_val:
        retraite_compl = revenu * BAREME["tns_retraite_compl_taux_4pass"] / 100
    elif revenu <= 8 * pass_val:
        retraite_compl = (
            4 * pass_val * BAREME["tns_retraite_compl_taux_4pass"] / 100
            + (revenu - 4 * pass_val) * BAREME["tns_retraite_compl_taux_8pass"] / 100
        )
    else:
        retraite_compl = (
            4 * pass_val * BAREME["tns_retraite_compl_taux_4pass"] / 100
            + 4 * pass_val * BAREME["tns_retraite_compl_taux_8pass"] / 100
        )

    # Invalidité-décès
    assiette_inv = min(revenu, pass_val)
    invalidite = assiette_inv * BAREME["tns_invalidite_deces_taux"] / 100

    # Formation professionnelle
    formation = pass_val * BAREME["tns_formation_taux"] / 100

    # Sous-total hors CSG/CRDS
    sous_total = maladie + ij + retraite_base + retraite_compl + invalidite + formation

    # CSG/CRDS : assiette = revenu + cotisations obligatoires (hors CSG) × 98%
    assiette_csg = (revenu + sous_total) * 0.98
    csg_crds = assiette_csg * BAREME["tns_csg_crds_taux"] / 100

    total = sous_total + csg_crds
    taux_effectif = round(total / revenu_net * 100, 1) if revenu_net > 0 else 0

    return {
        "revenu_net_base": round(revenu_net, 2),
        "pass_utilise": pass_val,
        "detail_cotisations": {
            "maladie_maternite": round(maladie, 2),
            "indemnites_journalieres": round(ij, 2),
            "retraite_base": round(retraite_base, 2),
            "retraite_complementaire": round(retraite_compl, 2),
            "invalidite_deces": round(invalidite, 2),
            "formation_professionnelle": round(formation, 2),
            "CSG_CRDS": round(csg_crds, 2),
        },
        "total_cotisations": round(total, 2),
        "taux_effectif_global": f"{taux_effectif}%",
        "revenu_disponible_estime": round(revenu_net - total, 2),
        "note": (
            "Simulation indicative SSI 2025 (gérant maj. SARL / EI). "
            "Les cotisations réelles sont calculées sur le revenu N-2 avec régularisation N. "
            "Valider avec votre URSSAF et un expert-comptable."
        ),
    }


def exec_calculer_penalites_retard(
    montant_ht: float,
    date_echeance: str,
    date_paiement: str,
    taux_tva: float = 20.0,
) -> dict:
    """Calcule les pénalités de retard B2B (art. L441-10 C.com.)."""
    def _parse_date(s: str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(s.strip(), fmt)
            except ValueError:
                continue
        raise ValueError(f"Format de date non reconnu : '{s}'. Utilisez YYYY-MM-DD ou DD/MM/YYYY.")

    try:
        d_echeance  = _parse_date(date_echeance)
        d_paiement  = _parse_date(date_paiement)
    except ValueError as e:
        return {"erreur": str(e)}

    if d_paiement <= d_echeance:
        return {
            "montant_ht": montant_ht,
            "jours_retard": 0,
            "penalites": 0.0,
            "indemnite_forfaitaire": 0.0,
            "total_reclamable": 0.0,
            "message": "Aucun retard : la date de paiement est antérieure ou égale à l'échéance.",
        }

    jours_retard = (d_paiement - d_echeance).days
    montant_ttc  = montant_ht * (1 + taux_tva / 100)

    # Taux minimum légal B2B = 3 fois le taux d'intérêt légal professionnel
    taux_annuel = BAREME["taux_interet_legal_pro_s1_2025"] * 3
    penalites   = montant_ttc * (taux_annuel / 100) * (jours_retard / 365)
    forfait     = BAREME["indemnite_forfaitaire_recouvrement"]
    total       = penalites + forfait

    return {
        "montant_ht": round(montant_ht, 2),
        "montant_ttc": round(montant_ttc, 2),
        "taux_tva": f"{taux_tva}%",
        "date_echeance": d_echeance.strftime("%d/%m/%Y"),
        "date_paiement": d_paiement.strftime("%d/%m/%Y"),
        "jours_retard": jours_retard,
        "taux_penalites_annuel": f"{taux_annuel:.2f}% (3 × taux légal pro S1 2025 : {BAREME['taux_interet_legal_pro_s1_2025']}%)",
        "penalites_calculees": round(penalites, 2),
        "indemnite_forfaitaire_recouvrement": forfait,
        "total_reclamable": round(total, 2),
        "formule": f"{montant_ttc:.2f}€ TTC × {taux_annuel:.2f}% × ({jours_retard}j / 365) + {forfait}€ forfait",
        "base_legale": "Art. L441-10 Code de commerce — à mentionner sur CGV et factures.",
    }


def exec_calculer_tva_intracommunautaire(siren: str) -> dict:
    siren = siren.replace(" ", "").replace("-", "")
    if not siren.isdigit() or len(siren) != 9:
        return {"erreur": f"SIREN invalide : '{siren}'. Doit contenir exactement 9 chiffres."}
    cle = _calculer_cle_tva(siren)
    numero = f"FR{cle}{siren}"
    return {
        "siren": siren,
        "numero_tva_intracommunautaire": numero,
        "cle_controle": cle,
        "note": "Numéro calculé selon la formule officielle française (FR + clé + SIREN). Vérifiable sur le portail VIES de la Commission Européenne."
    }


TOOL_EXECUTORS = {
    "bodacc_annonces": lambda args: exec_bodacc_annonces(
        siren=args["siren"], nb_annonces=args.get("nb_annonces", 5)
    ),
    "valider_tva_vies": lambda args: exec_valider_tva_vies(
        code_pays=args["code_pays"], numero_tva=args["numero_tva"]
    ),
    "baremes_fiscaux_sociaux": lambda args: exec_baremes_fiscaux_sociaux(
        categorie=args.get("categorie", "tout")
    ),
    "calculer_cotisations_tns": lambda args: exec_calculer_cotisations_tns(
        revenu_net=args["revenu_net"], annee=args.get("annee", 2025)
    ),
    "calculer_penalites_retard": lambda args: exec_calculer_penalites_retard(
        montant_ht=args["montant_ht"],
        date_echeance=args["date_echeance"],
        date_paiement=args["date_paiement"],
        taux_tva=args.get("taux_tva", 20.0),
    ),
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
    "calculer_tva_intracommunautaire": lambda args: exec_calculer_tva_intracommunautaire(
        siren=args["siren"]
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
