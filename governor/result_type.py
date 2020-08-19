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

GET_STAKE = {
    "stake": int,
    "unstakes": [{"unstake": int, "unstakeBlockHeight": int, "remainingBlocks": int}],
}

QUERY_ISCORE = {
    "blockHeight": int,
    "estimatedICX": int,
    "iscore": int,
}
