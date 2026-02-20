import time
import logging
from core.evo_factory import evolve_new_alpha

logging.basicConfig(filename='logs/worker.log', level=logging.INFO, format='%(asctime)s - %(message)s')

print("🌑 MOONSHOT v3 WORKER STARTED – Constantly finding & evolving new alphas on live data")

while True:
    try:
        evolve_new_alpha()
        time.sleep(45)
    except Exception as e:
        logging.error(f"Error: {e}")
        time.sleep(10)
