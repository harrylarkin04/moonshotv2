import time
import logging
from core.evo_factory import evolve_new_alpha
import traceback  # Added for better error logging

logging.basicConfig(
    filename='logs/worker.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)

logger = logging.getLogger('evolution_worker')

print("🌑 MOONSHOT v3 EVOLUTIONARY WORKER STARTED")
print("🔥 1200+ strategy population • 50 generations • Elite selection only")

while True:
    try:
        logger.info("Starting evolutionary cycle")
        start_time = time.time()
        result = evolve_new_alpha(ui_context=False)
        elapsed = time.time() - start_time
        status = "SUCCESS" if result else "NO_ELITE"
        logger.info(f"Evolution completed in {elapsed:.1f}s: {status}")
        time.sleep(60)  # Longer sleep between cycles
    except Exception as e:
        logger.error(f"Evolution crashed: {str(e)}\n{traceback.format_exc()}")
        time.sleep(10)
