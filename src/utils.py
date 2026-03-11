from src.content_structure import Craft_and_Structure,Information_and_Ideas

def get_domain_handler(domain: str):
    if domain == "Craft and Structure":
        return Craft_and_Structure()
    elif domain == "Information and Ideas":
        return Information_and_Ideas()
    else:
        raise ValueError(f"Unsupported domain: {domain}")