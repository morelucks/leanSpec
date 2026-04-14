"""Checkpoint sync (non-genesis anchor) tests."""

from consensus_testing import (
    BlockSpec,
    BlockStep,
    ForkChoiceTest,
    ForkChoiceTestFiller,
    StoreChecks,
    generate_pre_state,
)
from lean_spec.subspecs.containers.slot import Slot
from lean_spec.subspecs.containers.validator import ValidatorIndex
from lean_spec.subspecs.ssz.hash import hash_tree_root


def test_store_from_non_genesis_anchor(
    fork_choice_test: ForkChoiceTestFiller,
) -> None:
    """Store initializes correctly from a non-genesis anchor block and state."""
    # 1. Generate a mid-chain anchor state and block at slot 10
    #
    # We start from genesis, advance to slot 10, and build a block.
    # The resulting (state, block) pair is our trusted checkpoint.
    genesis = generate_pre_state(num_validators=4)
    state_at_9 = genesis.process_slots(Slot(9))

    # Build the anchor block.
    # Proposer index 2 is selected round-robin (10 % 4 = 2).
    parent_root = hash_tree_root(state_at_9.latest_block_header)
    anchor_block, anchor_state, _, _ = state_at_9.build_block(
        slot=Slot(10),
        proposer_index=ValidatorIndex(2),
        parent_root=parent_root,
        known_block_roots={parent_root},
    )

    # 2. Initialize the fork choice test from this non-genesis anchor
    #
    # The framework will call Store.from_anchor() during make_fixture().
    fork_choice_test(
        anchor_state=anchor_state,
        anchor_block=anchor_block,
        steps=[
            # Build blocks on top of the anchor
            BlockStep(
                block=BlockSpec(slot=Slot(11)),
                checks=StoreChecks(head_slot=Slot(11)),
            ),
            BlockStep(
                block=BlockSpec(slot=Slot(12)),
                checks=StoreChecks(head_slot=Slot(12)),
            ),
            BlockStep(
                block=BlockSpec(slot=Slot(13)),
                checks=StoreChecks(head_slot=Slot(13)),
            ),
        ],
    )
