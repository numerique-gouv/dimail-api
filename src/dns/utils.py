import dns.name
import dns.resolver

def get_ip_address(domain: str) -> str:
    answer = dns.resolver.resolve(domain)
    for item in answer:
        return str(item.address)

def make_auth_resolver(domain: str, insist: bool = False) -> dns.resolver.Resolver:
    print(f"Je cherche les resolvers pour {domain}")
    name = dns.name.from_text(domain)
    try:
        answer = dns.resolver.resolve(name, rdtype = "NS")
    except dns.resolver.NoAnswer:
        (_, up) = domain.split(".", 1)
        print(f"Je ne trouve pas les NS pour {domain}, je remonte d'un cran vers {up}")
        return make_auth_resolver(up, insist)
    except dns.resolver.NXDOMAIN:
        if insist:
            (_, up) = domain.split(".", 1)
            print(f"Je ne trouve pas les NS pour {domain}, je remonte d'un cran vers {up}")
            return make_auth_resolver(up, insist)
        raise
    except Exception:
        raise
    addresses = []
    for item in answer:
        ip_addr = get_ip_address(str(item.target))
        addresses.append(ip_addr)
    resolver = dns.resolver.Resolver()
    resolver.nameservers = addresses
    return resolver


