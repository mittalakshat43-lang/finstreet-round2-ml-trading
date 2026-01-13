# fyers/orders.py

from fyers_apiv3 import fyersModel

def place_order(
    access_token,
    symbol="NSE:RITES-EQ",
    qty=1,
    side="BUY",
    order_type="MARKET"
):
    """
    Places a simple market order using FYERS API
    """

    # Initialize FYERS client
    fyers = fyersModel.FyersModel(
        client_id="6N3D2EQCU5-100",
        token="JVU3RW4QQY",
        log_path=""
    )

    # Map side to FYERS format
    side_map = {
        "BUY": 1,
        "SELL": -1
    }

    order_data = {
        "symbol": symbol,
        "qty": qty,
        "type": 2 if order_type == "MARKET" else 1,  # 2 = Market, 1 = Limit
        "side": side_map[side],
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False
    }

    response = fyers.place_order(order_data)
    print("📤 Order Response:", response)

    return response


if __name__ == "__main__":
    ACCESS_TOKEN = "PASTE_ACCESS_TOKEN_HERE"

    place_order(
        access_token="JVU3RW4QQY",
        symbol="NSE:RITES-EQ",
        qty=1,
        side="BUY"
    )

