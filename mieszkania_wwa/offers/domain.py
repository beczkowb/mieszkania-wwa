class Offer:
    def __init__(self, pk, lat, lng, price, subject, post_id):
        self.pk = pk
        self.lat = lat
        self.lng = lng
        self.price = price
        self.subject = subject
        self.post_id = post_id

    def __eq__(self, other):
        return other.pk == self.pk

    def __hash__(self):
        return hash(self.pk)