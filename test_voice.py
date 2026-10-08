from services.speech import speak
import time

for i in range(5):
    print(f"Speaking {i+1}")
    speak(f"This is test number {i+1}")
    time.sleep(3)