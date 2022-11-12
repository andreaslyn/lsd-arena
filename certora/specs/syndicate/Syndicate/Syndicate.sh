certoraRun \
contracts/specs/syndicate/SyndicateHelper.sol \
    --verify SyndicateHelper:certora/specs/syndicate/Syndicate/Syndicate.spec \
    --packages @blockswaplab=node_modules/@blockswaplab @openzeppelin=node_modules/@openzeppelin
