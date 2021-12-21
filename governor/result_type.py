GET_DELEGATION = {
    "totalDelegated": int,
    "votingPower": int,
    "delegations": [{"value": int}],
}

GET_PREP = {
    "blockHeight": int,
    "bonded": int,
    "delegated": int,
    "power": int,
    "irep": int,
    "lastGenerateBlockHeight": int,
    "totalBlocks": int,
    "unvalidatedSequenceBlocks": int,
    "validatedBlocks": int,
}

GET_PREPS = {
    "blockHeight": int,
    "startRanking": int,
    "totalDelegated": int,
    "totalStake": int,
    "preps": [
        {
            "status": int,
            "penalty": int,
            "grade": int,
            "stake": int,
            "blockHeight": int,
            "txIndex": int,
            "bonded": int,
            "delegated": int,
            "power": int,
            "totalBlocks": int,
            "validatedBlocks": int,
            "irep": int,
            "irepUpdateBlockHeight": int,
            "unvalidatedSequenceBlocks": int,
            "lastGenerateBlockHeight": int,
            "lastHeight": int,
        }
    ]
}

GET_PREP_STATS = {
    "blockHeight": int,
    "preps": [
        {
            "blockHeight": int,
            "grade": int,
            "status": int,
            "penalties": int,
            "lastHeight": int,
            "lastState": int,
            "total": int,
            "fail": int,
            "realTotal": int,
            "realFail": int,
            "failCont": int,
        }
    ]
}

GET_STAKE = {
    "stake": int,
    "unstakes": [{"unstake": int, "unstakeBlockHeight": int, "remainingBlocks": int}],
}

QUERY_ISCORE = {
    "blockHeight": int,
    "estimatedICX": int,
    "iscore": int,
}

STATUS = {
    "lastBlock": {
        "blockHeight": int,
        "timestamp": int,
    }
}
