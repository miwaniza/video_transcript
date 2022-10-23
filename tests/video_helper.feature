# Created by dyd at 22.10.2022
Feature: 1
  Scenario: Get audio from video
    Given I have a video file
    When I extract audio from video
    Then I get audio file