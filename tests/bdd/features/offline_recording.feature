Feature: Offline Recording with Client Assembly
  As a user without internet connection
  I want to record audio and save it locally
  So that I can continue working offline and upload later

  Background:
    Given the user has no internet connection
    And the WaveForge Pro application is loaded
    And the ConnectionMonitor shows "Offline" status

  Scenario: Record audio while offline
    Given the user is on the main recording page
    When the user clicks the record button
    Then the recording indicator should be visible
    And the recording should start
    And chunks should be saved locally only
    And no upload attempts should be made

  Scenario: Save recording with client assembly
    Given the user has recorded audio for 5 seconds while offline
    When the user clicks the stop button
    Then the save modal should appear
    And the user should be prompted to enter a filename
    When the user enters "offline_test" as the filename
    And the user clicks the save button
    Then the recording should be assembled on the client
    And the recording should appear in the playlist
    And the recording should have a "LOCAL" badge
    And an upload button should be visible for this recording

  Scenario: Play locally-stored recording
    Given the user has a local recording in the playlist
    When the user clicks on the recording
    And the user clicks the play button
    Then the audio should play from IndexedDB
    And playback should start immediately
    And the current time should update during playback

  Scenario: Upload local recording when connection restored
    Given the user has a local recording in the playlist
    And the user was offline
    When the internet connection is restored
    And the ConnectionMonitor shows "Online" status
    Then the upload button should become enabled
    When the user clicks the upload button
    Then the recording should start uploading to the server
    And a progress indicator should be visible
    And the badge should change from "LOCAL" to "SERVER" when complete

  Scenario: Automatic background upload queue
    Given the user has 3 local recordings in the playlist
    And the user was offline
    When the internet connection is restored
    Then the upload queue should process recordings automatically
    And recordings should upload one at a time
    And the UI should show upload progress
    And all recordings should eventually have "SERVER" badges

  Scenario: Download local recording
    Given the user has a local recording in the playlist
    When the user clicks the download button
    Then the file should be downloaded from IndexedDB
    And the filename should match the recording name
    And the file should be in WebM format
