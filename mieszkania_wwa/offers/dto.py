class UnsavedOffer:
    def __init__(self, lat, lng, price, subject, post_id):
        self.lat = lat
        self.lng = lng
        self.price = price
        self.subject = subject
        self.post_id = post_id

    def __eq__(self, other):
        return other.lat == self.lat and\
            other.lng == self.lng and\
            other.price == self.price and\
            other.subject == self.subject and\
            other.post_id == self.post_id

    def __hash__(self):
        return hash((self.lat, self.lng, self.price, self.subject, self.post_id))