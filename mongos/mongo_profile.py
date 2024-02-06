import os
import sys
from typing import Optional

ENV_VAR_NAME = "profile_sc_mongo_uri"


def get_mongo_uri() -> Optional[str]:
    profile: Optional[str] = os.getenv(ENV_VAR_NAME)
    if profile is None:
        print(f"WARNING: export {ENV_VAR_NAME}=$uri", file=sys.stdout)
    return profile


# _profiles = {
#     "staging":  "mongodb://twitterscantest:twitterscantest1234@mongodb-staging.loc:27017/twitter_scan?retryWrites=false&w=majority",
#     "prod":     "mongodb://twitterscantest:twitterscantest1234@mongodb2.loc:27017/twitter_scan?retryWrites=false"
# }
