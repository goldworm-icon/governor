GET_DELEGATION = {
    "totalDelegated": int,
    "votingPower": int,
    "delegations": [{"value": int}],
}

GET_PREP = {
    "blockHeight": int,
    "delegated": int,
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
            "delegated": int,
            "totalBlocks": int,
            "validatedBlocks": int,
            "irep": int,
            "irepUpdateBlockHeight": int,
            "unvalidatedSequenceBlocks": int,
            "lastGenerateBlockHeight": int,
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
