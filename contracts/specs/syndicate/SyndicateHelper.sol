pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { Syndicate } from "../../syndicate/Syndicate.sol";
import { TransferFailed } from "../../syndicate/SyndicateErrors.sol";

/// @dev Use the helper contract containing helper methods for certora spec
contract SyndicateHelper is Syndicate {
    function reward(uint256 eip1559Reward) public {
        (bool success, ) = address(this).call{value: eip1559Reward}("");
        if (!success) revert TransferFailed();
    }

    function balanceOf(address addr) public view returns(uint256) {
        return addr.balance;
    }

    function sETHBalanceOf(address addr, bytes calldata blsPubKey) public view returns(uint256) {
        (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsPubKey);
        IERC20 sETH = IERC20(getSlotRegistry().stakeHouseShareTokens(stakeHouse));
        return sETH.balanceOf(addr);
    }

    function previewUnclaimedETHAsFreeFloatingStaker(
        address staker,
        bytes[] calldata blsPubKeys
    ) external view returns (uint256) {
        uint256 sum = 0;
        for (uint256 i = 0; i < blsPubKeys.length; ++i) {
            sum += this.previewUnclaimedETHAsFreeFloatingStaker(staker, blsPubKeys[i]);
        }
        return sum;
    }

    function previewUnclaimedETHAsCollateralizedSlotOwner(
        address staker,
        bytes[] calldata blsPubKeys
    ) external view returns (uint256) {
        uint256 sum = 0;
        for (uint256 i = 0; i < blsPubKeys.length; ++i) {
            sum += this.previewUnclaimedETHAsCollateralizedSlotOwner(staker, blsPubKeys[i]);
        }
        return sum;
    }

    function getSETHStakedBalanceForKnots(bytes[] calldata blsPubKeys, address staker) public view returns(uint256) {
        uint256 sum = 0;
        for (uint256 i = 0; i < blsPubKeys.length; ++i) {
            sum += this.sETHStakedBalanceForKnot(blsPubKeys[i], staker);
        }
        return sum;
    }

    function arraySum(uint256[] calldata a) pure public returns(uint256) {
        uint256 sum = 0;
        for (uint256 i = 0; i < a.length; ++i) {
            sum += a[i];
        }
        return sum;
    }

    function totalUserCollateralisedSLOTBalanceForKnots(address user, bytes[] calldata blsPubKeys)
            external view returns (uint256) {
        uint256 sum = 0;
        for (uint256 i = 0; i < blsPubKeys.length; ++i) {
            (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsPubKeys[i]);
            sum += getSlotRegistry().totalUserCollateralisedSLOTBalanceForKnot(stakeHouse, user, blsPubKeys[i]);
        }
        return sum;
    }

    function circulatingCollateralisedSlotInStakehouseForKnot(bytes calldata blsPubKey) external view returns (uint256) {
        (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsPubKey);
        return getSlotRegistry().circulatingCollateralisedSlot(stakeHouse);
    }

    function memberKnotToStakeHouse(bytes calldata blsPubKey) public view returns (address) {
        (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsPubKey);
        return stakeHouse;
    }

    function allSameMemberKnotStakeHouse(bytes[] calldata blsPubKeys) external view returns(bool) {
        if (blsPubKeys.length == 0) return false;
        address stakeHouse = memberKnotToStakeHouse(blsPubKeys[0]);
        for (uint256 i = 1; i < blsPubKeys.length; ++i) {
            if (memberKnotToStakeHouse(blsPubKeys[i]) != stakeHouse) return false;
        }
        return true;
    }
}
