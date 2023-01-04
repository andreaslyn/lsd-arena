// SPDX-License-Identifier: MIT

methods {
    // Helper methods:
    reward(uint256);
    arraySum(uint256[]) returns uint256 envfree;
    balanceOf(address) returns uint256 envfree;
    sETHBalanceOf(address, bytes) returns(uint256) envfree;
    getSETHStakedBalanceForKnots(bytes[], address) returns uint256 envfree;
    previewUnclaimedETHAsCollateralizedSlotOwner(address, bytes[]) returns(uint256) envfree;
    totalUserCollateralisedSLOTBalanceForKnots(address, bytes[]) returns (uint256) envfree;
    circulatingCollateralisedSlotInStakehouseForKnot(bytes) returns uint256 envfree;
    memberKnotToStakeHouse(bytes) returns address envfree;
    allSameMemberKnotStakeHouse(bytes[]) returns bool envfree;
    previewUnclaimedETHAsFreeFloatingStaker(address, bytes[]) returns(uint256) envfree;

    // Syndicate methods:
    totalFreeFloatingShares() returns uint256 envfree;
    totalETHReceived() returns uint256 envfree;
    stake(bytes[], uint256[], address);
    unstake(address, address, bytes[], uint256[]);
    claimAsStaker(address, bytes[]);
    previewUnclaimedETHAsFreeFloatingStaker(address, bytes) returns(uint256) envfree;
    claimAsCollateralizedSLOTOwner(address, bytes[]);
    previewUnclaimedETHAsCollateralizedSlotOwner(address, bytes) returns(uint256) envfree;
    registerKnotsToSyndicate(bytes[]) envfree;
    deRegisterKnots(bytes[]) envfree;
    updateAccruedETHPerShares() envfree;
    addPriorityStakers(address[]) envfree;
    updatePriorityStakingBlock(uint256) envfree;
    updateCollateralizedSlotOwnersAccruedETH(bytes) envfree;
    batchUpdateCollateralizedSlotOwnersAccruedETH(bytes[]) envfree;
    calculateUnclaimedFreeFloatingETHShare(bytes, address) returns uint256 envfree;
    calculateETHForFreeFloatingOrCollateralizedHolders() returns uint256 envfree;
    calculateNewAccumulatedETHPerFreeFloatingShare() returns uint256 envfree;
    calculateNewAccumulatedETHPerCollateralizedSharePerKnot() returns uint256 envfree;
}

// The PRECISION definition is used for division and equality comparisons,
// to circumvent issues with rounding.
definition PRECISION returns uint256 = 1000000000000000000000000; // 1e24

// A division operations which scales the nominator by PRECISION,
// to circumvent issues with rounding.
definition precision_div(uint256 x, uint256 y) returns uint256 =
    (x * PRECISION()) / y;

// An equality comparison treats numbers with PRECISION in difference to be equal.
// There is probably a better way to work with rounding issues!
definition precision_eq(uint256 x, uint256 y) returns bool =
    x - y <= PRECISION() && y - x <= PRECISION();

// Convert a uint256 number to ether.
definition asEther(uint256 x) returns uint256 = x * 1000000000000000000;

// When a reward is received, then totalETHReceived is increased by that amount.
rule rewardTotalETHReceived() {
    uint256 t0 = totalETHReceived();

    env e;
    uint256 rewardAttempt;
    reward(e, rewardAttempt);

    uint256 t = totalETHReceived();
    uint256 actualReward = e.msg.value >= rewardAttempt ? rewardAttempt : 0;
    assert t == t0 + actualReward;
}

// Methods which do not change the balance of the syndicate do not affect totalETHReceived.
rule noRewardTotalETHReceived(method f)
filtered {
    f -> f.selector != reward(uint256).selector
} {
    uint256 t0 = totalETHReceived();

    env e;
    calldataarg args;
    f(e, args);

    uint256 t = totalETHReceived();
    assert t == t0;
}

// When a reward is received, then previewUnclaimedETHAsFreeFloatingStaker is increased
// by an amount corresponding to the staker's share of sETH in the syndicate.
rule rewardPreviewUnclaimedETHAsFreeFloatingStaker() {
    address staker;
    bytes[] knots;

    uint256 before = previewUnclaimedETHAsFreeFloatingStaker(staker, knots);

    env e;
    uint256 totalReward;
    require e.msg.value >= totalReward;
    reward(e, totalReward);

    uint256 after = previewUnclaimedETHAsFreeFloatingStaker(staker, knots);
    uint256 givenReward = after - before;
    uint256 totalKnotStake = totalFreeFloatingShares();
    uint256 theStake = getSETHStakedBalanceForKnots(knots, staker);

    assert precision_eq(
        precision_div(givenReward * 2, totalReward),
        precision_div(theStake, totalKnotStake));
}

// Methods, which do not change the balance of the syndicate and do not claim free
// floating staker rewards, do not affect previewUnclaimedETHAsFreeFloatingStaker.
rule noRewarNoClaimPreviewUnclaimedETHAsFreeFloatingStaker(method f)
filtered {
    f -> f.selector != claimAsStaker(address, bytes[]).selector
      && f.selector != unstake(address, address, bytes[], uint256[]).selector
      && f.selector != reward(uint256).selector
} {
    address staker;
    bytes[] knots;

    uint256 before = previewUnclaimedETHAsFreeFloatingStaker(staker, knots);

    env e;
    calldataarg args;
    f(e, args);

    uint256 after = previewUnclaimedETHAsFreeFloatingStaker(staker, knots);

    assert before == after;
}

// When a reward is received, then previewUnclaimedETHAsCollateralizedSlotOwner is increased
// by an amount corresponding to the staker's share of sETH in the syndicate.
rule rewardPreviewUnclaimedETHAsCollateralizedSlotOwner() {
    address staker;
    bytes[] knots;
    require knots.length > 0;
    require allSameMemberKnotStakeHouse(knots);

    uint256 before = previewUnclaimedETHAsCollateralizedSlotOwner(staker, knots);

    env e;
    uint256 totalReward;
    require e.msg.value >= totalReward;
    reward(e, totalReward);

    uint256 after = previewUnclaimedETHAsCollateralizedSlotOwner(staker, knots);
    uint256 givenReward = after - before;
    uint256 totalCollateralizedStake =
        circulatingCollateralisedSlotInStakehouseForKnot(knots[0]);
    uint256 theStake = totalUserCollateralisedSLOTBalanceForKnots(staker, knots);

    assert precision_eq(
        precision_div(givenReward * 2, totalReward),
        precision_div(theStake, totalCollateralizedStake));
}

// Methods, which do not change the balance of the syndicate and do not claim collateralized
// SLOT owner rewards, do not affect previewUnclaimedETHAsCollateralizedSlotOwner.
rule noRewardNoClaimPreviewUnclaimedETHAsCollateralizedSlotOwner(method f)
filtered {
    f -> f.selector != claimAsCollateralizedSLOTOwner(address, bytes[]).selector
      && f.selector != reward(uint256).selector
} {
    address staker;
    bytes[] knots;
    require allSameMemberKnotStakeHouse(knots);

    uint256 before = previewUnclaimedETHAsCollateralizedSlotOwner(staker, knots);

    env e;
    calldataarg args;
    f(e, args);

    uint256 after = previewUnclaimedETHAsCollateralizedSlotOwner(staker, knots);

    assert before == after;
}

// When increasing stake with the stake method, the following rewards for
// that user become correspondingly higher.
rule stakeReward() {
    address staker;
    bytes[] knots;

    uint256 totalKnotStakeBefore = totalFreeFloatingShares();
    uint256 stakedBefore = getSETHStakedBalanceForKnots(knots, staker);
    uint256 before = previewUnclaimedETHAsFreeFloatingStaker(staker, knots);

    env eStake;
    uint256[] sETHs;
    uint256 sETH = arraySum(sETHs);

    stake(eStake, knots, sETHs, staker);

    uint256 totalKnotStakeAfter = totalFreeFloatingShares();
    uint256 stakedAfter = getSETHStakedBalanceForKnots(knots, staker);

    assert totalKnotStakeAfter - totalKnotStakeBefore == sETH;
    assert stakedAfter - stakedBefore == sETH;

    env eReward;
    uint256 totalReward;
    require (eReward.msg.value >= totalReward);
    reward(eReward, totalReward);

    uint256 after = previewUnclaimedETHAsFreeFloatingStaker(staker, knots);
    uint256 givenReward = after - before;

    assert precision_eq(
        precision_div(givenReward * 2, totalReward),
        precision_div(stakedAfter, totalKnotStakeAfter));
}

// When decreasing stake with the unstake method, the following rewards for
// that user become correspondingly lower.
rule unstakeReward() {
    env eUnstake;
    bytes[] knots;
    require knots.length > 0;
    require allSameMemberKnotStakeHouse(knots);

    uint256 totalKnotStakeBefore = totalFreeFloatingShares();
    uint256 stakedBefore = getSETHStakedBalanceForKnots(knots, eUnstake.msg.sender);
    uint256 before = previewUnclaimedETHAsFreeFloatingStaker(eUnstake.msg.sender, knots);

    address sETHReceiver;
    address ethReceiver;
    uint256[] sETHs;
    uint256 sETH = arraySum(sETHs);
    uint256 ethReceiverBalanceBefore = balanceOf(ethReceiver);
    uint256 sETHReceiverBalanceBefore = sETHBalanceOf(sETHReceiver, knots[0]);

    unstake(eUnstake, ethReceiver, sETHReceiver, knots, sETHs);

    uint256 ethReceiverBalanceAfter = balanceOf(ethReceiver);
    uint256 sETHReceiverBalanceAfter = sETHBalanceOf(sETHReceiver, knots[0]);

    assert ethReceiverBalanceAfter - ethReceiverBalanceBefore == before;
    assert sETHReceiverBalanceAfter - sETHReceiverBalanceBefore == sETH;

    uint256 totalKnotStakeAfter = totalFreeFloatingShares();
    uint256 stakedAfter = getSETHStakedBalanceForKnots(knots, eUnstake.msg.sender);

    assert totalKnotStakeBefore - totalKnotStakeAfter == sETH;
    assert stakedBefore - stakedAfter == sETH;

    env eReward;
    uint256 totalReward;
    require (eReward.msg.value >= totalReward);
    reward(eReward, totalReward);

    uint256 after = previewUnclaimedETHAsFreeFloatingStaker(eUnstake.msg.sender, knots);
    uint256 givenReward = after - before;

    assert precision_eq(
        precision_div(givenReward * 2, totalReward),
        precision_div(stakedAfter, totalKnotStakeAfter));
}

// If previewUnclaimedETHAsFreeFloatingStaker is x ETH, then claimAsStaker will
// transfer x ETH to the recipient.
rule previewUnclaimedClaimAsStaker() {
    env e;
    address recipient;
    bytes[] knots;

    uint256 unclaimed = previewUnclaimedETHAsFreeFloatingStaker(e.msg.sender, knots);

    uint256 balanceBefore = balanceOf(recipient);
    claimAsStaker(e, recipient, knots);
    uint256 balanceAfter = balanceOf(recipient);

    assert unclaimed == balanceAfter - balanceBefore;
}

// Immediately after claimAsStaker has been called,
// previewUnclaimedETHAsFreeFloatingStaker is zero.
rule claimAsStakerPreviewUnclaimed() {
    env e;
    address recipient;
    bytes[] knots;

    claimAsStaker(e, recipient, knots);

    uint256 unclaimed = previewUnclaimedETHAsFreeFloatingStaker(e.msg.sender, knots);

    assert unclaimed == 0;
}

// If previewUnclaimedETHAsCollateralizedSlotOwner is x ETH, then
// claimAsCollateralizedSLOTOwner will transfer x ETH to the recipient.
rule previewUnclaimedClaimAsCollateralizedSlotOwner() {
    env e;
    address recipient;
    bytes[] knots;

    uint256 unclaimed = previewUnclaimedETHAsCollateralizedSlotOwner(e.msg.sender, knots);

    uint256 balanceBefore = balanceOf(recipient);
    claimAsCollateralizedSLOTOwner(e, recipient, knots);
    uint256 balanceAfter = balanceOf(recipient);

    assert unclaimed == balanceAfter - balanceBefore;
}

// Immediately after claimAsCollateralizedSLOTOwner has been called,
// previewUnclaimedETHAsCollateralizedSlotOwner is zero.
rule claimPreviewUnclaimedETHAsCollateralizedSlotOwner() {
    env e;
    address recipient;
    bytes[] knots;

    claimAsCollateralizedSLOTOwner(e, recipient, knots);

    uint256 unclaimed = previewUnclaimedETHAsCollateralizedSlotOwner(e.msg.sender, knots);

    assert unclaimed == 0;
}
