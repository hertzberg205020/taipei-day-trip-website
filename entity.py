class Attraction:

    def __init__(self, _id: int, name: str, category: str, description: str,
                 address: str, transport: str, mrt: str,
                 latitude: float, longitude: float, images: list[str] = None):
        self.id = _id
        self.name = name
        self.category = category
        self.description = description
        self.address = address
        self.transport = transport
        self.mrt = mrt
        self.latitude = latitude
        self.longitude = longitude
        self.images = images
