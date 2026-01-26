from src.domain.models import Cart, Movie


def test_cart_from_text():
    text = """Back to the Future 1
    Back to the Future 2
    Back to the Future 3"""
    cart = Cart.from_text(text)
    assert len(cart.items) == 3
    assert cart.items[0].title == "Back to the Future 1"
    assert cart.items[1].title == "Back to the Future 2"
    assert cart.items[2].title == "Back to the Future 3"


def test_cart_is_bttf():
    movie = Movie("Back to the Future 1")
    movie.series_title = "Back to the Future"
    assert movie.series_title == "Back to the Future"
    assert Movie("La chèvre").series_title != "Back to the Future"


def test_cart_empty():
    assert len(Cart.from_text("").items) == 0
    assert len(Cart.from_text("   ").items) == 0
