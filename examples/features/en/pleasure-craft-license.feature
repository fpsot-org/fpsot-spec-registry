# language: en
# SPDX-License-Identifier: Community-Spec-1.0
# Example feature of the FPSOT registry specification (REG-105), under TST-020 to TST-036.
# It replays the filings of examples/pleasure-craft/ under the ca-federal profile.
# Every person, number and order is fictional. All data is synthetic (TST-050 to TST-056).
@pleasure-craft-license
Feature: Replay of a pleasure craft license register
  Each scenario states the filings, their dates and the derived state that the replay must give.

  Rule: A license runs five years from its issue, transfer or renewal

    @pleasure-craft-license-001
    Scenario: A transfer opens a new owner group and a new term
      Given the register "pleasure-craft-licenses" under the profile "ca-federal" at version "0.1.0"
      And the filing "ownership-transfer" with the cause "sale" effective "2026-06-10T16:00:00Z" and submitted "2026-06-25T15:00:00Z"
      When the register completes the filing at "2026-06-26T15:00:00Z"
      Then the deadline status of the filing is "met"
      And as of "2026-06-20T12:00:00Z" recorded at "2026-08-10T12:00:00Z" the owner group "019a1b2c-3d4e-7f03-8a03-000000000302" holds the whole craft
      And the license "EX 000001" is valid from "2026-06-10" to "2031-06-10"

    @pleasure-craft-license-002
    Scenario: A renewal starts a new term from its own date
      Given the register "pleasure-craft-licenses" under the profile "ca-federal" at version "0.1.0"
      And the filing "license-renewal" effective "2031-05-20T16:00:00Z"
      When the register completes the filing at "2031-05-20T16:00:00Z"
      Then as of "2031-06-01T12:00:00Z" recorded at "2031-06-01T12:00:00Z" the license "EX 000001" is valid from "2031-05-20" to "2036-05-20"
      And the state of the license is "active"

    @pleasure-craft-license-003
    Scenario: An expired license needs no filing
      Given the register "pleasure-craft-licenses" under the profile "ca-federal" at version "0.1.0"
      And the last filing "license-renewal" of the license ends its validity on "2036-05-20"
      When the register replays its filings as of "2036-06-01T12:00:00Z" recorded at "2036-06-01T12:00:00Z"
      Then the state of the license is "expired"
      And the last filing sequence of the snapshot is 5

  Rule: A correction replaces a filing for every later record time

    @pleasure-craft-license-004
    Scenario: The hull serial number follows the correction once it is recorded
      Given the register "pleasure-craft-licenses" under the profile "ca-federal" at version "0.1.0"
      And the filing "filing-correction" that corrects sequence 1, completed at "2026-07-15T15:00:00Z"
      When the register replays its filings as of "2026-06-01T12:00:00Z" recorded at "2026-07-31T12:00:00Z"
      Then the hull serial number of the craft is "EXA 12354 B626"
      And the owner group "019a1b2c-3d4e-7f03-8a03-000000000301" was created by the correction and ended by sequence 2

  Rule: A lawful destruction keeps the chain verifiable

    @pleasure-craft-license-005
    Scenario: A destroyed filing leaves a tombstone and the chain still verifies
      Given the register "pleasure-craft-licenses" under the profile "ca-federal" at version "0.1.0"
      And the filing "destruction-order" that destroys sequence 1, completed at "2026-08-04T15:00:00Z"
      When a verifier checks the light chain from sequence 1 to sequence 5
      Then the content and the salt of sequence 1 are gone and its tombstone keeps its commitment
      And the previous commitment of sequence 2 equals the commitment in the tombstone
      And as of "2026-06-20T12:00:00Z" recorded at "2026-06-30T12:00:00Z" the craft shows as a destroyed row
