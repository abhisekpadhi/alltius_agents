import os
import json
from lib.logging import log

class Recall:
    def remember(self, key, value):
        try:
            # Load existing cache
            cache = {}
            if os.path.exists('cache.json'):
                with open('cache.json', 'r') as f:
                    try:
                        cache = json.load(f)
                    except json.JSONDecodeError:
                        cache = {}
            else:
                # Create cache file if it doesn't exist
                with open('cache.json', 'w') as f:
                    json.dump({}, f, indent=2)
            
            # Update cache
            cache[key] = value
            
            # Write back to file
            with open('cache.json', 'w') as f:
                json.dump(cache, f, indent=2)
            log.info("Cache set successfully")
            
        except Exception as e:
            log.error("Failed to set cache", {"error": str(e)})

    def recall(self, key):
        try:
            if not os.path.exists('cache.json'):
                # Create cache file if it doesn't exist
                with open('cache.json', 'w') as f:
                    json.dump({}, f, indent=2)
                return None
                
            with open('cache.json', 'r') as f:
                try:
                    cache = json.load(f)
                    return cache.get(key)
                except json.JSONDecodeError:
                    log.error("Failed to parse cache file")
                    return None
                    
        except Exception as e:
            log.error("Failed to read cache", {"error": str(e)})
            return None

recall = Recall()