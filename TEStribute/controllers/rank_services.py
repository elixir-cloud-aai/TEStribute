import json

from TEStribute import rank_services


def RankServices(body):

    ranked_response = __post_rank_services(body)

    # TODO:
    #   handle FileNotFoundError

    return ranked_response


def __post_rank_services(params):

    response = rank_services(
        drs_ids=params.get("drs_ids"),
        drs_uris=params.get("drs_uris"),
        mode=params.get("mode"),
        resource_requirements=params.get("resource_requirements"),
        tes_uris=params.get("tes_uris")
    )

    return response
