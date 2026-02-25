from typing import Optional
from datetime import datetime

def format_expiration_dt(expiration_dt: Optional[int]) -> Optional[str]:
    if expiration_dt is None:
        return None

    return datetime.fromtimestamp(float(expiration_dt)).isoformat()