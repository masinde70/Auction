
class BannedAuctionException(Exception):
    """Raised when an illegal action is taken on an auction in banned state"""


class DoneAuctionException(Exception):
    """Raised when an illegal action is taken on an auction in done state"""


class DueAuctionException(Exception):
    """Raised when an illegal action is taken on an auction in due state"""
