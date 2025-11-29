Feature: Performance and Scalability
  As a power user recording long sessions
  I want the application to handle large files efficiently
  So that I can work with professional-length recordings

  Background:
    Given the WaveForge Pro application is loaded
    And the user has sufficient storage space

  Scenario: Fast save for 1-hour recording (online)
    Given the user has an active internet connection
    When the user records audio for 60 minutes
    And all chunks are uploaded during recording
    And the user stops the recording
    Then the save should complete in less than 2 seconds
    And the server should assemble the file in the background
    And the recording should appear in playlist immediately
    And the recording should have a "SERVER" badge

  Scenario: Client assembly for 1-hour recording (offline)
    Given the user is offline
    When the user records audio for 60 minutes
    And the user stops the recording
    Then client-side assembly should begin
    And a progress indicator should show assembly status
    And assembly should complete in reasonable time
    And the recording should be saved to IndexedDB
    And memory usage should remain acceptable

  Scenario: Handle 100+ recordings in playlist
    Given the user has 100 recordings in the playlist
    When the playlist is rendered
    Then the UI should load within 3 seconds
    And scrolling should be smooth
    And all recordings should display correctly
    And server badges and local badges should be accurate
    And memory usage should be optimized

  Scenario: Large file download performance
    Given the user has a 500MB recording on the server
    When the user clicks the download button
    Then the download should start immediately
    And a progress indicator should show download status
    And the browser should handle the large file correctly
    And the download should not freeze the UI

  Scenario: Efficient chunk buffering during recording
    Given the user starts a long recording session
    When recording for extended periods (2+ hours)
    Then memory usage should remain stable
    And chunks should be flushed to IndexedDB regularly
    And RAM should not exceed 500MB for the recording process
    And the application should not slow down over time

  Scenario: Concurrent recording and playback
    Given the user is recording audio
    When the user plays back a different recording simultaneously
    Then both operations should work without interference
    And recording quality should not be affected
    And playback quality should not be affected
    And no audio glitches should occur

  Scenario: Multiple tabs with recordings
    Given the user has WaveForge open in 3 tabs
    When each tab loads the playlist
    Then IndexedDB should be accessed safely
    And all tabs should show the same recordings
    And updates in one tab should reflect in others
    And no database conflicts should occur

  Scenario: Service worker performance
    Given the user has 20 recordings queued for upload
    When the service worker starts processing the queue
    Then uploads should process efficiently
    And the UI should remain responsive
    And upload progress should be tracked accurately
    And failed uploads should retry automatically

  Scenario: Garbage collection and cleanup
    Given the user has many old recordings
    When the user deletes 50 recordings
    Then IndexedDB storage should be freed immediately
    And temporary files should be cleaned up
    And the application should not have memory leaks
    And performance should improve after cleanup

  Scenario Outline: Scalability with different recording lengths
    Given the user has an active internet connection
    When the user records audio for <duration> minutes
    And the user stops the recording
    Then the save should complete in less than <max_time> seconds
    And the recording should be playable immediately
    
    Examples:
      | duration | max_time |
      | 5        | 1        |
      | 30       | 2        |
      | 60       | 2        |
      | 120      | 3        |
      | 240      | 3        |
