import dns.name
import dns.resolver

# Ce qu'on cherche à valider sur un domaine :
# - est-ce que c'est vraiment un nom de domaine (i.e. pas le nom de ma belle mère)
# - est-ce que le domaine existe (intéroger NOS dns), quels sont les DNS faisant autorité
# - quels sont les entrées attendues (SPF, divers CNAME, clef DKIM) -> lister les enregistrements à vérifier
# - vérifier chacun de ces enregistrements sur un des dns faisant aurotité (en court-circuitant le cache)
# - refaire les mêmes contrôles sur nos dns et/ou sur des dns publics, indiquer si les caches sont à jour ou s'il y a une propagation en cours
# - produire des messages d'erreur explicites sur ce qui ne va pas et ce qu'il faut corriger

name = dns.name.from_text("fdn.fr")
print(name)

answer = dns.resolver.resolve(name, rdtype = "MX")
print(answer)
for x in answer:
    print(f"item: {x}")
    print(x)
    print(x.exchange)
    print(x.preference)
