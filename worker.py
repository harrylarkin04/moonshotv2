import time
import logging
from core.evo_factory import evolve_new_alpha

logging.basicConfig(
    filename='logs/worker.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    filemode='a'
)

logger = logging.getLogger('evolution_worker')

print("🌑 MOONSHOT v3 EVOLUTIONARY WORKER STARTED")
print("🔥 1200+ strategy population • 50 generations • Elite selection only")

while True:
    try:
        logger.info("Starting evolutionary cycle")
        result = evolve_new_alpha(ui_context=False)
        status = "SUCCESS" if result else "NO_ELITE"
        logger.info(f"Evolution completed: {status}")
        time.sleep(45)
    except Exception as e:
        logger.error(f"Evolution crashed: {str(e)}")
        time.sleep(10)
