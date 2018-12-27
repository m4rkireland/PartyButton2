from aiy.board import Board, Led
from aiy.voice.tts import say
from aiy.voice.audio import play_wav, play_wav_async

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import threading

_rapid = False

class PartyButton:
    _rapid = False
    _rapid_lock = threading.Lock()

    def __init__(self):
        
        self._board = Board()
        self._board.button.when_pressed = self._on_button_press
        self._board.button.when_released = self._on_button_release
        self._coretopic = "home/partybutton/"
        self._armed = False
        self._activated = False

        self._led_task = threading.Thread(target=self._run_led_task)
        self._host = "192.168.1.222"
        self._port = 1883
        self._timeout = 60
        self._client = mqtt.Client(client_id="partybutton", clean_session=False)
        self._client.on_connect = self._on_connect
        
    def start(self):
        # MQTT stuff
        print("Start")
        self._client.connect(self._host, self._port, self._timeout)
        self._client.loop_start()
        self._led_task.start()
        self._board.led.state = Led.BLINK

    def _run_led_task(self):
        while True:
            with PartyButton._rapid_lock:
                if (PartyButton._rapid == True):
                    self._board.led.state = Led.ON
                    time.sleep(0.1)
                    self._board.led.state = Led.OFF
                    time.sleep(0.1)

    def _on_button_press(self):
        self._client.publish(self._coretopic + "arm" + "/status","ON", retain = 1)
        self._armed = True
        with PartyButton._rapid_lock:
            PartyButton._rapid = True

        play_wav_async('/home/pi/PartyButton2/GSIntro.wav')

        time.sleep(0.2)
        self._set_say("Initiating Party Mode")
        #play_wav('/home/pi/PartyButton2/dial-up-modem-01.wav')
        
        #play_wav_async('/home/pi/PartyButton2/GSIntro.wav')
        time.sleep(4)

        self._set_say("Setting the lights")

        time.sleep(4.5)

        self._set_say("Loading the music")

        time.sleep(6.5)
        self._set_say("Party Mode, ACTIVATED. - There ain't no party like a Maytion Road party!")
        
        # do voices
        # do lights
        # do MQTT
        self._client.publish(self._coretopic + "active" + "/status", "ON", retain = 1)
        self._activated = True
        
    def _set_say(self, text):
        say(text, lang='en-GB', volume=70, pitch=95, speed=100, device='default')

    def _on_button_release(self):
        with PartyButton._rapid_lock:
            PartyButton._rapid = False
        
        self._armed = False
        self._activated = False        
        self._client.publish(self._coretopic + "arm" + "/status","OFF", retain = 1)
        self._client.publish(self._coretopic + "active" + "/status", "OFF", retain = 1)        
        self._board.led.state = Led.BLINK

    def _on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(self._coretopic + "#",qos=1)

def main():
    PartyButton().start()


if __name__ == '__main__':
    main()
