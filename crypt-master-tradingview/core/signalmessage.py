from signalwire.rest import Client as signalwire_client

client = signalwire_client("YourProjectID", "YourAuthToken", signalwire_space_url = 'example.signalwire.com')

message = client.messages.create(
                              from_='+15550011222',
                              body='Hello World!',
                              to='+15550011333'
                          )

print(message.sid)