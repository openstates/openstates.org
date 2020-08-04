from .common import pretty_url


def person_as_dict(person):
    return {
        "id": person.id,
        "name": person.name,
        "image": person.image,
        "primary_party": person.primary_party,
        "current_role": person.current_role,
        "pretty_url": pretty_url(person),
    }
