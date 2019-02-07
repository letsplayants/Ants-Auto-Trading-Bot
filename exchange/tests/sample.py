import websocket
import json

class MySocket:
    # ws = 
    def __init__(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                    on_message = lambda ws,msg: self.on_message(ws, msg),
                    on_error   = lambda ws,msg: self.on_error(ws, msg),
                    on_close   = lambda ws:     self.on_close(ws),
                    on_open    = lambda ws:     self.on_open(ws))

        self.ws.run_forever()

    def on_message(self, ws, message):
        print( message )

    def on_error(self, ws, error):
        print( error )

    def on_close(self, ws):
        print( "### closed ###" )

    def on_open(self, ws):
        data=[{"ticket":"upbit_arbit_bot"}, #고유한 키값을 넣어서 응답이 왔을 때 구분자로 사용한다.
            {"type":"orderbook","codes":['KRW-BTC']},
            {"format":"SIMPLE"}]
        ws.send(json.dumps(data))

if __name__ == "__main__":
    upbitSocket = MySocket()