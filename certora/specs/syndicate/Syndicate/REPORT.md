# Objective

The objective was to understand the syndicate contract well enough to state important properties and invariants in a
Certora specification. As it turned out, some of the subgoals were to obtain a high level understanding of Stakehouse
LSD Networks and learn about concepts from the Stakehouse protocol.

# Approach

Background knowledge on Stakehouse LSD Networks was obtained through the official
[LSD Network documentation](https://docs.joinstakehouse.com/lsd/overview).

The [lsd-arena](https://github.com/stakehouse-dev/lsd-arena) repository was cloned, to play around with it,
run the Foundry tests and run Certora specs. The repository contained useful links with documentation. The
[syndicate test](https://github.com/stakehouse-dev/lsd-arena/blob/main/test/foundry/Syndicate.t.sol) `Syndicate.t.sol`
was a good place to play around with the syndicate contract and get inspiration.

The documentation for the [Stakehouse protocol](https://docs.joinstakehouse.com/protocol/learn/Stakehouse) was useful
for understanding the role of KNOTs, dETH, sETH and SLOT tokens.

At this point it was possible to read and understand the syndicate contract. The `Syndicate.t.sol` test file was used to
verify understanding by changing tests and see the consequences. Properties of the syndicate contract started to emerge.

To state properties of the syndicate contract, it was time to write a Certora spec.
The [Certora tutorials](https://github.com/Certora/Tutorials) were useful to learn initially, and
the [Certora documentation](https://docs.certora.com/en/latest/index.html) was used extensively.

# Summary of the Syndicate Contract

The primary function of the syndicate contract is to receive rewards in ETH and distribute it between collateralized
SLOT owners and free floating stakers. In an LSD Network, per KNOT there is one collateralized SLOT owner and one
free floating staker, i.e. the Node Runner's smart wallet and the Fees and MEV Pool, respectively. There is a KNOT
for each validator associated to the LSD Network. It requires 32 ETH to create a validator, 4 ETH from the Node Runner,
4 ETH from the Fees and MEV Pool, and 24 ETH from the Protected Staking Pool.

The collateralized SLOT owners and free floating stakers get SLOT tokens when the validator is created. Each SLOT token
gives rise to a number of sETH, which can be staked to the syndicate. The share of sETH staked to the syndicate
corresponds to the share of ETH rewards which users can claim from the syndicate.

# Properties of the Syndicate Contract

We will start with two simple properties of the `totalETHReceived` method.

> When a reward is received, then `totalETHReceived` is increased by that amount.

> Methods which do not change the balance of the syndicate do not affect `totalETHReceived`.

The `previewUnclaimedETHAsFreeFloatingStaker` method has the following two properties.

> When a reward is received, then `previewUnclaimedETHAsFreeFloatingStaker` is increased by an amount corresponding
> to the staker's share of sETH in the syndicate.

> Methods, which do not change the balance of the syndicate and do not claim free floating staker rewards, do not
> affect `previewUnclaimedETHAsFreeFloatingStaker`.

The `rewardPreviewUnclaimedETHAsCollateralizedSlotOwner` methods satisfies two properties, analogous to those of
`previewUnclaimedETHAsFreeFloatingStaker`, but for collateralized SLOT owners instead of free floating stakers:

> When a reward is received, then `previewUnclaimedETHAsCollateralizedSlotOwner` is increased
> by an amount corresponding to the staker's share of sETH in the syndicate.

> Methods, which do not change the balance of the syndicate and do not claim collateralized
> SLOT owner rewards, do not affect `previewUnclaimedETHAsCollateralizedSlotOwner`.

The `stake` method satisfies:

> When increasing stake with the `stake` method, the following rewards for that user become correspondingly higher.

The `unstake` method satisfies the opposite property:

> When decreasing stake with the `unstake` method, the following rewards for that user become correspondingly lower.

There are two relations between the `claimAsStaker` method and the `previewUnclaimedETHAsFreeFloatingStaker`:

> If `previewUnclaimedClaimAsStaker` is `x` ETH, then `claimAsStaker` will transfer `x` ETH to the recipient.

> Immediately after `claimAsStaker` has been called, `previewUnclaimedClaimAsStaker` is zero.

There are two relations between `claimAsCollateralizedSLOTOwner` and
`previewUnclaimedETHAsCollateralizedSlotOwner`, analogous to those relations between
`claimAsStaker` and `previewUnclaimedETHAsFreeFloatingStaker`:

> If `previewUnclaimedETHAsCollateralizedSlotOwner` is `x` ETH, then `claimAsCollateralizedSLOTOwner`
> will transfer `x` ETH to the recipient.

> Immediately after `claimAsCollateralizedSLOTOwner` has been called,
> `previewUnclaimedETHAsCollateralizedSlotOwner` is zero.

# Appendix

Link to (untested) syndicate spec and syndicate helper.
