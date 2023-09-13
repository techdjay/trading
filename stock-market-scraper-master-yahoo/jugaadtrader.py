from jugaad_trader import Upstox
u = Upstox(client_id="2WABGQ",
            password="Jayvns9807#",
            twofa="1991")

status = u.login()
print(status)

holdings = u.get_holdings(series="EQ", product="D")
print(holdings['data'])