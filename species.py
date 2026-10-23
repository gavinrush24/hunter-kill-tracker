SPECIES = [
    "White-tailed Deer",
    "Mule Deer",
    "Red Deer",
    "Fallow Deer",
    "Roe Deer",
    "Moose",
    "Black Bear",
    "Brown Bear",
    "Wild Boar",
    "Coyote",
    "Red Fox",
    "Pronghorn",
    "Bighorn Sheep",
    "Canada Goose",
    "Mallard",
]


def is_valid_species(name):
    """Return True if the name is in our master list."""
    return name in SPECIES