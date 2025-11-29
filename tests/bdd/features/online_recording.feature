Feature: Online Recording with Server Assembly
  As a user with an active internet connection
  I want to record audio and have it saved on the server
  So that I can save recordings quickly without processing delays

  Background:
    Given the user has an active internet connection
    And the WaveForge Pro application is loaded
    And the ConnectionMonitor shows "Online" status

  Scenario: Record audio with online connection
    Given the user is on the main recording page
    When the user clicks the record button
    Then the recording indicator should be visible
    And the recording should start
    And chunks should be uploaded in real-time
    
  Scenario: Save recording with server assembly
    Given the user has recorded audio for 5 seconds while online
    When the user clicks the stop button
    Then the save process should complete in less than 2 seconds
    And the recording should appear in the playlist
    And the recording should have a "SERVER" badge
    And no upload button should be visible for this recording

  Scenario: Play server-backed recording
    Given the user has a server-backed recording in the playlist
    When the user clicks on the recording
    And the user clicks the play button
    Then the audio should stream from the server
    And playback should start within 1 second
    And the current time should update during playback

  Scenario: Download server-backed recording
    Given the user has a server-backed recording in the playlist
    When the user clicks the download button
    Then the file should be downloaded from the server
    And the filename should match the recording name
    And the file should be in WebM format

  Scenario: Server assembly with rich metadata
    Given the user is recording audio online
    When the user records for 30 seconds
    And the user stops the recording
    Then the recording metadata should include duration
    And the metadata should include format information
    And the metadata should include sample rate
    And the metadata should be saved on the server

  Scenario: Fast save for long recordings
    Given the user has an active internet connection
    When the user records audio for 60 seconds
    And all chunks are uploaded during recording
    And the user stops the recording
    Then the save should complete in less than 2 seconds
    And the recording should be available immediately
    And the server should handle the assembly in the background

  Scenario: Real-time chunk upload monitoring
    Given the user is recording audio online
    When chunks are generated every 5 seconds
    Then each chunk should be uploaded immediately
    And the upload queue should be processed in order
    And the ConnectionMonitor should track upload status
    And uploaded chunks should be marked in IndexedDB
