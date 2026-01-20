import pytest
from src.domain.models import Cart, Movie
from src.core.strategies import BackToTheFutureStrategy

@pytest.fixture
def strategy():
    return BackToTheFutureStrategy()

def create_cart_with_series(titles):
    movies = []
    for title in titles:
        if "Back to the Future" in title:
            series_title = "Back to the Future"
            price = 15.0
        else:
            series_title = None
            price = 20.0
        movies.append(Movie(title=title, series_title=series_title, price=price))
    return Cart(items=movies)

def test_example_1(strategy):
    # Back to the Future 1 Back to the Future 2 Back to the Future 3 -> 36
    # 3 distinct BTTF -> 20% off all BTTF. (15*3)*0.8 = 36
    cart = create_cart_with_series(["Back to the Future 1", "Back to the Future 2", "Back to the Future 3"])
    assert strategy.calculate_price(cart) == 36

def test_example_2(strategy):
    # Back to the Future 1 Back to the Future 3 -> 27
    # 2 distinct BTTF -> 10% off all BTTF. (15*2)*0.9 = 27
    cart = create_cart_with_series(["Back to the Future 1", "Back to the Future 3"])
    assert strategy.calculate_price(cart) == 27

def test_example_3(strategy):
    # Back to the Future 1 -> 15
    # 1 distinct BTTF -> 0% off. 15
    cart = create_cart_with_series(["Back to the Future 1"])
    assert strategy.calculate_price(cart) == 15

def test_example_4(strategy):
    # Back to the Future 1 Back to the Future 2 Back to the Future 3 Back to the Future 2 -> 48
    # 3 distinct BTTF (1, 2, 3) -> 20% off ALL BTTF. (15*4)*0.8 = 48
    cart = create_cart_with_series(["Back to the Future 1", "Back to the Future 2", "Back to the Future 3", "Back to the Future 2"])
    assert strategy.calculate_price(cart) == 48

def test_example_5(strategy):
    # Back to the Future 1 Back to the Future 2 Back to the Future 3 La chèvre -> 56
    # 3 distinct BTTF -> 20% off ALL BTTF. ((15*3)*0.8) + 20 = 45*0.8 + 20 = 36+20 = 56
    cart = create_cart_with_series(["Back to the Future 1", "Back to the Future 2", "Back to the Future 3", "La chèvre"])
    assert strategy.calculate_price(cart) == 56
