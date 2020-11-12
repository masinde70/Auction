from django.urls import reverse

def create_auction_email(auction, request):

    return (
        "Auction created",

        "Dear {username},\n\n"
        "Thank you for registering a new auction with us. We will get your item(s) sold in no time.\n"
        "In the meantime you can view your auction at {url}.\n\n"
        "Best Regards,\n"
        "YAAS Team"
        .format(
            username=request.user.username.capitalize(),
            url=request.build_absolute_uri(reverse('auction_read', kwargs={'auction_id': auction.id}))
        )
    )


def create_bid_email(bid, auction):
    return (
        "New Bid",

        "Dear All,\n\n"
        "A new bid of {amount:.2f} has been placed on auction '{title}'.\n\n"
        "Best Regards,\n"
        "YAAS Team"
        .format(
            amount=bid.amount,
            title=auction.title)
    )


def resolve_auction_email(auction):
    return (
        "Auction {title} concluded.".format(title=auction.title),

        "Dear All,\n\n"
        "The auction '{title}' has been resolved.\n\n"
        "Best Regards,\n"
        "YAAS Team"
            .format(
            title=auction.title,
        )
    )


def ban_auction_email(auction):
    return (
        "Auction {title} banned.".format(title=auction.title),

        "Dear All,\n\n"
        "The auction '{title}' has been banned.\n"
        "We apologize for any inconvenience.\n\n"
        "Best Regards,\n"
        "YAAS Team"
            .format(
            title=auction.title,
        )
    )



