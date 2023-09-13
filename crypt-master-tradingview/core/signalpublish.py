from core import signalcli
import re

my_name = "sigbot"
my_state = {
    "logging": False
}


def on_message(sigcli_obj, event_name, msg, state):
    print(str(msg))
    re_m = re.match('/(\w+)', msg.message_body)
    if re_m:
        command = re_m.group(1)
        if command == "log":
            if state['logging']:
                sigcli_obj.reply(msg, my_name + ": Logging is OFF", reply_to_sent_messages=True)
                state['logging'] = False
            else:
                sigcli_obj.reply(msg, my_name + ": Logging is ON", reply_to_sent_messages=True)
                state['logging'] = True
        else:
            sigcli_obj.reply(msg, my_name + ": Unknown command '" + command + "'", reply_to_sent_messages=True)


## create new signal-cli object (will automatically start signal-cli in the background)
# sig = signalcli.Signalcli(debug=True, user_name="+46123456789")
sig = signalcli.Signalcli(debug=True, user_name="+8613975746074")

## register event callbacks that are triggered whenever something happens
k = sig.on('message', on_message, my_state)

## start the asyncio event loop
sig.run()
