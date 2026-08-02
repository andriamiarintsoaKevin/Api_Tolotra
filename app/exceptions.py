class TouristNotFoundException(Exception):
    def __init__(self, tourist_id: int):
        self.tourist_id = tourist_id
