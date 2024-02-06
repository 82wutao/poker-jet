#!/usr/bin/python3
from typing import Any, Callable, Dict, List, Tuple, Union, cast

from api_twitter.api_key import get_v1_token
from api_twitter.v1 import ApiV11

apikey = get_v1_token()
api = ApiV11()
api.switch_apitoken(apikey)
api.switch_conn("abc.com/big-data")


def filter_user(usernames: List[str],
                predicate: Callable[[Dict[str, Any]], bool]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    names = ",".join(usernames)
    (statuscode, resp_json) = api.loopup_user(names)

    if statuscode != 200:
        raise Exception("loopup_user({}) \n\tresponse code {},\n\tbody {}".format(
            names, statuscode, resp_json))

    ok: List[Dict[str, Any]] = []
    notok: List[Dict[str, Any]] = []

    def _bin_classsifier(d: Dict[str, Any]):
        append = ok.append if predicate(d) else notok.append
        append(d)

    [_bin_classsifier(d) for d in cast(List[Dict[str, Any]], resp_json)]
    return tuple([ok, notok])
