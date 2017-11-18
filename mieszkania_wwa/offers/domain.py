class Offer:
    def __init__(self, pk, lat, lng, price, subject):
        self.pk = pk
        self.lat = lat
        self.lng = lng
        self.price = price
        self.subject = subject

    def __eq__(self, other):
        return other.pk == self.pk

    def __hash__(self):
        return hash(self.pk)